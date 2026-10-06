"""Правила предобработки: превращают «сырые» данные в флаги сводки."""

# Пороги для правил
WARM_CLOTHES_THRESHOLD_C = 0.0
EXPENSIVE_RATE_THRESHOLD = 100.0


def needs_warm_clothes(temp_c: float) -> bool:
    """True, если на улице холоднее порога."""
    return temp_c < WARM_CLOTHES_THRESHOLD_C


def is_expensive(rate_to_rub: float) -> bool:
    """True, если курс выше порога."""
    return rate_to_rub > EXPENSIVE_RATE_THRESHOLD


def normalize_description(description: str | None) -> str:
    """Если описание погоды пустое — подставляем 'unknown'."""
    if not description:
        return "unknown"
    return description

