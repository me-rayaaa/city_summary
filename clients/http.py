"""Общий HTTP-клиент: GET с timeout и retry."""

import logging
import random
import time

import requests

from exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
TIMEOUT = (3, 7)
RETRYABLE_STATUSES = {500, 502, 503, 504}


def get_json(
    url: str,
    params: dict | None = None,
    *,
    timeout: tuple[int, int] = TIMEOUT,
    max_attempts: int = MAX_ATTEMPTS,
) -> dict:
    """GET-запрос с retry. Возвращает распарсенный JSON.

    Retry выполняется при Timeout, ConnectionError, 5xx и 429.
    При 429 учитывается заголовок Retry-After.
    4xx (кроме 429) пробрасываются наружу — вызывающий код решает сам.
    """
    last_exc: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info("GET %s attempt=%s/%s", url, attempt, max_attempts)
            response = requests.get(url, params=params, timeout=timeout)

            # 429 — ждём Retry-After и повторяем
            if response.status_code == 429:
                if attempt == max_attempts:
                    raise ExternalServiceError(
                        f"Rate limited on {url} after {max_attempts} attempts"
                    )
                delay = _retry_after_seconds(response)
                logger.warning("429 on %s, sleeping %.1fs", url, delay)
                time.sleep(delay)
                continue

            # 5xx — ретраим (своими руками, без raise_for_status)
            if response.status_code in RETRYABLE_STATUSES:
                last_exc = requests.exceptions.HTTPError(
                    f"HTTP {response.status_code} from {url}",
                    response=response,
                )
                if attempt == max_attempts:
                    break
                delay = _backoff_delay(attempt)
                logger.warning(
                    "HTTP %s on %s (attempt %s/%s); sleeping %.1fs",
                    response.status_code,
                    url,
                    attempt,
                    max_attempts,
                    delay,
                )
                time.sleep(delay)
                continue

            # 4xx (кроме 429) — не ретраим, сразу HTTPError наружу
            if 400 <= response.status_code < 500:
                response.raise_for_status()

            # 2xx — успех
            response.raise_for_status()
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as exc:
                raise ExternalServiceError(
                    f"Invalid JSON from {url}"
                ) from exc

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            last_exc = exc
            if attempt == max_attempts:
                break
            delay = _backoff_delay(attempt)
            logger.warning(
                "Network error on %s (attempt %s/%s): %s; sleeping %.1fs",
                url,
                attempt,
                max_attempts,
                exc,
                delay,
            )
            time.sleep(delay)

    raise ExternalServiceError(
        f"Service unavailable after {max_attempts} attempts: {url}"
    ) from last_exc


def _backoff_delay(attempt: int) -> float:
    """Экспоненциальная задержка: 1s, 2s, 4s + jitter."""
    return 2 ** (attempt - 1) + random.uniform(0, 0.5)


def _retry_after_seconds(response: requests.Response) -> float:
    """Читает Retry-After. Если его нет или он не число — использует 1s."""
    value = response.headers.get("Retry-After")
    if value is None:
        return 1.0
    try:
        return float(value)
    except ValueError:
        return 1.0

