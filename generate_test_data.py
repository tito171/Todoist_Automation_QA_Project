import os, csv
from config import COLUMN_TRANSLATION, LIST_OF_TASKS_CSV, ORDERING_TEST_DATA_CSV, ROOT_DIR

# ==============================================================================
# ======================  Обработка с помощью python-csv  ======================
# ==============================================================================


def read_file(file):
    cases = []
    with open(file, mode="r", newline="", encoding="utf-8") as file_csv:
        csv_reader = csv.DictReader(file_csv, skipinitialspace=True)
        for row in csv_reader:
            case = {}
            cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
            for key, value in cleaned_row.items():
                if not value or value.strip().lower() in ("nan", "none"):
                    continue
                if key in ("Дата в системе", "Правило валидации интервала"):
                    continue
                new_key = COLUMN_TRANSLATION.get(key, key)
                if new_key == "due":
                    case[new_key] = {"string": str(value)}
                elif new_key == "labels":
                    case[new_key] = [l.strip() for l in str(value).split(",")]
                else:
                    if value.isdigit():
                        case[new_key] = int(value)
                    else:
                        case[new_key] = value
            cases.append(case)
        return cases


list_of_tasks = read_file(LIST_OF_TASKS_CSV)
ordering_test_data = read_file(ORDERING_TEST_DATA_CSV)
dict_data = {"LIST_OF_TASKS": list_of_tasks, "ORDERING_TEST_DATA": ordering_test_data}

# ===============================================================================
# ===============================  Запись в файл  ===============================
# ===============================================================================

data_dir = os.path.join(ROOT_DIR, "test_data")
output_file = os.path.join(data_dir, "test_data_store.py")

with open(output_file, mode="w", encoding="utf-8") as f:
    f.write("# ====================================================================\n")
    f.write("# ЭТОТ ФАЙЛ СГЕНЕРИРОВАН АВТОМАТИЧЕСКИ ИЗ ТАБЛИЦ.\n")
    f.write("# НЕ ПРАВЬТЕ ЕГО РУКАМИ! ДЛЯ ОБНОВЛЕНИЯ ЗАПУСТИТЕ СКРИПТ ГЕНЕРАЦИИ.\n")
    f.write("# ====================================================================\n\n")

    for key, value in dict_data.items():
        f.write(f"{key} = [\n")
        for item in value:
            f.write(f"\t{item},\n")
        f.write(f"]\n\n")
