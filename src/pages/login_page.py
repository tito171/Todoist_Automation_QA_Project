from selenium.webdriver.common.by import By
from config import URL_LOGIN_PAGE
from pages.base_page import BasePage
from pages.inbox_page import InboxPage


class LoginPage(BasePage):
    URL = URL_LOGIN_PAGE
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[autocomplete='current-password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "form button[type='submit']")

    def type_username(self, email):
        self.type(self.EMAIL_INPUT, email)

    def type_password(self, password):
        self.type(self.PASSWORD_INPUT, password)

    def click_login_btn(self):
        self.click(self.LOGIN_BTN)

    def login_as(self, email, password):
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)
        return InboxPage(self.driver)
