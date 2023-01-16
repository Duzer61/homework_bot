class StatusCodeNotOk(Exception):
    """Ответ от API не содержит код 200."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'Должен быть код 200. Сервер вернул статус код: {self.value}'
