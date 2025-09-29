import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Анализирует траты по указанной категории за последние 3 месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Название категории для анализа
        date: Дата, начиная с которой анализируются транзакции (формат 'YYYY-MM-DD').
              Если не указана, используется текущая дата.

    Returns:
        Словарь с результатами анализа:
        {
            'category': str,           # Название категории
            'total_amount': float,     # Общая сумма по категории
            'transaction_count': int,  # Количество транзакций
            'transactions': List[Dict] # Список транзакций
        }
    """
    try:
        # Определяем конечную дату периода
        end_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
        start_date = end_date - timedelta(days=90)  # 3 месяца назад

        # Копируем DataFrame, чтобы не изменять исходный
        df = transactions.copy()

        # Преобразуем дату операции в datetime, если это еще не сделано
        if not pd.api.types.is_datetime64_any_dtype(df["Дата операции"]):
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

        # Фильтруем по категории и дате
        mask = (
            (df["Категория"] == category)
            & (df["Дата операции"].dt.date >= start_date)
            & (df["Дата операции"].dt.date <= end_date)
        )

        # Применяем фильтры и выбираем нужные колонки
        result_df = df.loc[mask, ["Дата операции", "Сумма операции", "Описание", "Категория"]].copy()

        # Сортируем по дате (от новых к старым)
        result_df = result_df.sort_values("Дата операции", ascending=False)

        # Сбрасываем индекс для красоты
        result_df = result_df.reset_index(drop=True)

        logging.info(
            f"Найдено {len(result_df)} транзакций по категории '{category}' "
            f"на общую сумму {result_df['Сумма операции'].sum():.2f} руб."
        )

        return result_df

    except Exception as e:
        logging.error(f"Ошибка при анализе трат по категории {category}: {e}")
        # Возвращаем пустой DataFrame с нужными колонками в случае ошибки
        return pd.DataFrame(columns=["Дата операции", "Сумма операции", "Описание", "Категория"])
