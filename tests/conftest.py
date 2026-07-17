from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.login_page import LoginPage
from src.main_page import MainPage
from config import BASE_URL, EMAIL, PASSWORD, TD_API_TOKEN
from test_data.test_data_store import LIST_OF_TASKS
import pytest, httpx


@pytest.fixture(scope="session")
def driver():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")
    prefs = {
        "credentials_enable_service": False,  # Отключает предложение сохранить пароль
        "profile.password_manager_enabled": False,  # Отключает сам менеджер паролей
        "autofill.profile_enabled": False,  # Отключает автозаполнение адресов/форм
    }
    options.add_experimental_option("prefs", prefs)
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def main_page(driver):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login_as(EMAIL, PASSWORD)
    main_page = MainPage(driver)
    yield main_page
    driver.delete_all_cookies()


@pytest.fixture(scope="module")
def tasks_list():
    tasks_api = []
    headers = {"Authorization": f"Bearer {TD_API_TOKEN}", "Content-Type": "application/json"}
    with httpx.Client() as client:
        for task in LIST_OF_TASKS:
            response = client.post(f"{BASE_URL}/api/v1/tasks", json=task, headers=headers)
            if response.status_code == 200:
                data = response.json()
                tasks_api.append({"id": data.get("id"), "added_at": data.get("added_at")})  # 'added_at':"2025-01-15T10:30:00Z"
            else:
                pytest.fail(f"API не смог создать задачу '{task['content']}'. Код: {response.status_code}")
    yield tasks_api
    with httpx.Client() as client:
        for task in tasks_api:
            response = client.delete(f"{BASE_URL}/api/v1/tasks/{task['id']}", headers=headers)
            if response.status_code != 204:
                print(f"Не удалось удалить задачу '{task['id']}' через API. Код: {response.status_code}")
