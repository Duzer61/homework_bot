class NoTokenException(Exception):
    """Отсутствует необходимый токен."""

    pass


class NotCorrectResponse(Exception):
    """Ответ от API не соответствует ожидаемому."""

    pass
