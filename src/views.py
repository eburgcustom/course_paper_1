import json
from datetime import datetime

import pandas as pd

from src.utils import get_currency_rates, get_greeting, get_stock_prices, get_user_settings


def main_page_view(transactions: pd.DataFrame, date_time: str) -> str:
    """
    Формирует JSON-ответ для главной страницы.

    Args:
        transactions: DataFrame с транзакциями.
        date_time: Строка с датой и временем в формате 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        Строка в формате JSON с данными для главной страницы.
    """

    # Получаем приветствие
    greeting = get_greeting()

    # Получаем настройки пользователя
    user_settings = get_user_settings("user_settings.json")

    # Получаем данные о курсах валют и акциях
    currency_rates = get_currency_rates(user_settings.get("user_currencies", []))
    stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

    # Обрабатываем транзакции
    # Преобразуем дату операции в datetime, если это еще не сделано
    if not pd.api.types.is_datetime64_any_dtype(transactions["Дата операции"]):
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтруем транзакции за текущий месяц
    date_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    start_of_month = date_obj.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = transactions[transactions["Дата операции"] <= date_obj].copy()
    monthly_transactions = monthly_transactions[monthly_transactions["Дата операции"] >= start_of_month]

    # 1. Информация по картам
    cards_info = []
    if not monthly_transactions.empty:
        # Группируем по последним 4 цифрам карты
        for card, group in monthly_transactions.groupby(monthly_transactions["Номер карты"].str[-4:]):
            total_spent = group["Сумма операции"].sum()
            cashback = group["Кэшбэк"].sum()

            cards_info.append(
                {"last_digits": card, "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
            )

    # 2. Топ-5 транзакций по сумме платежа
    top_transactions = []
    if not monthly_transactions.empty:
        top_tx = monthly_transactions.nlargest(5, "Сумма операции")
        for _, tx in top_tx.iterrows():
            top_transactions.append(
                {
                    "date": tx["Дата операции"].strftime("%d.%m.%Y"),
                    "amount": round(tx["Сумма операции"], 2),
                    "category": tx.get("Категория", "Не указана"),
                    "description": tx.get("Описание", ""),
                }
            )

    # Формируем итоговый JSON
    page_data = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(page_data, ensure_ascii=False, indent=4, default=str)
