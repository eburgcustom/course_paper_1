import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_transactions():
    """Фикстура с тестовыми данными транзакций"""
    data = {
        "Дата операции": [
            "26.09.2025 12:00:00",
            "25.09.2025 15:30:00",
            "20.09.2025 10:15:00",
            "15.09.2025 18:45:00",
            "01.09.2025 09:00:00",
            "25.08.2025 14:20:00",
        ],
        "Сумма операции": [1000, 2000, 1500, 3000, 2500, 1800],
        "Описание": [
            "Покупка в Пятерочке",
            "АЗС Лукойл",
            "Супермаркет Перекресток",
            "Кафе Шоколадница",
            "Аптека",
            "Супермаркет Магнит",
        ],
        "Категория": ["Супермаркеты", "Транспорт", "Супермаркеты", "Кафе и рестораны", "Здоровье", "Супермаркеты"],
    }
    return pd.DataFrame(data)


def test_spending_by_category(sample_transactions):
    """Тестирование функции spending_by_category"""
    # Вызываем тестируемую функцию
    result = spending_by_category(sample_transactions, "Супермаркеты")

    # Проверяем, что результат - это DataFrame
    assert isinstance(result, pd.DataFrame)

    # Проверяем, что все возвращенные транзакции относятся к категории 'Супермаркеты'
    assert all(result["Категория"] == "Супермаркеты")

    # Проверяем, что даты отсортированы по убыванию
    dates = pd.to_datetime(result["Дата операции"])
    assert dates.is_monotonic_decreasing, "Даты не отсортированы по убыванию"

    # Проверяем, что возвращены только нужные колонки
    expected_columns = ["Дата операции", "Сумма операции", "Описание", "Категория"]
    assert all(col in result.columns for col in expected_columns)

    # Проверяем, что возвращены все транзакции по категории
    expected_count = sum(sample_transactions["Категория"] == "Супермаркеты")
    assert len(result) == expected_count


def test_spending_by_category_empty_result(sample_transactions):
    """Тестирование функции spending_by_category с несуществующей категорией"""
    result = spending_by_category(sample_transactions, "Несуществующая категория")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
    assert all(col in result.columns for col in ["Дата операции", "Сумма операции", "Описание", "Категория"])
