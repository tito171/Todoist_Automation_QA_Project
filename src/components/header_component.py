from components.base_component import BaseComponent
from selenium.webdriver.common.by import By
from components.view_component import ViewComponent


class HeaderComponent(BaseComponent):
    DISPLAY_BTN = (By.XPATH, "//*[@type='button' and @aria-label='Меню опций отображения']")

    def open_view_menu(self):
        self.click_inner(self.DISPLAY_BTN)
        return ViewComponent(self.driver)
