from components.base_component import BaseComponent
from selenium.webdriver.common.by import By
import re
from datetime import datetime, timedelta
from config import MONTHS, WEEKDAYS


class TaskListComponent(BaseComponent):
    TASK_LIST = (By.CSS_SELECTOR, "div[data-testid='project-list-view']")
    TASK_CARD = (By.CSS_SELECTOR, "li[data-testid='task-list-item']")
    TASK_GROUP_SECTION = (By.CSS_SELECTOR, "section[data-testid='section']")
    GROUP_HEADER = (By.CSS_SELECTOR, "div[class*='section_header_content']")
    TASK_NAME = (By.CSS_SELECTOR, "div[class='task_content']")
    TASK_PRIORITY = (By.CSS_SELECTOR, "button[class*='task_checkbox']")
    TASK_DATE = (By.CSS_SELECTOR, "button[data-testid='due-date-control'] span[class*='date']")
    TASK_LABELES = (By.CSS_SELECTOR, "span[class*='simple_content']")

    def __init__(self, driver, timeout=30):
        super().__init__(driver, timeout, root_locator=self.TASK_LIST)

    def wait_until_tasks_loaded(self):
        self.find_inner_elements(self.TASK_CARD)

    def get_all_tasks(self, tasks_map=None):
        group_sections = self.find_inner_elements(self.TASK_GROUP_SECTION)
        actual_tasks = {}
        if group_sections:
            for group_section in group_sections:
                group_name = self.get_sub_element_text(group_section, self.GROUP_HEADER)
                actual_tasks[group_name] = self._parse_group_section(group_section, group_name, tasks_map)
        else:
            group_name = "(Без раздела)"
            tasks_containers = self.find_inner_elements(self.TASK_CARD)
            actual_tasks[group_name] = []
            for container in tasks_containers:
                task_data = self._parse_task_card(container, group_name, tasks_map)
                actual_tasks[group_name].append(task_data)
        return actual_tasks

    def _parse_group_section(self, group_section, group_name, tasks_map=None):
        group_tasks = []
        tasks_containers = self.find_sub_elements(group_section, self.TASK_CARD)
        for container in tasks_containers:
            task_data = self._parse_task_card(container, group_name, tasks_map)
            group_tasks.append(task_data)
        return group_tasks

    def _parse_task_card(self, container, group_name, tasks_map=None):
        date_text = self.get_sub_element_text(container, self.TASK_DATE, fail_if_missing=False)
        labels = self.find_sub_elements(container, self.TASK_LABELES)
        task_data = {
            "content": self.get_sub_element_text(container, self.TASK_NAME),
            "priority": self._get_priority_of_task(container),
            "date": self._get_date_of_task(date_text, group_name),
            "id": container.get_dom_attribute("data-item-id"),
        }
        if labels:
            task_data["labels"] = [label.text for label in labels]
        if tasks_map:
            task_data["added_at"] = tasks_map.get(task_data.get("id"))
        return task_data

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
        base_date = group_name.split(" ‧ ")[0].split()

        day_ = int(base_date[0])
        month_ = MONTHS[base_date[1]]
        year_ = base_date[2] if len(base_date) == 3 else datetime.now().year

        return f"{year_}-{month_:02d}-{day_:02d}"

    def _parse_date_from_string(self, date_text):
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
