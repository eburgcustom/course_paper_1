# Анализатор финансовых операций

Проект для анализа банковских транзакций: главная страница с агрегатами и данными из внешних API, сервис анализа выгодных категорий повышенного кешбэка, отчёт «Траты по категории».

## Структура проекта

- `src/`
  - [main.py](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/src/main.py:0:0-0:0) — точка входа, запуск сценариев и отчётов
  - [views.py](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/src/views.py:0:0-0:0) — формирование JSON для страницы «Главная»
  - [reports.py](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/src/reports.py:0:0-0:0) — отчёт «Траты по категории`
  - [services.py](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/src/services.py:0:0-0:0) — сервис «Выгодные категории повышенного кешбэка»
  - [utils.py](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/src/utils.py:0:0-0:0) — утилиты: чтение Excel, запросы к API, фильтры, агрегации
- `tests/` — автотесты для `views`, `services`, `reports`, `utils`
- `data/operations.xlsx` — входные транзакции
- [user_settings.json](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/user_settings.json:0:0-0:0) — пользовательские настройки (валюты и акции)
- [.env.template](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/.env.template:0:0-0:0) — шаблон переменных окружения (API ключи)
- [pyproject.toml](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/pyproject.toml:0:0-0:0) / [poetry.lock](cci:7://file:///C:/Users/UNKNOWN/PycharmProjects/Course_paper_1/poetry.lock:0:0-0:0) — зависимости

## Установка

Вариант A: pip
```bash
poetry install
poetry shell
```
### Зависимости: pandas, requests, python-dotenv, openpyxl, pytest, flake8.

Настройки
Скопируйте 
.env.template
 в 
.env
 и заполните при необходимости.
Для котировок акций нужен API ключ Alpha Vantage:
переменная окружения: API_KEY_ALPHAVANTAGE
user_settings.json:
```{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

## Запуск
```bash
python -m src.main
```
## Сценарий:

* Формирует JSON для главной страницы (
views.main_page_view
)
* Запускает сервис анализа кэшбэка за текущий месяц (
services.analyze_cashback_categories
)
* Показывает интерактивный отчёт «Траты по категории» с возможностью экспорта в CSV
### Основные функции
* views.main_page_view(transactions: pd.DataFrame, date_time: str) -> str
  * Вход: дата-время YYYY-MM-DD HH:MM:SS
  * Фильтр: с начала месяца до указанной даты
  * Выход (JSON): 
greeting
, cards, top_transactions, 
currency_rates
, 
stock_prices
* services.analyze_cashback_categories(transactions: List[dict], year: int, month: int) -> str
  * Вход: список транзакций, год, месяц
  * Выход: JSON с суммой кэшбэка по категориям за месяц
  * Устойчив к типам даты (строка/Timestamp)
* reports.spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str]) -> pd.DataFrame
  * Возвращает DataFrame с транзакциями по категории за последние 3 месяца от заданной (или текущей) даты
  * Отсортировано по дате по убыванию
  * Колонки: Дата операции, Сумма операции, Описание, Категория

### Тесты:

 * tests/test_views.py
 — структура JSON главной страницы, моки API
 * tests/test_services.py — сервис кешбэка
 * tests/test_reports.py
 — отчёт по категории
* tests/test_utils.py
 — утилиты, чтение Excel, запросы к API
### Логирование
Логи настроены в 
main.py
, 
utils.py
, 
services.py
, 
reports.py
. Формат: %(asctime)s - %(levelname)s - %(message)s.