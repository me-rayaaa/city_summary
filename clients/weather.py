"""Клиент погоды Open-Meteo: геокодинг + текущая погода."""

from clients.http import get_json
from exceptions import CityNotFoundError, InvalidResponseError

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes → человекочитаемое описание
WMO_CODES: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "freezing rain",
    67: "heavy freezing rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}


def get_weather(city: str) -> dict:
    """Возвращает погоду по городу: {"temp_c": float, "description": str}."""
    lat, lon, display_name = _geocode(city)
    return _fetch_current(lat, lon, display_name)


def _geocode(city: str) -> tuple[float, float, str]:
    """Геокодинг: получает координаты и каноническое имя города."""
    data = get_json(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
    )

    results = data.get("results")
    if not results:
        raise CityNotFoundError(f"City not found: {city}")

    first = results[0]
    try:
        latitude = float(first["latitude"])
        longitude = float(first["longitude"])
        name = str(first["name"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidResponseError(
            f"Geocoding response missing required fields for city={city}"
        ) from exc

    return latitude, longitude, name


def _fetch_current(latitude: float, longitude: float, city_name: str) -> dict:
    """Текущая погода по координатам."""
    data = get_json(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
            "timezone": "auto",
        },
    )

    current = data.get("current")
    if not isinstance(current, dict):
        raise InvalidResponseError("Forecast response missing 'current' block")

    try:
        temp_c = float(current["temperature_2m"])
        weather_code = int(current["weather_code"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidResponseError(
            "Forecast response missing temperature_2m or weather_code"
        ) from exc

    description = WMO_CODES.get(weather_code, "unknown")

    return {
        "city": city_name,
        "temp_c": temp_c,
        "description": description,
    }
