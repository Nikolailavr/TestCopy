import argparse
import json
import os
from pathlib import Path
from loguru import logger

import misc.consts as consts

path_parent = Path(__file__).parent.parent

logger.add(
    Path().joinpath(f"{path_parent}/logs/log.json"),
    format="{time} | {level} | {message}",
    level="INFO",
    serialize=True,
    rotation="1 day",
    compression="zip"
)

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
        raise ex  # Для отладки
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


def get_file_name(path: str) -> str:
    """
    Получаем имя файла из полного пути
    :param path: Путь до файла
    :return Имя файла
    """
    pos = path.rfind('/')
    if pos != -1:
        return path[pos + 1:]
    else:
        return path
