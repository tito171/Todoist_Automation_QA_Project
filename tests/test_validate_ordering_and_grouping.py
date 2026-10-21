from test_data.test_data_store import ORDERING_TEST_DATA
from tests.helpers import verify_tasks_grouping, verify_tasks_sorting
import pytest, allure

pytestmark = pytest.mark.order(2)


@pytest.fixture(scope="module", autouse=True)
def reset_view_options(main_page):
    yield
    main_page.header.open_view_menu().reset_view_options()


@allure.epic("Управление списком задач")
@allure.feature("Фильтрация, группировка и сортировка")
@allure.story("Валидация комбинированных режимов отображения задач")
@allure.title("Группировка по '{case[group_by]}' - Сортировка по '{case[sort_by]}' ({case[direction]})")
@pytest.mark.parametrize("case", ORDERING_TEST_DATA, ids=lambda x: f"{x.get('group_by')}-{x.get('sort_by')}-{x.get('direction')}")
def test_validate_ordering_and_grouping(main_page, tasks_map, case):
    actual_tasks=main_page.header.open_view_menu().apply_view_options(case['group_by'],case['sort_by'],case['direction']).get_all_tasks(tasks_map)
    assert verify_tasks_grouping(actual_tasks,case['group_by'])
    assert verify_tasks_sorting(actual_tasks,case['sort_by'],case['direction'])
