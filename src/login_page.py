from selenium.webdriver.common.by import By
from src.base_page import BasePage
from config import URL_LOGIN_PAGE


class LoginPage(BasePage):
    URL = URL_LOGIN_PAGE
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[autocomplete='current-password']")
    LOGIN_BTN = (By.CSS_SELECTOR, "form button[type='submit']")

    def login_as(self, email, password):
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)
