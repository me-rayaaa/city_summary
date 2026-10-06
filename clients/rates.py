"""Клиент курсов валют Frankfurter."""

import requests

from clients.http import get_json
from exceptions import CurrencyNotFoundError, InvalidResponseError

RATE_URL_TEMPLATE = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"


def get_rate(currency: str) -> float:
    """Возвращает курс currency → RUB.

    Кидает CurrencyNotFoundError, если Frankfurter вернул 422/404
    (неизвестный ISO-код).
    """
    url = RATE_URL_TEMPLATE.format(currency=currency.upper())

    try:
        data = get_json(url)
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status in (404, 422):
            raise CurrencyNotFoundError(
                f"Currency not found: {currency}"
            ) from exc
        raise

    try:
        rate = float(data["rate"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidResponseError(
            f"Rate response missing 'rate' for currency={currency}"
        ) from exc

    return rate

