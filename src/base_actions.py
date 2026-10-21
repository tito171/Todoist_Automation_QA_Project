from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException


class BaseActions:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def type(self, locator, text_input):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(text_input)

    def click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def wait_for_element_presence(self, locator, timeout=None):
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        return wait.until(EC.presence_of_element_located(locator))

    def wait_for_element_to_be_invisible(self, locator):
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_all_elements(self, locator):
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def find_sub_elements(self, parent_element, sub_locator):
        return parent_element.find_elements(*sub_locator)

    def get_sub_element_text(self, parent_element, sub_locator, fail_if_missing=True):
        try:
            return parent_element.find_element(*sub_locator).text
        except NoSuchElementException:
            if fail_if_missing:
                raise NoSuchElementException(f"Ошибка! Текстовый подэлемент {sub_locator} отсутствует внутри родительского контейнера")
            return None

    def get_sub_element_attr(self, parent_element, sub_locator, attr_name):
        try:
            return parent_element.find_element(*sub_locator).get_dom_attribute(attr_name)
        except NoSuchElementException:
            raise NoSuchElementException(f"Ошибка! Не удалось забрать атрибут '{attr_name}', так как подэлемент с локатором {sub_locator} не найден в родительском контейнере")
