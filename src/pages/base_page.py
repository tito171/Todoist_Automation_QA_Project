from base_actions import BaseActions


class BasePage(BaseActions):
    URL = None

    def open(self):
        if not self.URL:
            raise ValueError("URL не задан для этого класса страницы")
        self.driver.get(self.URL)
