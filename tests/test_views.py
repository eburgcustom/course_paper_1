import json
from unittest.mock import MagicMock

import pandas as pd
import pytest

from src.views import main_page_view


@pytest.fixture
def sample_transactions_df() -> pd.DataFrame:
    """Фикстура с примером DataFrame транзакций."""
    data = {
        "Дата операции": ["01.07.2024 10:00:00", "15.07.2024 15:30:00", "20.07.2024 20:00:00"],
        "Сумма операции": [-1000, -5000, -300],
        "Номер карты": ["*1234", "*1234", "*5678"],
        "Категория": ["Еда", "Развлечения", "Транспорт"],
        "Кэшбэк": [10, 50, 3],
        "Описание": ["Обед", "Кино", "Метро"],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    return df


def test_main_page_view_success(mocker: MagicMock, sample_transactions_df: pd.DataFrame) -> None:
    """Тест успешного формирования JSON для главной страницы."""
    # Мокируем все вспомогательные функции, которые вызываются внутри main_page_view
    mocker.patch("src.views.get_greeting", return_value="Добрый день")
    mocker.patch("src.views.get_user_settings", return_value={"user_stocks": ["AAPL"], "user_currencies": ["USD"]})
    mocker.patch("src.views.get_stock_prices", return_value=[{"stock": "AAPL", "price": 180.5}])
    mocker.patch("src.views.get_currency_rates", return_value=[{"currency": "USD", "rate": 90.0}])
    mocker.patch("src.utils.get_top_expenses", return_value=[{"category": "Развлечения", "amount": 5000.0}])
    mocker.patch("src.utils.get_transactions_for_period", return_value=sample_transactions_df)

    # Дата для фильтрации транзакций
    date_str = "2024-07-31 23:59:59"

    # Вызываем тестируемую функцию с DataFrame и датой
    result = main_page_view(sample_transactions_df, date_str)

    # Проверяем, что результат является корректным JSON-объектом
    assert isinstance(result, str)
    parsed_result = json.loads(result)

    # Проверяем наличие ключей в результате
    assert "greeting" in parsed_result
    assert "cards" in parsed_result
    assert "top_transactions" in parsed_result
    assert "currency_rates" in parsed_result
    assert "stock_prices" in parsed_result

    # Проверяем значения некоторых ключей
    assert parsed_result["greeting"] == "Добрый день"
    assert parsed_result["stock_prices"] == [{"stock": "AAPL", "price": 180.5}]
    assert parsed_result["currency_rates"] == [{"currency": "USD", "rate": 90.0}]

    # Проверяем, что списки не пустые
    assert len(parsed_result["cards"]) > 0
    assert len(parsed_result["top_transactions"]) > 0
