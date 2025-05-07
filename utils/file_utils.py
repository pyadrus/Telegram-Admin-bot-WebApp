import json


def read_json_file(file_path):
    """
    Чтение файла с настройками
    :return:
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
