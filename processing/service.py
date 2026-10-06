"""Сборка сводки по городу из данных клиентов."""

from clients.rates import get_rate
from clients.weather import get_weather
from processing.preprocessing import (
    is_expensive,
    needs_warm_clothes,
    normalize_description,
)


def build_city_summary(city: str, currency: str = "USD") -> dict:
    """Собирает сводку по городу.

    Возвращает dict с погодой, курсом и вычисленными флагами.
    """
    weather = get_weather(city)
    rate = get_rate(currency)

    return {
        "city": weather["city"],
        "weather": {
            "temp_c": weather["temp_c"],
            "description": normalize_description(weather["description"]),
            "warm_clothes": needs_warm_clothes(weather["temp_c"]),
        },
        "rates": {
            "currency": currency.upper(),
            "rate_to_rub": rate,
            "expensive": is_expensive(rate),
        },
    }
