from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from src.login_page import LoginPage
from src.main_page import MainPage
from config import BASE_URL, EMAIL, PASSWORD, TD_API_TOKEN
from test_data.test_data_store import LIST_OF_TASKS
import pytest, httpx, json, uuid, os


@pytest.fixture(scope="session")
def driver():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument("--disable-save-password-bubble")
    options.add_argument("--disable-autofill")

    prefs = {
        "credentials_enable_service": False,  # Отключает предложение сохранить пароль
        "profile.password_manager_enabled": False,  # Отключает сам менеджер паролей
        "autofill.profile_enabled": False,  # Отключает автозаполнение адресов/форм
    }
    options.add_experimental_option("prefs", prefs)

    options.page_load_strategy = "eager"

    user_data_dir = os.path.join(os.getcwd(), "selenium_todoist_profile")
    options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(15)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def main_page(driver):
    main_page = MainPage(driver)
    main_page.open()
    try:
        main_page.wait_until_page_loaded(timeout=5)
        print("\nВход выполнен автоматически по сохраненному кэшу!")
    except:
        login_page = LoginPage(driver)
        login_page.login_as(EMAIL, PASSWORD)
        main_page.wait_until_page_loaded(timeout=60)
    yield main_page


@pytest.fixture(scope="module")

def tasks_list():
    headers = {"Authorization": f"Bearer {TD_API_TOKEN}"}
    commands = []
    for task in LIST_OF_TASKS:
        commands.append(
            {
                "type": "item_add",
                "temp_id": str(uuid.uuid4()),
                "uuid": str(uuid.uuid4()),
                "args": task,
            }
        )
    payload = {"commands": json.dumps(commands)}
    with httpx.Client() as client:
        response = client.post(f"{BASE_URL}/api/v1/sync", headers=headers, data=payload)
        if response.status_code != 200:
            pytest.fail(f"Глобальная ошибка Sync API. Код: {response.status_code}, Ответ: {response.text}")
        data = response.json()
        sync_status = data.get("sync_status")
        for cmd in commands:
            cmd_uuid = cmd.get("uuid")
            status = sync_status.get(cmd_uuid)
            if status != "ok":
                pytest.fail(f"Ошибка команды '{cmd_uuid}' на сервере")

        tasks = {}
        headers_rest = {"Authorization": f"Bearer {TD_API_TOKEN}", "Content-Type": "application/json"}
        response_rest = client.get(f"{BASE_URL}/api/v1/tasks", headers=headers_rest)
        if response_rest.status_code == 200:
            data_rest = response_rest.json()
            results = data_rest.get("results")
            for task in results:
                tasks.update({f"{task.get('id')}": f"{task.get('added_at')}"})

    yield tasks
    commands_delete = []
    for id in tasks.keys():
        commands_delete.append(
            {
                "type": "item_delete",
                "uuid": str(uuid.uuid4()),
                "args": {"id": f'{id}'},
            }
        )
    payload_delete = {"commands": json.dumps(commands_delete)}
    with httpx.Client() as client:
        response_delete = client.post(f"{BASE_URL}/api/v1/sync", headers=headers, data=payload_delete)
        if response_delete.status_code != 200:
            print(f"Не удалось удалить задачи. Код: {response_delete.status_code}, Ответ: {response_delete.text}")
