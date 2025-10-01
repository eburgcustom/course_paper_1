import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def read_transactions_from_excel(file_path: str) -> pd.DataFrame:
    """
    Читает транзакции из Excel-файла в DataFrame pandas.

    Args:
        file_path: Путь к Excel-файлу.

    Returns:
        DataFrame с транзакциями.
    """
    try:
        df = pd.read_excel(file_path)
        logging.info(f"Успешно загружен файл: {file_path}")
        return df
    except FileNotFoundError:
        logging.error(f"Файл не найден: {file_path}")
        return pd.DataFrame()


def get_greeting() -> str:
    """
    Возвращает приветствие в зависимости от текущего времени суток.

    Returns:
        Строка с приветствием.
    """
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 17:
        return "Добрый день"
    elif 17 <= current_hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_user_settings(file_path: str) -> Dict[str, List[str]]:
    """
    Загружает пользовательские настройки из JSON-файла.

    Args:
        file_path: Путь к файлу user_settings.json.

    Returns:
        Словарь с настройками пользователя.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            logging.info(f"Пользовательские настройки загружены из {file_path}")
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error(f"Не удалось загрузить настройки из {file_path}")
        return {"user_currencies": [], "user_stocks": []}


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает курсы валют от ЦБ РФ.

    Args:
        currencies: Список кодов валют для получения.

    Returns:
        Список словарей с курсами валют.
    """
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    result = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for currency in currencies:
            if currency in data["Valute"]:
                result.append({"currency": currency, "rate": data["Valute"][currency]["Value"]})
        logging.info(f"Курсы валют успешно получены для: {currencies}")
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении курсов валют: {e}")
    return result


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает цены на акции с помощью API Alpha Vantage.

    Args:
        stocks: Список тикеров акций.

    Returns:
        Список словарей с ценами на акции.
    """
    load_dotenv()
    api_key = os.getenv("API_KEY_ALPHAVANTAGE")
    if not api_key:
        logging.error("API ключ для Alpha Vantage не найден.")
        return []

    result = []
    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            quote = data.get("Global Quote")
            if quote and "05. price" in quote:
                result.append({"stock": stock, "price": float(quote["05. price"])})
            else:
                logging.warning(f"Не удалось получить цену для акции: {stock}. Ответ API: {data}")
        except requests.RequestException as e:
            logging.error(f"Ошибка при получении цены для акции {stock}: {e}")
        except (ValueError, KeyError) as e:
            logging.error(f"Ошибка обработки данных для акции {stock}: {e}")

    logging.info(f"Цены на акции успешно получены для: {stocks}")
    return result


def get_top_expenses(transactions: pd.DataFrame, top_n: int = 5) -> list[dict]:
    """
    Возвращает топ-N самых больших расходов.

    Args:
        transactions: DataFrame с транзакциями.
        top_n: Количество возвращаемых транзакций.

    Returns:
        Список словарей с категориями и суммами расходов.
    """
    # Фильтруем только расходы (отрицательные суммы)
    expenses = transactions[transactions["Сумма операции"] < 0].copy()
    # Берем абсолютное значение суммы для корректной сортировки
    expenses["Сумма операции"] = expenses["Сумма операции"].abs()
    # Группируем по категории и суммируем, затем сортируем и берем топ-N
    top_expenses = expenses.groupby("Категория")["Сумма операции"].sum().nlargest(top_n).reset_index()
    return top_expenses.to_dict("records")


def get_transactions_for_period(transactions: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Фильтрует транзакции за указанный период (в днях от текущей даты).

    Args:
        transactions: DataFrame со всеми транзакциями.
        days: Количество дней для фильтрации.

    Returns:
        Отфильтрованный DataFrame.
    """
    end_date = pd.to_datetime(datetime.now())
    start_date = end_date - pd.Timedelta(days=days)
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
    return transactions[(transactions["Дата операции"] >= start_date) & (transactions["Дата операции"] <= end_date)]
