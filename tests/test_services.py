import json

import pytest

from src.services import analyze_cashback_categories


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными о транзакциях."""
    return [
        # Транзакции за октябрь 2021 (целевой месяц)
        {"Дата операции": "15.10.2021 08:12:45", "Категория": "Супермаркеты", "Кэшбэк": 10.50},
        {"Дата операции": "20.10.2021 18:30:00", "Категория": "Супермаркеты", "Кэшбэк": 5.25},
        {"Дата операции": "25.10.2021 12:00:10", "Категория": "Такси", "Кэшбэк": 20.00},
        # Транзакция без кэшбэка
        {"Дата операции": "12.10.2021 10:00:00", "Категория": "Рестораны", "Кэшбэк": None},
        # Транзакция с нулевым кэшбэком
        {"Дата операции": "13.10.2021 11:00:00", "Категория": "Аптеки", "Кэшбэк": 0},
        # Транзакции за другие месяцы/годы
        {"Дата операции": "05.11.2021 14:20:30", "Категория": "Супермаркеты", "Кэшбэк": 8.00},
        {"Дата операции": "10.10.2020 09:00:00", "Категория": "Такси", "Кэшбэк": 15.00},
        # Еще одна транзакция для проверки округления
        {"Дата операции": "28.10.2021 19:45:00", "Категория": "Такси", "Кэшбэк": 11.111},
    ]


def test_analyze_cashback_categories_empty_input():
    """
    Проверяет, что функция корректно обрабатывает пустой список транзакций.
    """
    result_json = analyze_cashback_categories([], year=2021, month=10)
    result_data = json.loads(result_json)

    assert result_data == {}


def test_analyze_cashback_categories_with_data(sample_transactions):
    """
    Проверяет корректность анализа категорий кэшбэка для месяца с данными.
    """
    # Анализируем октябрь 2021
    result_json = analyze_cashback_categories(sample_transactions, year=2021, month=10)
    result_data = json.loads(result_json)

    # Ожидаемый результат:
    # Супермаркеты: 10.50 + 5.25 = 15.75
    # Такси: 20.00 + 11.11 (округлено) = 31.11
    expected_data = {"Супермаркеты": 15.75, "Такси": 31.11}

    assert result_data == expected_data


def test_analyze_cashback_categories_no_data(sample_transactions):
    """
    Проверяет, что функция возвращает пустой объект, если за период нет транзакций.
    """
    # Анализируем январь 2022, для которого нет данных
    result_json = analyze_cashback_categories(sample_transactions, year=2022, month=1)
    result_data = json.loads(result_json)

    # Ожидаемый результат - пустой словарь
    expected_data = {}

    assert result_data == expected_data
