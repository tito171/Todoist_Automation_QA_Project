from test_data.test_data_store import TESTS_SORTING_AND_GROUPNG
from tests.helpers import add_param_to_list_tasks, verify_tasks_grouping, verify_tasks_sorting
import pytest, allure

pytestmark = pytest.mark.order(2)


@pytest.fixture(scope="module", autouse=True)
def reset_sorting(main_page):
    yield
    main_page.sorting.reset_sorting()


@allure.epic("Управление списком задач")
@allure.feature("Фильтрация, группировка и сортировка")
@allure.story("Валидация комбинированных режимов отображения задач")
@allure.title("Группировка по '{case[group_by]}' - Сортировка по '{case[sort_by]}' ({case[direction]})")
@pytest.mark.parametrize("case", TESTS_SORTING_AND_GROUPNG, ids=lambda x: f"{x.get('group_by')}-{x.get('sort_by')}-{x.get('direction')}")
def test_validate_ordering_and_grouping(main_page, tasks_list, case):
    main_page.tasks_list.wait_until_tasks_loaded()

    with allure.step(f"Сортировать список по параметрам: {case["group_by"]}, {case["sort_by"]}, {case["direction"]}"):
        main_page.sorting.sort_tasks_list(case["group_by"], case["sort_by"], case["direction"])

    with allure.step("Собрать список задач с интерфейса"):
        actual_tasks = main_page.tasks_list.get_all_tasks()

    with allure.step("Добавить к каждой задаче из списка параметры id и added_at, полученных в ответе от сервера"):
        tasks = add_param_to_list_tasks(tasks_list, actual_tasks)

    with allure.step("Проверить, что в группе находятся задачи с соответствующим параметром"):
        assert verify_tasks_grouping(tasks, case["group_by"])

    with allure.step("Проверить, что порядок задач в группе соответствует параметру и правилам сортировки"):
        assert verify_tasks_sorting(tasks, case["sort_by"], case["direction"])
