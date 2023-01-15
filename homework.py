import logging
import os
import requests
import sys
import time
import telegram
from dotenv import load_dotenv
from exceptions import NoTokenException, StatusCodeNotOk
from http import HTTPStatus

load_dotenv()


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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = {
        '<PRACTICUM_TOKEN> (токен Практикум.Домашка)': PRACTICUM_TOKEN,
        '<TELEGRAM_TOKEN> (токен бота Telegram)': TELEGRAM_TOKEN,
        '<TELEGRAM_CHAT_ID> (id аккаунта Telegram)': TELEGRAM_CHAT_ID,
    }
    for token_description, token in tokens.items():
        if token is None:
            logger.critical(f'Отсутствует токен {token_description} '
                            f'в файле .env')
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
    except telegram.error.TelegramError as error:
        logger.error(f'сбой при отправке сообщения: {message} - {error}')
    else:
        logger.debug(f'В Телеграм отправлено сообщение: {message}')
    finally:
        return


def get_api_answer(timestamp):
    """Запрашивает эндпоинт API-сервиса Яндекс.Домашка."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS,
                                params=payload)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            raise StatusCodeNotOk(response.status_code)
    except requests.RequestException as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')


def check_response(response):
    """
    Проверяет ответ API на соответствие документации.
    Извлекает данные о проверках домашних работ.
    """
    logger.debug('Проверяем response')
    if not isinstance(response, dict):
        raise TypeError(f'Структура данных API не соответствует ожиданию. '
                        f'Получен {type(response)} вместо <dict>')
    elif 'homeworks' not in response:
        raise KeyError('В ответе API нет ключа <homeworks>.')
    elif not isinstance(response['homeworks'], list):
        raise TypeError(f'Структура данных API не соответствует ожиданию. '
                        f'Получен {type(response["homeworks"])} вместо <list>')
    homeworks = response.get('homeworks')
    if homeworks != []:
        return homeworks
    return False


def parse_status(homework):
    """Извлекает статус домашней работы из ответа API."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе отсутствует имя домашней работы. '
                       '"homework_name"')
    homework_name = homework['homework_name']
    if 'status' not in homework:
        raise KeyError('В ответе отсутствует ключ статуса работы')
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('Неизвестный статус работы')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise NoTokenException(
            'Отсутствует один из необходимых токенов. '
            'Выполнение программы остановлено.'
        )
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_messages = []

    while True:
        logger.info('Запрашиваем статус домашки')
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                if message not in old_messages:
                    old_messages.append(message)
                    send_message(bot, message)
            else:
                message = 'Статус работы пока не менялся.'
                if message not in old_messages:
                    old_messages.append(message)
                    send_message(bot, message)
        except Exception as error:
            logger.error(f'Сбой в работе программы: {error}.')
            message = (f'Сбой в работе программы: {error}. Выполнение '
                       f'программы продолжено, но возможно нужно вмешаться.')
            if message not in old_messages:
                old_messages.append(message)
                send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
