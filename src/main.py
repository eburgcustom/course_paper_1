import json
import logging
from datetime import datetime

import pandas as pd

from src.reports import spending_by_category
from src.services import analyze_cashback_categories
from src.utils import read_transactions_from_excel
from src.views import main_page_view

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def show_spending_report(transactions_df: pd.DataFrame) -> None:
    """Показывает отчет по расходам по категориям"""
    print("\n--- Отчет по расходам по категориям ---")

    # Получаем список уникальных категорий
    categories = [str(cat) for cat in transactions_df["Категория"].dropna().unique()]
    print("\nДоступные категории:")
    for i, category in enumerate(sorted(categories), 1):
        print(f"{i}. {category}")

    while True:
        try:
            choice = input("\nВведите номер категории (или 0 для выхода): ")
            if choice == "0":
                return

            category_idx = int(choice) - 1
            if 0 <= category_idx < len(categories):
                category = sorted(categories)[category_idx]
                break
            print("Ошибка: введите корректный номер категории")
        except ValueError:
            print("Ошибка: введите число")

    # Получаем отчет по выбранной категории
    report = spending_by_category(transactions_df, category)

    if report.empty:
        print(f"Нет данных о расходах в категории '{category}' за последние 3 месяца.")
    else:
        # Выводим общую информацию
        total = report["Сумма операции"].sum()
        print(f"\n=== Отчет по категории: {category} ===")
        print(f"Период: последние 3 месяца (до {datetime.now().strftime('%d.%m.%Y')})")
        print(f"Всего транзакций: {len(report)}")
        print(f"Общая сумма: {total:.2f} руб.")

        # Выводим таблицу с транзакциями
        print("\nПоследние транзакции:")
        print(report[["Дата операции", "Сумма операции", "Описание"]].to_string(index=False))

        # Предлагаем сохранить отчет в файл
        save = input("\nСохранить отчет в файл? (да/нет): ").lower()
        if save in ["да", "д", "y", "yes"]:
            filename = f"отчет_{category.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
            report.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"Отчет сохранен в файл: {filename}")


def main() -> None:
    """
    Главная функция, которая запускает все реализованные функциональности.
    """
    # Путь к файлу с транзакциями
    transactions_file = "data/operations.xlsx"

    # Чтение транзакций
    transactions_df = read_transactions_from_excel(transactions_file)

    if transactions_df.empty:
        print("Не удалось прочитать данные о транзакциях. Завершение работы.")
        return

    # Получаем текущую дату и время
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Веб-страницы ---
    print("--- Данные для главной страницы ---")
    try:
        main_page_json = main_page_view(transactions_df, current_datetime)
        print(main_page_json)
    except Exception as e:
        print(f"Ошибка при формировании главной страницы: {e}")
    print("-" * 30)

    # --- Пример вызова сервиса анализа кэшбэка ---
    print("\n--- Анализ кэшбэка за текущий месяц ---")
    try:
        # Получаем текущий год и месяц
        now = datetime.now()
        cashback_analysis = analyze_cashback_categories(
            transactions_df.to_dict("records"), year=now.year, month=now.month
        )
        print(json.dumps(json.loads(cashback_analysis), ensure_ascii=False, indent=4))
    except Exception as e:
        print(f"Ошибка при анализе кэшбэка: {e}")
    print("-" * 30)

    # --- Отчет по расходам ---
    show_spending_report(transactions_df)


if __name__ == "__main__":
    main()
