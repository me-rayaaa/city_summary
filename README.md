# City Summary

CLI-утилита «Сводка по городу»: получает погоду и курс валюты к рублю
из внешних API, применяет правила предобработки и печатает результат.

## Требования

- Python 3.10+
- requests

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск

```bash
python main.py --city Moscow
python main.py --city Moscow --currency EUR
```

Пример вывода:

```
Город: Moscow
Погода: 12.2°C, overcast
Тёплая одежда: нет
USD→RUB: 84.89
Дорогой курс: нет
```

## Коды выхода

- `0` — успех
- `2` — ошибка аргументов
- `3` — город или код валюты не найден
- `4` — внешний сервис недоступен после retry

## Внешние API

- Погода: [Open-Meteo](https://open-meteo.com/)
- Курсы: [Frankfurter](https://frankfurter.dev/)

