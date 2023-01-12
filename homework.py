import logging
import os
import requests
import time
import telegram
# from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from dotenv import load_dotenv
from exceptions import NoTokenException

load_dotenv()
# secret_token = os.getenv('TOKEN')

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    filename='main.log',
    filemode='a')


def check_tokens():
    """Проверяет доступность переменных окружения"""
    tokens = {
        'PRACTICUM_TOKEN - токен Практикум.Домашка': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN - токен бота Telegram': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID - id аккаунта Telegram': TELEGRAM_CHAT_ID
    }
    for token_description, token in tokens:
        if token is None:
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message
    )


def get_api_answer(timestamp):
    """Запрашивает эндпоинт API-сервиса Яндекс.Домашка."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS,
                                params=payload)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        return False
    return response.json()


def check_response(response):
    """
    Проверяет ответ API на соответствие документации.
    Извлекает данные о проверках домашних работ.
    """
    # НАПИСАТЬ ПРОВЕРКУ!!!!
    homeworks = response.get('homeworks')
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы из ответа API."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise NoTokenException('Нет одного из необходимых токенов.\
                                Выполнение программы остановлено')

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                if homeworks[0]:
                    message = parse_status(homeworks[0])
                    send_message(message)


                else:
                    pass



        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
