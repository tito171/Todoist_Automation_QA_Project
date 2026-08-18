import os
import pandas as pd

from config import (
    LIST_OF_TASKS_XLSX,
    ROOT_DIR,
    TESTS_DATA_AND_TIME_XLSX,
    TESTS_RECURRING_CALENDAR_XLSX,
    TESTS_SORTING_AND_GROUPNG_XLSX,
)

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


def parse_base_excel(file_path):
    df = pd.read_excel(file_path, dtype=str).dropna(how="all")
    df.columns = df.columns.str.strip()

    ignored_columns = ["№", "Дата в системе", "Правило валидации интервала"]
    df = df.drop(columns=ignored_columns, errors="ignore")
    df = df.rename(columns=COLUMN_TRANSLATION)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    cases = df.to_dict(orient="records")

    for case in cases:
        for key, value in case.items():
            if str(value).strip() in ("nan", "NaN", "None"):
                case[key] = None
        if case.get("due") is not None:
            case["due"] = {"string": str(case["due"])}

    return cases


def post_process_api_tasks(cases):
    for case in cases:
        if "labels" in case:
            raw_labels = case["labels"]
            if raw_labels is None:
                case["labels"] = []
            else:
                case["labels"] = [l.strip() for l in str(raw_labels).split(",")]

        if "priority" in case:
            raw_priority = case["priority"]
            if raw_priority is None:
                case["priority"] = 1
            else:
                try:
                    case["priority"] = int(raw_priority)
                except ValueError:
                    case["priority"] = 1
    return cases


data_dir = os.path.join(ROOT_DIR, "test_data")

date_and_time = parse_base_excel(TESTS_DATA_AND_TIME_XLSX)
recurring_date = parse_base_excel(TESTS_RECURRING_CALENDAR_XLSX)
sorting_and_grouping = parse_base_excel(TESTS_SORTING_AND_GROUPNG_XLSX)

raw_api_tasks = parse_base_excel(LIST_OF_TASKS_XLSX)
api_tasks_data = post_process_api_tasks(raw_api_tasks)

output_file = os.path.join(data_dir, "test_data_store.py")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# ====================================================================\n")
    f.write("# ЭТОТ ФАЙЛ СГЕНЕРИРОВАН АВТОМАТИЧЕСКИ ИЗ EXCEL ТАБЛИЦ.\n")
    f.write("# НЕ ПРАВЬТЕ ЕГО РУКАМИ! ДЛЯ ОБНОВЛЕНИЯ ЗАПУСТИТЕ СКРИПТ ГЕНЕРАЦИИ.\n")
    f.write("# ====================================================================\n\n")

    f.write(f"LIST_OF_TASKS = {repr(api_tasks_data)}\n\n")
    f.write(f"TESTS_RECURRING_CALENDAR = {repr(recurring_date)}\n\n")
    f.write(f"TESTS_DATA_AND_TIME = {repr(date_and_time)}\n\n")
    f.write(f"TESTS_SORTING_AND_GROUPNG = {repr(sorting_and_grouping)}\n")
