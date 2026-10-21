from components.base_component import BaseComponent
from selenium.webdriver.common.by import By


class ConfirmationModal(BaseComponent):
    CONFIRM_MODAL=(By.XPATH,"//div[@data-testid='confirmation-modal']")
    CONFIRM_DELETE_BTN=(By.XPATH,"//button[@type='button' and contains(.,'Удалить')]")

    def __init__(self, driver, timeout=30):
        super().__init__(driver, timeout, root_locator=self.CONFIRM_MODAL)

    def confirm_deletion(self):
        self.click_inner(self.CONFIRM_DELETE_BTN)
