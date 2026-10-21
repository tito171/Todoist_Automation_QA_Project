from base_actions import BaseActions


class BaseComponent(BaseActions):
    def __init__(self, driver, timeout=30, root_locator=None):
        super().__init__(driver, timeout)
        self.root_locator = root_locator

    def click_inner(self, sub_locator):
        if self.root_locator:
            self.wait_for_element(self.root_locator)
            self.click(sub_locator)
        else:
            self.click(sub_locator)

    def type_inner(self, sub_locator, text_input):
        if self.root_locator:
            self.wait_for_element(self.root_locator)
            self.type(sub_locator, text_input)
        else:
            self.type(sub_locator, text_input)

    def find_inner_elements(self, sub_locator):
        if self.root_locator:
            parent_element = self.wait_for_element(self.root_locator)
            sub_elements = self.find_sub_elements(parent_element, sub_locator)
            return sub_elements
        else:
            return self.wait_for_all_elements(sub_locator)
