class CitySummaryError(Exception):
    """Базовое исключение приложения."""


class CityNotFoundError(CitySummaryError):
    """Город не найден в геокодере."""


class CurrencyNotFoundError(CitySummaryError):
    """Код валюты не найден в сервисе курсов."""


class ExternalServiceError(CitySummaryError):
    """Внешний сервис недоступен после retry."""


class InvalidResponseError(CitySummaryError):
    """Ответ внешнего API не соответствует ожидаемому формату."""

