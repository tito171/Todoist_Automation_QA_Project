from selenium.webdriver.common.by import By
from components.header_component import HeaderComponent
from components.sidebar_component import SidebarComponent
from pages.base_page import BasePage
from config import URL_INBOX_PAGE


class InboxPage(BasePage):
    URL = URL_INBOX_PAGE
    NAV_MENU = (By.CSS_SELECTOR, "div[data-testid='app-sidebar-container']")

    @property
    def sidebar(self):
        return SidebarComponent(self.driver)

    @property
    def header(self):
        return HeaderComponent(self.driver)

    def wait_until_page_loaded(self, timeout=None):
        self.wait_for_element_presence(self.NAV_MENU, timeout=timeout)
