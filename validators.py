import logging  # модуль для сбора логов
import math
# подтягиваем функцию для подсчета токенов в списке сообщений
from gpt import count_gpt_tokens
# подтягиваем константы из config файла
from config import LOGS, MAX_USERS, MAX_USER_GPT_TOKENS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, MAX_TTS_SYMBOLS
# подтягиваем функции для работы с БД
from database import count_users, count_all_blocks, count_all_symbol

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


# получаем количество уникальных пользователей, кроме самого пользователя
def check_number_of_users(user_id):
    try:
        count = count_users(user_id)
        if count is None:
            logging.error("Ошибка при подключении к БД")
            return None, "Ошибка при работе с БД"
        if count > MAX_USERS:
            logging.info("Ограничение пользователей.")
            return None, "Превышено максимальное количество пользователей"
        return True, ""
    except ValueError as e:
        logging.error(e)
        return None, "Ошибка в работе с базой данных. Попробуйте позже"


# проверяем, не превысил ли пользователь лимиты на общение с GPT
def is_gpt_token_limit(messages, total_spent_tokens):
    try:
        all_tokens = count_gpt_tokens(messages) + total_spent_tokens
        if all_tokens > MAX_USER_GPT_TOKENS:
            logging.info("У пользователя превышен лимит ответов gpt")
            return None, f"Превышен общий лимит GPT-токенов {MAX_USER_GPT_TOKENS}"
        return all_tokens, ""
    except ValueError as e:
        logging.error(e)
        return None, "Ошибка подсчета лимитов с нейросетью. Попробуйте позже"


def is_stt_block_limit(user_id, duration):
    try:
        # Переводим секунды в аудиоблоки
        audio_blocks = math.ceil(duration / 15)  # округляем в большую сторону
        # Функция из БД для подсчёта всех потраченных пользователем аудиоблоков
        all_blocks = count_all_blocks(user_id)

        # Проверяем, что аудио длится меньше 30 секунд
        if duration >= 30:
            msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
            limit = f"Превышение у пользователя {user_id} предела аудио в 30 секунд"
            logging.info(limit)
            return None, msg
        else:  # Если длительность меньше 30 секунд
            # Сравниваем all_blocks с количеством доступных пользователю аудиоблоков
            if all_blocks >= MAX_USER_STT_BLOCKS:
                msg = (f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. "
                       f"Доступно: {MAX_USER_STT_BLOCKS - all_blocks}")
                limit = f"Пользователь {user_id} не смог войти из-за кол-ва пользователей"
                logging.info(limit)
                return None, msg

            return audio_blocks, False
    except ValueError as e:
        logging.error(e)
        return None, "Ошибка обработки аудио. Попробуйте в следующий раз"


def is_tts_symbol_limit(user_id, text):
    try:
        text_symbols = len(text)

        # Функция из БД для подсчёта всех потраченных пользователем символов
        all_symbols = count_all_symbol(user_id) + text_symbols

        # Сравниваем количество символов в тексте с максимальным количеством символов в тексте
        if text_symbols >= MAX_TTS_SYMBOLS:
            logging.info(f"Количество символов у {user_id} превышает максимальный")
            return None, "Превышено максимальное кол-во символов"

        # Сравниваем all_symbols с количеством доступных пользователю символов
        if all_symbols >= MAX_USER_TTS_SYMBOLS:
            logging.info(f"У пользователя {user_id} превышен лимит на отправку символов")
            return None, "Превышен лимит символов для синтеза"

        return len(text), False
    except ValueError as e:
        logging.error(e)
        return None, "Ошибка подсчета символов. Попробуйте в следующий раз"
