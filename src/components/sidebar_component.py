from components.base_component import BaseComponent
from components.task_form_component import TaskFormComponent
from selenium.webdriver.common.by import By


class SidebarComponent(BaseComponent):
    NAV_MENU = (By.CSS_SELECTOR, "div[data-testid='app-sidebar-container']")
    CREATE_TASK_BTN = (By.XPATH, "//div[@data-testid='app-sidebar-container']//button[@type='button' and contains(., 'Добавить задачу')]")

    def __init__(self, driver, timeout=30):
        super().__init__(driver, timeout, root_locator=self.NAV_MENU)

    def open_task_form(self):
        self.click_inner(self.CREATE_TASK_BTN)
        return TaskFormComponent(self.driver)
