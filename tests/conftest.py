from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from src.pages.login_page import LoginPage
from config import BASE_URL, EMAIL, PASSWORD, HEADERS
from test_data.test_data_store import LIST_OF_TASKS
import pytest, httpx, json, uuid


@pytest.fixture(scope="module")
def driver():
    options = Options()
    # options.add_argument("-headless=new")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    # options.set_preference("dom.webdriver.enabled", False)
    # options.set_preference("useAutomationExtension", False)

    options.page_load_strategy = "eager"

    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(15)
    yield driver
    driver.quit()


@pytest.fixture(scope="module")
def main_page(driver):
    login_page = LoginPage(driver)
    login_page.open()
    main_page=login_page.login_as(EMAIL,PASSWORD)
    yield main_page


@pytest.fixture(scope="module")
def create_tasks():
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
    with httpx.Client(headers=HEADERS) as client:
        response = client.post(f"{BASE_URL}/api/v1/sync", data=payload)
        if response.status_code != 200:
            pytest.fail(f"Глобальная ошибка Sync API. Код: {response.status_code}, Ответ: {response.text}")
        data = response.json()
        for cmd in commands:
            if data.get("sync_status").get(cmd.get("uuid")) != "ok":
                pytest.fail(f"Ошибка команды '{cmd.get("uuid")}' на сервере")
    yield


@pytest.fixture(scope="module")
def tasks_mapping(create_tasks):
    tasks_map = {}
    with httpx.Client(headers=HEADERS, timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/api/v1/tasks")
        if response.status_code != 200:
            pytest.fail(f"Ошибка REST API при получении метаданных задач. Код: {response.status_code}")

        data = response.json()
        results = data.get("results")
        for result in results:
            tasks_map.update({f"{result.get('id')}": f"{result.get('added_at')}"})
        yield tasks_map
        if not tasks_map:
            return
        commands = []
        for id in tasks_map.keys():
            commands.append(
                {
                    "type": "item_delete",
                    "uuid": str(uuid.uuid4()),
                    "args": {"id": f"{id}"},
                }
            )
        payload = {"commands": json.dumps(commands)}
        response = client.post(f"{BASE_URL}/api/v1/sync", data=payload)
        if response.status_code != 200:
            print(f"Не удалось удалить задачи. Код: {response.status_code}, Ответ: {response.text}")
