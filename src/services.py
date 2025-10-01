import json
import logging
from typing import Any, Dict, List

import pandas as pd

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def analyze_cashback_categories(transactions: List[Dict[str, Any]], year: int, month: int) -> str:
    """
    Анализирует, сколько кэшбэка можно было бы получить по каждой категории
    в заданном месяце и году.

    Args:
        transactions: Список словарей с транзакциями.
        year: Год для анализа.
        month: Месяц для анализа.

    Returns:
        JSON-строка с анализом кэшбэка по категориям.
        Пример: {"Категория 1": 100.50, "Категория 2": 200.00}
    """
    logging.info(f"Запуск анализа кэшбэка за {year}-{month:02d}.")

    if not transactions:
        logging.info("Входной список транзакций пуст. Возвращаем пустой результат.")
        return json.dumps({})

    logging.info(f"Получено {len(transactions)} транзакций для анализа.")

    # Преобразуем список словарей в DataFrame
    df = pd.DataFrame(transactions)

    # Проверяем, есть ли столбец "Кэшбэк"
    if "Кэшбэк" not in df.columns:
        logging.warning("В транзакциях отсутствует столбец 'Кэшбэк'. Возвращаем пустой результат.")
        return json.dumps({})

    # Фильтруем транзакции, где есть кэшбэк, и он не равен нулю
    df = df[df["Кэшбэк"].notna() & (df["Кэшбэк"] > 0)].copy()

    # Преобразуем строковые даты в объекты datetime
    # df["Дата операции"] = df["Дата операции"].apply(lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M:%S"))

    # Преобразуем столбец с датами в datetime, если он еще не в этом формате
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

    # Фильтруем транзакции по заданному году и месяцу
    mask = (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
    monthly_transactions = df.loc[mask]

    # Группируем по категории и суммируем кэшбэк
    cashback_by_category = monthly_transactions.groupby("Категория")["Кэшбэк"].sum().round(2)

    # Преобразуем результат в словарь
    result_dict = cashback_by_category.to_dict()
    logging.info(f"Анализ завершен. Найдено {len(result_dict)} категорий с кэшбэком.")

    # Возвращаем как JSON-строку
    return json.dumps(result_dict, ensure_ascii=False, indent=4)
