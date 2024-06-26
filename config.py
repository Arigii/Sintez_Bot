HOME_DIR = '/home/student/gpt_bot'  # путь к папке с проектом

LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/messages.db'  # файл для базы данных

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token

MAX_USERS = 4  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 1000  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога
MAX_TTS_SYMBOLS = 5000  # максимальное кол-во символов в ответе speechkit

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 2000  # 5 000 символов
MAX_USER_GPT_TOKENS = 1000  # 2 000 токенов

# список с системным промтом
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник с юмором. Изображай комика, но в меру'
                                            'Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Отвечай строго не больше 3-4 предложений без пояснений'}]
