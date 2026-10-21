import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
BASE_URL = "https://api.todoist.com"
URL_LOGIN_PAGE = "https://app.todoist.com/auth/login"
URL_INBOX_PAGE="https://app.todoist.com/app/inbox"

load_dotenv(dotenv_path=ENV_PATH)

# =====================================================================
# 1. УЧЕТНЫЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
# =====================================================================
EMAIL = os.getenv("TODOIST_EMAIL")
PASSWORD = os.getenv("TODOIST_PASSWORD")
TD_API_TOKEN = os.getenv("TD_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TD_API_TOKEN}", "Content-Type": "application/json"}

# =====================================================================
# 2. ПУТИ К ФАЙЛАМ И ДИРЕКТОРИЯМ
# =====================================================================
LIST_OF_TASKS_CSV = os.path.join(ROOT_DIR, "test_data", "list_of_tasks.csv")
ORDERING_TEST_DATA_CSV = os.path.join(ROOT_DIR, "test_data", "ordering_test_data.csv")
TESTS_DATE_AND_TIME_CSV = os.path.join(ROOT_DIR, "test_data", "tests_date_and_time.csv")
TESTS_RECURRING_CALENDAR_CSV = os.path.join(ROOT_DIR, "test_data", "tests_recurring_calendar.csv")

# =====================================================================
# 3. СЛОВАРИ И КАРТЫ СООТВЕТСТВИЙ
# =====================================================================

# --- СЛОВАРЬ СООТВЕТСТВИЯ НАЗВАНИЙ МЕСЯЦЕВ ИЗ ПРИЛОЖЕНИЯ И ИХ ЧИСЛОВЫХ ПРЕДСТАВЛЕНИЙ ---
MONTHS = {"янв": 1, "февр": 2, "мар": 3, "апр": 4, "мая": 5, "июн": 6, "июл": 7, "авг": 8, "сент": 9, "окт": 10, "нояб": 11, "дек": 12}

# --- СЛОВАРЬ СООТВЕТСТВИЯ МЕЖДУ ПРИОРИТЕТОМ ЗАДАЧИ В UI И ВНУТРЕННИМ ПРИОРИТЕТОМ ---
PRIORITY_MAP = {
    1: "Приоритет 4",
    2: "Приоритет 3",
    3: "Приоритет 2",
    4: "Приоритет 1",
}

# --- СЛОВАРЬ СООТВЕТСТВИЯ НАЗВАНИЙ ДНЕЙ НЕДЕЛИ И ИХ ЧИСЛОВЫХ ПРЕДСТАВЛЕНИЙ ---
WEEKDAYS = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
    "Воскресенье": 6,
}

COLUMN_TRANSLATION = {
    # Для списка задач (API)
    "Название": "content",
    "Срок": "due",
    "Приоритет": "priority",
    "Метки": "labels",
    # Для календаря и дат
    "Значение": "text_input",
    "Ожидаемый текст": "expected_text",
    "Ожидаемое значение повтора": "expected_recurrence_input",
    "Ожидаемый день": "expected_day",
    "Ожидаемый текст на кнопке повтора": "expected_recurrence_btn",
    "Интервал": "interval",
    "Период проверки": "period",
    "Дата окончания": "end_date",
    "Ожидаемый цвет": "expected_color",
    # Для сортировки
    "Параметр группировки": "group_by",
    "Параметр сортировки": "sort_by",
    "Направление": "direction",
}