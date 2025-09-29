from unittest.mock import MagicMock, mock_open

import pandas as pd
import pytest
import requests

from src.utils import (get_currency_rates, get_greeting, get_stock_prices, get_user_settings,
                       read_transactions_from_excel)


@pytest.fixture
def mock_requests_get(mocker: MagicMock) -> MagicMock:
    """Фикстура для мокирования requests.get."""
    return mocker.patch("requests.get")


def test_read_transactions_from_excel_success(mocker: MagicMock) -> None:
    """Тест успешного чтения Excel-файла."""
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mocker.patch("pandas.read_excel", return_value=mock_df)
    df = read_transactions_from_excel("dummy_path.xlsx")
    pd.testing.assert_frame_equal(df, mock_df)


def test_read_transactions_from_excel_file_not_found(mocker: MagicMock) -> None:
    """Тест обработки отсутствующего Excel-файла."""
    mocker.patch("pandas.read_excel", side_effect=FileNotFoundError)
    df = read_transactions_from_excel("non_existent_path.xlsx")
    assert df.empty


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (8, "Доброе утро"),
        (14, "Добрый день"),
        (19, "Добрый вечер"),
        (2, "Доброй ночи"),
    ],
)
def test_get_greeting(mocker: MagicMock, hour: int, expected_greeting: str) -> None:
    """Тест приветствий в зависимости от времени суток."""
    mock_now = MagicMock()
    mock_now.hour = hour
    mocker.patch("src.utils.datetime").now.return_value = mock_now
    assert get_greeting() == expected_greeting


def test_get_user_settings_success(mocker: MagicMock) -> None:
    """Тест успешной загрузки настроек пользователя."""
    settings_data = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}'
    mocker.patch("builtins.open", mock_open(read_data=settings_data))
    settings = get_user_settings("dummy_path.json")
    assert settings == {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}


def test_get_user_settings_file_not_found(mocker: MagicMock) -> None:
    """Тест обработки отсутствующего файла настроек."""
    mocker.patch("builtins.open", side_effect=FileNotFoundError)
    settings = get_user_settings("non_existent.json")
    assert settings == {"user_currencies": [], "user_stocks": []}


def test_get_currency_rates_success(mock_requests_get: MagicMock) -> None:
    """Тест успешного получения курсов валют."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Valute": {
            "USD": {"Value": 75.0},
            "EUR": {"Value": 90.0},
        }
    }
    mock_requests_get.return_value = mock_response
    rates = get_currency_rates(["USD"])
    assert rates == [{"currency": "USD", "rate": 75.0}]


def test_get_currency_rates_api_error(mock_requests_get: MagicMock) -> None:
    """Тест обработки ошибки API при получении курсов валют."""
    mock_requests_get.side_effect = requests.RequestException
    rates = get_currency_rates(["USD"])
    assert rates == []


def test_get_stock_prices_success(mocker: MagicMock, mock_requests_get: MagicMock) -> None:
    """Тест успешного получения цен на акции."""
    mocker.patch("src.utils.os.getenv", return_value="test_api_key")
    mock_response = MagicMock()
    mock_response.json.return_value = {"Global Quote": {"05. price": "150.0"}}
    mock_requests_get.return_value = mock_response
    prices = get_stock_prices(["AAPL"])
    assert prices == [{"stock": "AAPL", "price": 150.0}]


def test_get_stock_prices_no_api_key(mocker: MagicMock) -> None:
    """Тест получения цен на акции без API-ключа."""
    mocker.patch("src.utils.os.getenv", return_value=None)
    prices = get_stock_prices(["AAPL"])
    assert prices == []
