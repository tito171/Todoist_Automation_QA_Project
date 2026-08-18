import os
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
GLOBAL_TEST_DATE = "2026-07-01"
BASE_URL = "https://api.todoist.com"
URL_LOGIN_PAGE = "https://app.todoist.com/auth/login"
URL_MAIN_PAGE="https://app.todoist.com/app/inbox"

load_dotenv(dotenv_path=ENV_PATH)

# =====================================================================
# 1. УЧЕТНЫЕ ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
# =====================================================================
EMAIL = os.getenv("TODOIST_EMAIL")
PASSWORD = os.getenv("TODOIST_PASSWORD")
TD_API_TOKEN = os.getenv("TD_API_TOKEN")

# =====================================================================
# 2. ПУТИ К ФАЙЛАМ И ДИРЕКТОРИЯМ
# =====================================================================
LIST_OF_TASKS_XLSX = os.path.join(ROOT_DIR, "test_data", "list_of_tasks.xlsx")
TESTS_DATA_AND_TIME_XLSX = os.path.join(ROOT_DIR, "test_data", "tests_date_and_time.xlsx")
TESTS_RECURRING_CALENDAR_XLSX = os.path.join(ROOT_DIR, "test_data", "tests_recurring_calendar.xlsx")
TESTS_SORTING_AND_GROUPNG_XLSX = os.path.join(ROOT_DIR, "test_data", "tests_sorting_and_grouping.xlsx")

# =====================================================================
# 3. СЛОВАРИ И КАРТЫ СООТВЕТСТВИЙ
# =====================================================================

# --- СЛОВАРЬ НАЗВАНИЙ МЕСЯЦЕВ ИЗ ПРИЛОЖЕНИЯ И ИХ ЧИСЛОВЫХ ПРЕДСТАВЛЕНИЙ ---
MONTHS = {"янв": 1, "февр": 2, "мар": 3, "апр": 4, "мая": 5, "июн": 6, "июл": 7, "авг": 8, "сент": 9, "окт": 10, "нояб": 11, "дек": 12}

# --- СЛОВАРЬ ДЛЯ ОПРЕДЕЛЕНИЯ СООТВЕТСТВИЯ МЕЖДУ ПРИОРИТЕТОМ ЗАДАЧИ В UI И ВНУТРЕННИМ ПРИОРИТЕТОМ ---
PRIORITY_MAP = {
    1: "Приоритет 4",
    2: "Приоритет 3",
    3: "Приоритет 2",
    4: "Приоритет 1",
}

# --- СЛОВАРЬ СООТВЕТСВИЯ НАЗВАНИЙ ДНЕЙ НЕДЕЛИ И ИХ ЧИСЛОВЫХ ПРЕДСТАВЛЕНИЙ ---
WEEKDAYS = {
    "Понедельник": 0,
    "Вторник": 1,
    "Среда": 2,
    "Четверг": 3,
    "Пятница": 4,
    "Суббота": 5,
    "Воскресенье": 6,
}

# --- СЛОВАРЬ СООТВЕТСВИЯ НАЗВАНИЙ ЦВЕТОВ И ИХ КОДОВ ---
COLORS = {"зеленый": "rgba(5, 133, 39, 1)", "коричневый": "rgba(173, 98, 0, 1)", "фиолетовый": "rgba(105, 46, 194, 1)", "серый": "rgba(128, 128, 128, 1)"}
