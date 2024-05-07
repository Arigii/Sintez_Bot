import telebot
from telebot import types
from validators import *  # модуль для валидации
from gpt import ask_gpt  # модуль для работы с GPT

# подтягиваем константы из config файла
from config import LOGS, COUNT_LAST_MSG

# подтягиваем функции из database файла
from database import create_database, add_message, select_n_last_messages
from speechkit import speech_to_text, text_to_speech
from creds import get_bot_token  # модуль для получения bot_token

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = telebot.TeleBot(get_bot_token())  # создаём объект бота


# функция для создания клавиатуры
def create_keyboard(buttons_list):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


# обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Привет, {user_name}! Я юморной бот, который ответит тебе на что угодно! "
                     "Отправь мне текст или голосовое сообщение и я отвечу тебе тем же! Для подробной информации, как я"
                     " работаю, используй команду /help",
                     reply_markup=create_keyboard(["/help"]))


# обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help_hand(message):
    bot.send_message(message.from_user.id,
                     text="Привет! Я тестовая виртуальная машина для генерации веселых ответов на любые темы "
                          "и запоминающая их. Я могу синтезировать и распознавать речь, отвечая тебе на голосовые "
                          "или просто отвечать на текст. У любого пользователя предоставлены определенные лимиты для "
                          "сообщений в рамках тестового режима. Используй команду /tts_stt для того, чтобы проверить "
                          "распознавание и синтез голосовых сообщений. Для обычной генерации просто отправляй сообщения"
                          " в чат.\n"
                          "Вот моя ссылка в телеграм для сообщения ошибок - https://t.me/Remminders \n"
                          "Вот репозиторий этого бота -- \n"
                          "Создан с помощью инструментария GPTYandex и Speechkit",
                     reply_markup=create_keyboard(["/tts_stt"]))


# обрабатываем команду /tts_stt
@bot.message_handler(commands=['tts_stt'])
def tts_stt_test(message):
    bot.send_message(message.chat.id, "Вход в тестовый режим синтеза и распознавания речи. "
                                      "Отправьте текст или голосовое. Для выхода воспользуйтесь словом 'exit'.",
                     reply_markup=create_keyboard(["exit"]))
    logging.info(f"Пользователь {message.from_user.id} вошел в тестовый режим синтеза и распознавания речи")
    bot.register_next_step_handler(message, treatment_message)


# логика хэндлера tts_stt_test
def treatment_message(message):
    user_id = int(message.from_user.id)
    try:
        if message.text == 'exit':
            bot.reply_to(message, "Выход из тестового режима синтеза и распознавания.",
                         reply_markup=types.ReplyKeyboardRemove())
            logging.info(f"Пользователь {user_id} вышел из тестового режима")
            return
        elif message.content_type == 'voice':
            # Обработка голосового сообщения
            file_id = message.voice.file_id
            file_info = bot.get_file(file_id)
            file = bot.download_file(file_info.file_path)
            status_stt, stt_text = speech_to_text(file)
            if not status_stt:
                bot.reply_to(message, stt_text)
            else:
                bot.reply_to(message, stt_text)
        elif message.content_type == 'text':
            status_tts, voice_response = text_to_speech(message.text)
            if status_tts:
                bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
            else:
                bot.reply_to(message, voice_response)
        else:
            bot.reply_to(message, "Отправьте голосовое или текстовое сообщение.")
        bot.register_next_step_handler(message, treatment_message)
    except ValueError as e:
        bot.reply_to(message, "Ошибка тестового режима. Попробуйте позже")
        logging.error(e)


# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    user_id = int(message.from_user.id)
    try:
        bot.send_message(user_id, "Распознаю и генерирую речь, подождите  👋≧◉ᴥ◉≦",
                         reply_markup=types.ReplyKeyboardRemove())
        # Проверка на максимальное количество пользователей
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        # Проверка на доступность аудиоблоков
        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        logging.info(f"Успешная проверка на доступность аудиоблоков у пользователя {user_id}")

        # Обработка голосового сообщения
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)
        status_stt, stt_text = speech_to_text(file)
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return
        logging.info(f"Успешная проверка голосового сообщения у пользователя {user_id}")

        # Запись в БД
        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        # Проверка на доступность GPT-токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return
        logging.info(f"Успешная проверка доступности токенов у пользователя {user_id}")

        # Запрос к GPT и обработка ответа
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        logging.info(f"Успешная обработка ответа у пользователя {user_id}")

        # Проверка на лимит символов для SpeechKit
        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)

        # Запись ответа GPT в БД
        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return

        logging.info(f"Успешная проверка лимитов у пользователя {user_id}")

        # Преобразование ответа в аудио и отправка
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            logging.info(f"Успешная отправка голосового сообщения пользователю {user_id}")
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            logging.info(f"Отказ пользователю {user_id} в отправке голосового")
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)
    except Exception as e:
        logging.error(e)
        bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")


# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    try:
        bot.send_message(user_id, "Генерирую ответ, подождите  ✍(◔◡◔)",
                         reply_markup=types.ReplyKeyboardRemove())
        # проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)  # мест нет =(
            return

        # добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        # считаем количество доступных пользователю GPT-токенов
        # и получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        logging.info(f"Успешная проверка токенов у пользователя {user_id}")

        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, error_message)
            return
        logging.info(f"Успешная проверка лимитов у пользователя {user_id}")

        # отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)

        # обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)
        bot.reply_to(message, answer_gpt)  # отвечаем пользователю текстом
        logging.info(f"Успешная отправка ответа gpt пользователю {user_id}")
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_database()
    bot.polling()  # запускаем бота
