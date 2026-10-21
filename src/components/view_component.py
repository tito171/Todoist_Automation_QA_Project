from components.base_component import BaseComponent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from components.task_list_component import TaskListComponent


class ViewComponent(BaseComponent):
    DISPLAY_POPUP_WINDOW = (By.XPATH, "//*[contains(@id, 'portal') and .//div[@aria-label='Меню опций отображения']]")
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
    RESET_ALL = (By.XPATH, "//section//button[.//span[contains(text(), 'Сбросить все')]]")

    def __init__(self, driver, timeout=30):
        super().__init__(driver, timeout, root_locator=self.DISPLAY_POPUP_WINDOW)

    def apply_view_options(self, group_by=None, sort_by=None, direction=None):
        if group_by:
            self.select_group_by(group_by)
        if sort_by:
            self.select_sort_by(sort_by)
        if direction:
            self.select_direction(direction)
        return self.close_menu()

    def select_group_by(self, group_by):
        self.click_inner(self.GROUP_LIST_OPTION)
        self.click_inner(self.GROUP_CRITERIA_OPTIONS[group_by])
        return self

    def select_sort_by(self, sort_by):
        self.click_inner(self.SORT_LIST_OPTION)
        self.click_inner(self.SORT_CRITERIA_OPTIONS[sort_by])
        return self

    def select_direction(self, direction):
        self.click_inner(self.SORT_LIST_DIRECTION)
        self.click_inner(self.SORT_DIRECTION_OPTIONS[direction])
        return self

    def reset_view_options(self):
        self.click_inner(self.RESET_ALL)
        return self.close_menu()

    def close_menu(self):
        self.wait_for_element(self.DISPLAY_POPUP_WINDOW).send_keys(Keys.ESCAPE)
        self.wait_for_element_to_be_invisible(self.DISPLAY_POPUP_WINDOW)
        return TaskListComponent(self.driver)
