from datetime import datetime, time
import allure
from config import MONTHS, PRIORITY_MAP


# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПЕРЕВОДА СТРОКОВОЙ ДАТЫ В ОБЪЕКТ DATETIME (ИСПОЛЬЗУЕТСЯ ДЛЯ СРОКА ЗАДАЧИ И ДАТЫ СОЗДАНИЯ) ---
def parse_date(date_str):
    # tzinfo : Time Zone Information
    if not date_str:
        return datetime.max

    if len(date_str) == 10:
        base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return datetime.combine(base_date, time.max)

    date = datetime.fromisoformat(date_str)
    return date.replace(tzinfo=None)


# --- АТОМАРНЫЕ ФУНКЦИИ ПАТТЕРНА 'ЦЕПОЧКА ОБЯЗАННОСТЕЙ' ИЛИ КОМПАРАТОРЫ ДЛЯ ПАТТЕРНА 'СТРАТЕГИЯ'---
def compare_priority(task_1, task_2, direction):
    if task_1["priority"] != task_2["priority"]:
        return task_1["priority"] > task_2["priority"] if direction == "По убыванию" else task_1["priority"] < task_2["priority"]
    return None


def compare_date(task_1, task_2, direction):
    date_1 = parse_date(task_1["date"])
    date_2 = parse_date(task_2["date"])
    if date_1 != date_2:
        return date_1 > date_2 if direction == "По убыванию" else date_1 < date_2
    return None


def compare_added_at(task_1, task_2, direction):
    added_at_1 = parse_date(task_1["added_at"])
    added_at_2 = parse_date(task_2["added_at"])
    if added_at_1 != added_at_2:
        return added_at_1 > added_at_2 if direction == "По убыванию" else added_at_1 < added_at_2
    return None


def compare_content(task_1, task_2, direction):
    if task_1["content"] != task_2["content"]:
        return task_1["content"] > task_2["content"] if direction == "По убыванию" else task_1["content"] < task_2["content"]
    return None


def compare_priority_always_desc(task_1, task_2, _):
    if task_1["priority"] != task_2["priority"]:
        return task_1["priority"] > task_2["priority"]
    return None


def compare_date_always_asc(task_1, task_2, _):
    date_1 = parse_date(task_1["date"])
    date_2 = parse_date(task_2["date"])
    if date_1 != date_2:
        return date_1 < date_2
    return None


def compare_added_at_always_asc(task_1, task_2, _):
    added_at_1 = parse_date(task_1["added_at"])
    added_at_2 = parse_date(task_2["added_at"])
    if added_at_1 != added_at_2:
        return added_at_1 < added_at_2
    return None


# --- ДИСПЕТЧЕР ЦЕПОЧКИ ---
def execute_comparison_chain(task_1, task_2, direction, chain):
    for compare_func in chain:
        result = compare_func(task_1, task_2, direction)
        if result is not None:
            return result


# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПЕРЕВОДА НАЗВАНИЯ ГРУППЫ В ДАТУ (ИСПОЛЬЗУЕТСЯ ДЛЯ ПОЛУЧЕНИЯ СРОКА ЗАДАЧИ) ---
def parse_date_from_group_name(group_name):
    base_date = group_name.split(" ‧ ")[0].split()

    day_ = int(base_date[0])
    month_ = MONTHS[base_date[1]]
    year_ = int(base_date[2]) if len(base_date) == 3 else datetime.now().year
    return datetime(year_, month_, day_)


# --- СЛОВАРЬ СТРАТЕГИЙ ---
STRATEGIES = {
    "Приоритет": {
        "group_validator": lambda task, group_name: PRIORITY_MAP[task["priority"]] == group_name,
        "tasks_comparator": lambda task_1, task_2, direction: execute_comparison_chain(task_1, task_2, direction, [compare_priority, compare_date_always_asc, compare_added_at_always_asc]),
    },
    "Срок": {
        "group_validator": lambda task, group_name: parse_date(task["date"]).date() == parse_date_from_group_name(group_name).date(),
        "tasks_comparator": lambda task_1, task_2, direction: execute_comparison_chain(task_1, task_2, direction, [compare_date, compare_priority_always_desc, compare_added_at_always_asc]),
    },
    "Название": {
        "tasks_comparator": lambda task_1, task_2, direction: execute_comparison_chain(
            task_1,
            task_2,
            direction,
            [compare_content, compare_priority_always_desc, compare_date_always_asc, compare_added_at_always_asc],
        ),
    },
    "Метка": {
        "group_validator": lambda task, group_name: group_name in task["labels"],
    },
}


# --- КОНТЕКСТ СТРАТЕГИИ ---
def verify_tasks_grouping(tasks, group_by):
    strategy = STRATEGIES.get(group_by)
    if not strategy:
        raise ValueError(f"Неизвестная стратегия группировки: {group_by}")

    for group_name, tasks_in_group in tasks.items():
        if "group_validator" in strategy:
            validator = strategy["group_validator"]
            for task in tasks_in_group:
                if not validator(task, group_name):
                    error_msg = f"Задача находится не в той группе\n" f"Группа '{group_name}'\n" f"Задача: {task}\n"
                    allure.attach(body=error_msg, name="ОШИБКА ГРУППИРОВКИ", attachment_type=allure.attachment_type.TEXT)
                    return False
    return True


def verify_tasks_sorting(tasks, sort_by, direction):
    strategy = STRATEGIES.get(sort_by)
    if not strategy:
        raise ValueError(f"Неизвестная стратегия сортировки: {sort_by}")

    for group_name, tasks_in_group in tasks.items():
        if "tasks_comparator" in strategy:
            comparator = strategy["tasks_comparator"]
            for i in range(len(tasks_in_group) - 1):
                if not comparator(tasks_in_group[i], tasks_in_group[i + 1], direction):
                    error_msg = f"Ошибка в группе '{group_name}' при сортировке '{sort_by}' ({direction})\n" f"Задача 1: {tasks_in_group[i]}\n" f"Задача 2: {tasks_in_group[i+1]}\n"
                    allure.attach(body=error_msg, name="ОШИБКА СОРТИРОВКИ", attachment_type=allure.attachment_type.TEXT)
                    return False
    return True


def add_param_to_list_tasks(tasks_list, actual_tasks):
    data_index = {task["id"]: task["added_at"] for task in tasks_list}
    for list_of_tasks in actual_tasks.values():
        for task in list_of_tasks:
            task["added_at"] = data_index.get(task.get("id"))
    return actual_tasks


def mock_browser_time(driver, target_date):
    js_code = f"""
        // Находим разницу между реальным текущим временем и нашей фейковой датой
        const targetMs = new Date('{target_date}T00:00:00').getTime();
        const realMs = new Date().getTime();
        const timeOffset = targetMs - realMs; // Смещение времени

        const OriginalDate = Date;
        const OriginalDateTimeFormat = Intl.DateTimeFormat;

        // 1. Динамический мок Date (время ИДЕТ, но сдвинуто на нужную дату)
        function FakeDate(...args) {{
            if (!(this instanceof FakeDate)) {{
                return new OriginalDate(new OriginalDate().getTime() + timeOffset).toString();
            }}
            if (args.length === 0) {{
                return new OriginalDate(new OriginalDate().getTime() + timeOffset);
            }}
            return new OriginalDate(...args);
        }}
        Object.getOwnPropertyNames(OriginalDate).forEach(prop => {{
            Object.defineProperty(FakeDate, prop, Object.getOwnPropertyDescriptor(OriginalDate, prop));
        }});
        // Метод now() теперь тоже возвращает идущее вперед фейковое время
        FakeDate.now = () => new OriginalDate().getTime() + timeOffset;
        FakeDate.prototype = OriginalDate.prototype;
        window.Date = FakeDate;

        // 2. Мокаем Intl.DateTimeFormat (чтобы парсеры текста видели фейковое время)
        window.Intl.DateTimeFormat = function(locales, options) {{
            const formatter = new OriginalDateTimeFormat(locales, options);
            return {{
                format: function(date) {{
                    return formatter.format(date || new OriginalDate(FakeDate.now()));
                }},
                formatToParts: function(date) {{
                    return formatter.formatToParts(date || new OriginalDate(FakeDate.now()));
                }},
                resolvedOptions: function() {{
                    return formatter.resolvedOptions();
                }}
            }};
        }};
        Object.setPrototypeOf(window.Intl.DateTimeFormat, OriginalDateTimeFormat);

        // 3. КРИТИЧЕСКИЙ ШАГ: Корректируем системный таймер performance
        const originalPerformanceNow = window.performance.now.bind(window.performance);
        if (window.performance && window.performance.timeOrigin) {{
            // Сдвигаем точку отсчета времени страницы на нашу фейковую дату
            Object.defineProperty(window.performance, 'timeOrigin', {{
                get: () => targetMs
            }});
        }}
    """
    result = driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js_code})
    return result["identifier"]
