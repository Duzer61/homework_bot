class NoTokenException(Exception):
    """Отсутствует необходимый токен."""

    pass


class NotCorrectResponse(Exception):
    """Ответ от API не соответствует ожидаемому."""

    pass


class StatusCodeNotOk(Exception):
    """Ответ от API не содержит код 200."""

    pass


class NotCorrectKey(Exception):
    """В ответе от API нет ключа homeworks."""

    pass
