import allure, pytest
from test_data.test_data_store import TESTS_DATA_AND_TIME, TESTS_RECURRING_CALENDAR
from tests.helpers import mock_browser_time
from config import COLORS, GLOBAL_TEST_DATE

pytestmark = pytest.mark.order(1)


@pytest.fixture(scope="module", autouse=True)
def setup_system_date(driver):
    script_id = mock_browser_time(driver, GLOBAL_TEST_DATE)
    yield
    driver.execute_cdp_cmd("Page.removeScriptToEvaluateOnNewDocument", {"identifier": script_id})
    driver.refresh()


@pytest.fixture(scope="module", autouse=True)
def open_form(main_page, setup_system_date):
    main_page.nlp_input.open_task_form()
    yield
    main_page.nlp_input.close_task_form()


@allure.epic("Интеллектуальный ввод задач")
@allure.feature("NLP распознавание дат и повторов")
@allure.story("Валидация цвета и текста распознанной даты")
@allure.title("Проверка распознавания даты: {case[text_input]}")
@pytest.mark.parametrize("case", TESTS_DATA_AND_TIME, ids=lambda x: f"Case: {x.get('text_input')}")
def test_nlp_date_recognition_and_color_validation(main_page, case):
    with allure.step(f"Ввести текст срока: {case['text_input']}"):
        main_page.nlp_input.type_name_task(case["text_input"])

    with allure.step("Проверить, что тег даты успешно появился в поле"):
        assert main_page.nlp_input.tag_date_is_present(), "Дата не распозналась парсером"

    with allure.step("Собрать актуальные данные с кнопки 'Срок'"):
        actual_date_button_data = main_page.nlp_input.get_actual_date_button_data()

    with allure.step(f"Проверить, что на кнопке 'Срок' появился ожидаемый текст: {case['expected_text']}"):
        assert actual_date_button_data["text"] == (case["expected_text"]), f"Текст на кнопке Срок не совпадает с ожидаемым\nОжидание: {case['expected_text']}\nРезультат: {actual_date_button_data['text']}"

    with allure.step(f"Проверить, что текст на кнопке 'Срок' имеет ожидаемый текст: {case['expected_color']}"):
        assert (
            actual_date_button_data["color"] == COLORS[case["expected_color"]]
        ), f"Цвет текста на кнопке не совпадает с ожидаемым\nОжидание: {COLORS[case["expected_color"]]}\nРезультат: {actual_date_button_data['color']}"


@allure.epic("Интеллектуальный ввод задач")
@allure.feature("NLP распознавание дат и повторов")
@allure.story("Распознавание циклических и повторяющихся дедлайнов")
@allure.title("Проверка циклического повтора: {case[text_input]}")
@pytest.mark.parametrize("case", TESTS_RECURRING_CALENDAR, ids=lambda x: f"Case: {x.get('text_input')}")
def test_nlp_recurring_deadlines_recognition(main_page, case):
    with allure.step(f"Ввести текст срока: {case['text_input']}"):
        main_page.nlp_input.type_name_task(case["text_input"])

    with allure.step("Проверить, что тег даты успешно появился в поле"):
        assert main_page.nlp_input.tag_date_is_present(), "Дата не распозналась парсером"

    with allure.step("Собрать актуальные данные с кнопки 'Срок'"):
        actual_date_button_data = main_page.nlp_input.get_actual_date_button_data()

    with allure.step(f"Проверить, что на кнопке 'Срок' появился ожидаемый текст: {case['expected_text']}"):
        assert actual_date_button_data["text"] == case["expected_text"], f"Текст на кнопке Срок не совпадает с ожидаемым\nОжидание: {case['expected_text']}\nРезультат: {actual_date_button_data['text']}"

    with allure.step("Проверить, что на кнопке 'Срок' появилась иконка повтора"):
        assert main_page.nlp_input.icon_recurring_is_present(), "Иконка повтора не отображается на кнопке 'Срок'"

    with allure.step("Открыть окно планировщика и собрать актуальные данные"):
        actual_data = main_page.nlp_input.get_data_from_scheduler(case["interval"], case["period"], case["end_date"])

    with allure.step(f"Проверить, что в поле 'Введите срок' отображается ожидаемый текст повтора: {case['expected_recurrence_input']}"):
        assert (
            actual_data["text_recurrence_input"] == case["expected_recurrence_input"]
        ), f"Текст в поле 'Введите срок' не совпадает с ожидаемым\nОжидание: {case['expected_recurrence_input']}\nРезультат: {actual_data['text_recurrence_input']}"

    with allure.step(f"Проверить, что в мини-календаре выбрана ожидаемая дата: {case['expected_day']}"):
        assert (
            actual_data["calendar_day"] == case["expected_day"]
        ), f"Выбранная дата на кнопке в мини-каледаре не совпадает с ожидаемой\nОжидание: {case['expected_day']}\nРезультат: {actual_data['calendar_day']}"

    with allure.step(f"Проверить, что в мини-календаре отмечены дни повтора согласно ожидаемому интервалу: {case['interval']}"):
        assert actual_data["valid_interval"] is True

    with allure.step(f"Проверить, что на кнопке 'Повтор' отображается ожидаемый текст повтора: {case['expected_recurrence_btn']}"):
        assert (
            actual_data["text_recurrence_btn"] == case["expected_recurrence_btn"]
        ), f"Текст на кнопке Повтор в мини-каледаре не совпадает с ожидаемым\nОжидание: {case["expected_recurrence_btn"]}\nРезультат: {actual_data['text_recurrence_btn']}"
