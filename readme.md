# Юморной бот на любые темы!!!

Я —  бот-комик, специализирующийся на запросах для получения смешного.
Независимо от того, что вы спрашиваете,
я сделаю для вас интересный ответ, не теряя в информативности или придумывая 
какие-либо сюжеты

Ссылка на бота: https://t.me/Visits_Card_Bot

## ВАЖНО!!!

**Необходимо получить API GPTYandex, авторизоваться, 
подключиться к виртуальной машине для корректной работы бота. 
Необходимо создать config.py, пример которого лежит в директории проекта.
Бот не распознает какие-либо сообщения помимо текстовых или голосовых**

## Использование

- Запустите бота, отправив команду `/start`.
- Чтобы узнать сведения о разработчике и о боте, напишите команду `/help`.
- Чтобы перейти в тестовый режим распознавания и синтеза,
воспользуйтесь командой `/tts_stt`.
  
Следуйте инструкциям бота и делайте выбор с помощью предоставленных кнопок.

## Файлы и Директории

`bot.py`: Основной скрипт с логикой бота.   
`gpt.py`: Файл с передачей запроса в YandexGPT  
`database.py`: Файл с инициализацией базы данных и всеми обработками запросов.  
`config.py`: Пример использования параметров для нормальной работы бота.  
`logs.txt`: Лог-файл с документированными ошибками.
`speechkit.py`: Файл с передачей запроса в SpeechKit
`validators.py`: Файл со всей валидацией, соединяющий все файлы
`requirements.txt`: Файл с виртуальными окружениями и управлением зависимостями
`creds.py`: Файл с получением личных данных из файлов для конфига
