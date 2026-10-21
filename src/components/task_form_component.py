from components.base_component import BaseComponent
from selenium.webdriver.common.by import By
from components.confirmation_modal import ConfirmationModal
from components.task_list_component import TaskListComponent


class TaskFormComponent(BaseComponent):
    TASK_EDITOR=(By.XPATH,"//div[@data-testid='quick-add']")
    TASK_EDITOR_CONTENT_FIELD = (By.XPATH, "//div[@aria-label='Название задачи']")
    TASK_EDITOR_CANCEL_BTN = (By.XPATH, "//button[@type='button' and @aria-label='Отмена']")
    TASK_EDITOR_CREATE_BTN=(By.XPATH,"//button[@type='button' and @aria-label='Добавить задачу']")

    def __init__(self, driver, timeout=30):
        super().__init__(driver, timeout, root_locator=self.TASK_EDITOR)

    def type_name_task(self, text_input):
        self.type_inner(self.TASK_EDITOR_CONTENT_FIELD, text_input)
        return self

    def create_task(self):
        self.click_inner(self.TASK_EDITOR_CREATE_BTN)
        return TaskListComponent(self.driver)

    def cancel_creation_task(self):
        self.click_inner(self.TASK_EDITOR_CANCEL_BTN)
        modal=ConfirmationModal(self.driver)
        try:
            self.wait_for_element(modal.CONFIRM_MODAL)
            modal.confirm_deletion()
        except:
            pass
        self.wait_for_element_invisibility(self.TASK_EDITOR)
        return TaskListComponent(self.driver)
