import logging
import requests
from config import LOGS
from creds import get_creds  # модуль для получения токенов

logging.basicConfig(filename=LOGS, level=logging.INFO,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

IAM_TOKEN, FOLDER_ID = get_creds()  # получаем iam_token и folder_id из файлов


def text_to_speech(text):
    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # мужской голос Филиппа
        'folderId': FOLDER_ID,
    }

    # Выполняем запрос
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content  # возвращаем статус и аудио
    else:
        logging.error("Ошибка при отправке запроса в Speechkit")
        return False, "При запросе в SpeechKit возникла ошибка"


def speech_to_text(data):
    try:
        # Указываем параметры запроса
        params = "&".join([
            "topic=general",  # используем основную версию модели
            f"folderId={FOLDER_ID}",
            "lang=ru-RU"  # распознаём голосовое сообщение на русском языке
        ])

        # Аутентификация через IAM-токен
        headers = {
            'Authorization': f'Bearer {IAM_TOKEN}',
        }

        # Выполняем запрос
        response = requests.post(
            f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
            headers=headers,
            data=data
        )

        # Читаем json в словарь
        decoded_data = response.json()

        # Проверяем, не произошла ли ошибка при запросе
        if decoded_data.get("error_code") is None and decoded_data.get("result") != '':
            return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
        else:
            logging.error("Пользователь отправил некорректное голосовое сообщение")
            return False, ("При запросе в SpeechKit возникла ошибка. Возможно, голосовое пустое или неразборчивое. "
                           "Повторите, пожалуйста")
    except ValueError:
        logging.error("При распознавании произошла ошибка")
        return False, "Произошла ошибка. Скорее всего, голосовое сообщение некорректное. Попробуйте отправить еще раз"
