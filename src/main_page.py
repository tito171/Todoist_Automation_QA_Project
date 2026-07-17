from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from src.base_page import BasePage
from config import MONTHS, WEEKDAYS
import json, allure, re
from time import sleep
from datetime import datetime, timedelta


class SortingComponent(BasePage):
    DISPLAY_BTN = (By.XPATH, "//*[@type='button' and @aria-label='Меню опций отображения']")
    DISPLAY_POPUP_WINDOW = (By.CSS_SELECTOR, "div[aria-label='Меню опций отображения']")
    GROUP_LIST_OPTION = (By.XPATH, "//div[.//div[text()='Группировка']]/following-sibling::*[@role='combobox']")
    SORT_LIST_OPTION = (By.XPATH, "//div[.//div[text()='Сортировка']]/following-sibling::*[@role='combobox']")
    SORT_LIST_DIRECTION = (By.XPATH, "//div[.//div[text()='Направление']]/following-sibling::*[@role='combobox']")
    GROUP_CRITERIA_OPTIONS = {
        "Срок": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='Срок']]"),
        "Приоритет": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='Приоритет']]"),
        "Метка": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='Метка']]"),
    }
    SORT_CRITERIA_OPTIONS = {
        "Название": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='Название']]"),
        "Срок": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='Срок']]"),
        "Приоритет": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='Приоритет']]"),
    }
    SORT_DIRECTION_OPTIONS = {
        "По убыванию": (By.XPATH, "//*[@role='listbox']//*[@role='option']//*[.//div[text()='По убыванию']]"),  # по убыванию
        "По возрастанию": (
            By.XPATH,
            "//*[@role='listbox']//*[@role='option']//*[.//div[text()='По возрастанию']]",
        ),
    }
    TASK_CARD = (By.CSS_SELECTOR, "li[data-testid='task-list-item']")
    TASK_GROUP_SECTION = (By.CSS_SELECTOR, "section[data-testid='section']")
    GROUP_HEADER = (By.CSS_SELECTOR, "div[class*='section_header_content']")
    TASK_NAME = (By.CSS_SELECTOR, "div[class='task_content']")
    TASK_PRIORITY = (By.CSS_SELECTOR, "button[class*='task_checkbox']")
    TASK_DATE = (By.CSS_SELECTOR, "button[data-testid='due-date-control'] span[class*='date']")
    TASK_LABELES = (By.CSS_SELECTOR, "span[class*='simple_content']")
    RESET_ALL = (By.XPATH, "//section//button[.//span[contains(text(), 'Сбросить все')]]")

    def sort_tasks_list(self, group_by, sort_by, direction):
        # Сортирует список задач по заданным параметрам группировки, сортировки и направления
        self.click(self.DISPLAY_BTN)

        self.click(self.GROUP_LIST_OPTION)
        self.click(self.GROUP_CRITERIA_OPTIONS[group_by])

        self.click(self.SORT_LIST_OPTION)
        self.click(self.SORT_CRITERIA_OPTIONS[sort_by])

        self.click(self.SORT_LIST_DIRECTION)
        self.click(self.SORT_DIRECTION_OPTIONS[direction])

        # Закрывает настройки отображения списка задач
        self.wait_for_element(self.DISPLAY_POPUP_WINDOW).send_keys(Keys.ESCAPE)
        sleep(0.5)

    def get_all_tasks(self):
        # Возвращает список задач сгруппированный по параметрам
        # Задача состоит из 4-х полей: content, priority, date, labels
        # Общий список задач это словарь со списками словарей
        # Задача это словарь, задачи одной группы объединяются в списки, а группа это ключ общего словаря
        group_sections = self.wait_for_all_elements(self.TASK_GROUP_SECTION)
        # словарь со списками словарей {группа:[{'content':,'priority':,'date':}, {'content':,'priority':,'date':}]}
        actual_tasks = {}
        for group_section in group_sections:
            group_name = self.get_sub_element_text(group_section, self.GROUP_HEADER)
            actual_tasks[group_name] = []  # список словарей
            tasks_containers = self.find_sub_elements(group_section, self.TASK_CARD)
            for container in tasks_containers:
                date_text = self.get_sub_element_text(container, self.TASK_DATE, fail_if_missing=False)
                labels = self.find_sub_elements(container, self.TASK_LABELES)
                actual_tasks[group_name].append(
                    {
                        "content": self.get_sub_element_text(container, self.TASK_NAME),
                        "priority": self._get_priority_of_task(container),
                        "date": self._get_date_of_task(date_text, group_name),
                        "labels": [label.text for label in labels],
                        "id": container.get_dom_attribute("data-item-id"),
                    }
                )
        allure.attach(json.dumps(actual_tasks, indent=4, ensure_ascii=False), name="Собранные задачи с UI", attachment_type=allure.attachment_type.TEXT)
        return actual_tasks

    def _get_priority_of_task(self, container):
        class_elem = self.get_sub_element_attr(container, self.TASK_PRIORITY, "class")
        match = re.search(r"priority_([1-4])", class_elem)
        return int(match.group(1)) if match else None

    def _get_date_of_task(self, date_text, group_name):
        if date_text is None:
            if group_name != "Без срока" and re.match(r"^\d{1,2}\s[а-я]+", group_name):
                return self._parse_date_from_group_name(group_name)
            else:
                return date_text

        date_text_parts = date_text.split()
        if len(date_text_parts) == 1:
            try:
                datetime.strptime(date_text, "%H:%M")
                base_date = self._parse_date_from_group_name(group_name)
                return f"{base_date}T{date_text}:00"
            except ValueError:
                pass
        return self._parse_date_from_string(date_text)

    def _parse_date_from_group_name(self, group_name):
        # Если группировка по сроку, то то на карточке задачи визуально срок отсутствует и date_text = None, но при этом у задачи срок присутствует
        # Чтобы получить срок выполнения задачи, нужно распарсить имя группы в определнный формат
        # 2 июл ‧ Сегодня ‧ Четверг
        # 2 июл ‧ Четверг
        # 2 июл 2027 ‧ Пятница
        # Разбиваем имя группы на элементы
        # Получим 3 элемента или 2 элемента
        # 2 июл ‧ Сегодня ‧ Четверг = [2 июл, Сегодня, Четверг]
        # 2 июл 2027 ‧ Пятница = [2 июл 2027, Пятница]
        base_date = group_name.split(" ‧ ")[0].split()

        day_ = int(base_date[0])
        month_ = MONTHS[base_date[1]]
        year_ = base_date[2] if len(base_date) == 3 else datetime.now().year

        return f"{year_}-{month_:02d}-{day_:02d}"

    def _parse_date_from_string(self, date_text):
        # Парсер для срока задачи из UI
        # Есть четкие форматы даты (Сегодня, Завтра, Понедельник, Вторник 18:00)
        # то есть дни прописываются строго с заглавной буквы, и между днем и временем нет предлогов
        # Соответственно в коде парсера нет приведения в нижнему регистру, так как набор входных данных четко задан
        # и если сломается верстка, или разработчик поменяет формат, то тест упадет с понятной ошибкой, и нужно будет либо менять тест, либо заводить баг-репорт
        date_parts = date_text.split()
        current_date = datetime.now().date()

        if date_parts[0].isdigit():
            day_ = int(date_parts[0])
            month_ = MONTHS[date_parts[1]]
            if len(date_parts) > 2 and date_parts[2].isdigit() and len(date_parts[2]) == 4:
                year_ = date_parts[2]
                time_ = date_parts[3] if len(date_parts) > 3 else None
            else:
                year_ = current_date.year
                time_ = date_parts[2] if len(date_parts) > 2 else None
            format_date = f"{year_}-{month_:02d}-{day_:02d}"
            return f"{year_}-{month_:02d}-{day_:02d}T{time_}:00" if time_ else format_date

        date = date_parts[0]
        match date:
            case "Сегодня":
                base_date = current_date
            case "Завтра":
                base_date = current_date + timedelta(days=1)
            case "Понедельник" | "Вторник" | "Среда" | "Четверг" | "Пятница" | "Суббота" | "Воскресенье":
                num_day = WEEKDAYS[date]
                date_ahead = num_day - current_date.weekday()
                if date_ahead <= 0:
                    date_ahead += 7
                base_date = current_date + timedelta(days=date_ahead)
            case _:
                raise KeyError(f"Неизвестный формат или день недели: '{date}'")
        format_date = base_date.strftime("%Y-%m-%d")
        format_time = date_parts[1] if len(date_parts) > 1 else None
        return f"{format_date}T{format_time}:00" if format_time else format_date

    def reset_sorting(self):
        self.click(self.DISPLAY_BTN)
        self.click(self.RESET_ALL)
        self.wait_for_element(self.DISPLAY_POPUP_WINDOW).send_keys(Keys.ESCAPE)
        sleep(0.5)


class NLPInputComponent(BasePage):
    CREATE_TASK_BTN = (By.XPATH, "//div[@data-testid='app-sidebar-container']//button[@type='button' and contains(., 'Добавить задачу')]")
    # TASK_EDITOR = (By.CSS_SELECTOR, "div[data-testid='quick-add']")
    TASK_EDITOR = (By.CSS_SELECTOR, "form[data-testid='task-editor']")
    # TASK_EDITOR_CONTENT_FIELD = (By.XPATH, "//div[@aria-label='Название задачи']")
    TASK_EDITOR_CONTENT_FIELD = (By.XPATH, "//form[@data-testid='task-editor']//div[@aria-label='Название задачи']")
    NLP_TAG_DATE = (By.XPATH, "//span[@data-testid='natural-language-match']")
    TASK_EDITOR_DATE_BTN = (By.XPATH, "//div[@aria-label='Выбрать дату' and @role='button']")
    TASK_EDITOR_DATE_TEXT = (By.CSS_SELECTOR, "span[class*='date']")
    TASK_EDITOR_DATE_RECURRING_ICON = (By.CSS_SELECTOR, "span[class*='date'] svg path[d^='M7 3H4.5a.5.5']")
    # TASK_EDITOR_CANCEL_BTN = (By.XPATH, "//button[@type='button' and @aria-label='Отмена']")
    TASK_EDITOR_CANCEL_BTN = (By.XPATH, "//div[@data-testid='task-editor-action-buttons']//button[@type='button' and contains(.,'Отмена')]")
    SCHEDULER = (By.CSS_SELECTOR, "div[data-testid='scheduler-view']")
    SCHEDULER_BTN_NODATE = (By.CSS_SELECTOR, "button[data-track='scheduler|date_shortcut_nodate']")
    SCHEDULER_INPUT = (By.CSS_SELECTOR, "input[aria-label='Введите срок']")
    CALENDAR_DAY_SELECTED = (By.CSS_SELECTOR, "button[class*='calendar__day--selected'] span[class='calendar__day__date__number']")
    RECURRENCE_BTN = (By.CSS_SELECTOR, "button[data-testid='recurrence-menu-button'] span")
    DATE_PICKER_NEXT_MONTH = (By.XPATH, "//button[@class='date-picker-header-action' and @aria-label='Перейти к следующему месяцу']")
    DATE_PICKER_PREV_MONTH = (By.XPATH, "//button[@class='date-picker-header-action' and @aria-label='Перейти к предыдущему месяцу']")

    def open_task_form(self):
        self.click(self.CREATE_TASK_BTN)
        self.wait_for_element(self.TASK_EDITOR)

    def close_task_form(self):
        self.click(self.TASK_EDITOR_CANCEL_BTN)

    def type_name_task(self, text_input):
        self.type(self.TASK_EDITOR_CONTENT_FIELD, text_input)

    def tag_date_is_present(self):
        return self.is_element_visible(self.NLP_TAG_DATE)

    def get_actual_date_button_data(self):
        element_text = self.wait_for_element(self.TASK_EDITOR_DATE_TEXT)
        actual_text = element_text.text if element_text else ""
        actual_color = element_text.value_of_css_property("color") if element_text else ""
        button_info = f"Текст на кнопке: '{actual_text}'\nЦвет текста (rgba): '{actual_color}'"
        allure.attach(body=button_info, name="Собранные UI-данные кнопки 'Срок'", attachment_type=allure.attachment_type.TEXT)
        return {"text": actual_text, "color": actual_color}

    def icon_recurring_is_present(self):
        return self.is_element_visible(self.TASK_EDITOR_DATE_RECURRING_ICON)

    def get_data_from_scheduler(self, interval_str, period_str, end_date_str):
        self.click(self.TASK_EDITOR_DATE_BTN)
        self.wait_for_element(self.SCHEDULER)
        text_recurrence_input = self.wait_for_element(self.SCHEDULER_INPUT).get_dom_attribute("value")
        calendar_day = self.wait_for_element(self.CALENDAR_DAY_SELECTED).text
        text_recurrence_btn = self.wait_for_element(self.RECURRENCE_BTN).text

        return {
            "text_recurrence_input": text_recurrence_input,
            "calendar_day": calendar_day,
            "text_recurrence_btn": text_recurrence_btn,
            "valid_interval": self._validate_schedule(interval_str, period_str, end_date_str),
        }

    def _validate_schedule(self, interval_str, period_str, end_date_str):
        list_dates_obj = self._get_recurrence_dates(period_str)
        intervals = [(list_dates_obj[i + 1] - list_dates_obj[i]).days for i in range(len(list_dates_obj) - 1)]
        allowed_intervals = {int(x.strip()) for x in interval_str.split(",")}
        if not set(intervals).issubset(allowed_intervals):
            error_msg = (
                f"Интервал нарушен!\n"
                f"Фактические шаги в днях между датами: {set(intervals)}\n"
                f"Ожидаемые шаги: {allowed_intervals}\n"
                f"Полный список дат в сетке календаря: {[d.strftime('%Y-%m-%d') for d in list_dates_obj]}"
            )
            allure.attach(body=error_msg, name="Нарушение интервалов дат в календаре", attachment_type=allure.attachment_type.TEXT)
            return False

        if end_date_str:
            last_allow_date_obj = None
            end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            while not last_allow_date_obj:
                target_buttons = self.wait_for_all_elements((By.CSS_SELECTOR, f"button[aria-label='{end_date_str}']"))
                if target_buttons:
                    has_recurrence = len(self.find_sub_elements(target_buttons[0], (By.CLASS_NAME, "calendar__day--recurrence"))) > 0
                    if has_recurrence:
                        last_allow_date_obj = end_date_obj
                    else:
                        recurrence_elements = self.wait_for_all_elements((By.CLASS_NAME, "calendar__day--recurrence"))
                        if recurrence_elements:
                            parent_button = self.find_sub_element(recurrence_elements[-1], (By.XPATH, ".."))
                            date_str = parent_button.get_dom_attribute("aria-label")
                            if date_str:
                                potential_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                                if potential_date <= end_date_obj:
                                    last_allow_date_obj = potential_date
                        else:
                            self.click(self.DATE_PICKER_PREV_MONTH)
                            sleep(0.3)
                else:
                    self.click(self.DATE_PICKER_NEXT_MONTH)
                    sleep(0.3)
            base_interval = next(iter(allowed_intervals))
            forbidden_date_obj = last_allow_date_obj + timedelta(days=base_interval)
            forbidden_date_str = forbidden_date_obj.strftime("%Y-%m-%d")
            while True:
                forbidden_date_buttons = self.wait_for_all_elements((By.CSS_SELECTOR, f"button[aria-label='{forbidden_date_str}']"))
                if forbidden_date_buttons:
                    has_forbidden_recurrence = len(self.find_sub_elements(forbidden_date_buttons[0], (By.CLASS_NAME, "calendar__day--recurrence"))) > 0
                    if has_forbidden_recurrence:
                        forbidden_msg = (
                            f"Ошибка дедлайна повторения!\n"
                            f"Календарь ошибочно подсветил пунктиром дату: {forbidden_date_str}\n"
                            f"Хотя установленная дата окончания повторов: {end_date_str}\n"
                            f"Последняя разрешенная дата повтора в сетке: {last_allow_date_obj.strftime('%Y-%m-%d')}"
                        )
                        allure.attach(body=forbidden_msg, name="Выход даты повтора за пределы дедлайна", attachment_type=allure.attachment_type.TEXT)
                        return False
                    else:
                        break
                else:
                    self.click(self.DATE_PICKER_NEXT_MONTH)
                    sleep(0.3)
        self.click(self.SCHEDULER_BTN_NODATE)
        return True

    def _get_recurrence_dates(self, period):
        set_dates_obj = set()  # множество объектов datetime.date (даты повтора, выделенных пунктиром)
        for _ in range(int(period)):
            day_buttons_recurrence = self.wait_for_all_elements((By.CLASS_NAME, "calendar__day--recurrence"))
            for day_button in day_buttons_recurrence:
                parent_button = self.find_sub_element(day_button, (By.XPATH, ".."))
                date_str = parent_button.get_dom_attribute("aria-label")
                if date_str:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    set_dates_obj.add(date_obj)
            self.click(self.DATE_PICKER_NEXT_MONTH)
        return sorted(list(set_dates_obj))


class MainPage(BasePage):
    def __init__(self, driver, timeout=15):
        super().__init__(driver, timeout)
        self.sorting = SortingComponent(driver)
        self.nlp_input = NLPInputComponent(driver)
