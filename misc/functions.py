import argparse
import os
from pathlib import Path
import json

import misc.consts as consts

path_parent = Path(__file__).parent.parent

if not os.path.exists(consts.LOCAL):
    os.mkdir(consts.LOCAL)


def read_json(path: str) -> dict:
    """
    Чтение данных из json файла
    :param path: Путь до файла
    :return: Словарь с данными из файла
    """
    result = dict()
    try:
        with open(path, 'r', encoding='utf-8') as file:
            result = json.load(file)
    except IsADirectoryError:
        raise IsADirectoryError(f'[ERR] Необходим полный путь до файла')
    except FileNotFoundError:
        raise FileNotFoundError(f'[ERR] Файл не найден')
    except Exception as ex:
        raise ex               # Для отладки
    return result


def parse_args() -> argparse.Namespace:
    """
    Получение атрибутов запуска
    :return: простое строковое представление
    """
    parser = argparse.ArgumentParser(
                        prog='TestCopy',
                        description='Copy files to endpoints')
    parser.add_argument('path')
    parser.add_argument('-o', '--override', action='store_true', help='Разрешить перезапись файлов')
    parser.add_argument('-d', '--dry', action='store_true', help='Запуск в "сухом режиме"')
    return parser.parse_args()
