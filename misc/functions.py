import argparse
import datetime
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
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except IsADirectoryError:
        logger.error(f'[ERR] Необходим полный путь до файла')
        exit(0)
    except FileNotFoundError:
        logger.error(f'[ERR] Файл не найден')
        exit(0)
    except json.decoder.JSONDecodeError:
        logger.error(f'[ERR] Файл пустой или не json')
        exit(0)
    except Exception as ex:
        logger.error(ex)
        exit(0)


def parse_args() -> argparse.Namespace:
    """
    Получение атрибутов запуска
    :return: простое строковое представление
    """
    parser = argparse.ArgumentParser(
        prog='TestCopy',
        description='Копирование файлов до конечных директорий')
    parser.add_argument('path', help='Путь до файлов')
    parser.add_argument('-o', '--override', action='store_true', help='Разрешить перезапись файлов')
    parser.add_argument('-d', '--dry', action='store_true', help='Запуск в "сухом" режиме')
    texttmp = '1 - Пробег по каждому файлу; 2 - Пробег по всем файлам а после уже копирование'
    parser.add_argument('-m', '--method', action='store_true', help=texttmp)
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


def check_env():
    """
    Checkin .env
    """
    if not all([consts.FTP_USER, consts.FTP_PASS, consts.OwnCloud_URL, consts.OwnCloud_Passwd]):
        print('Set params in .env')
        exit(0)


def timer(func):
    """
    Декоратор для посчета времени работы
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        print(f'Время выполения программы {datetime.datetime.now() - start} сек')
        return result
    return wrapper

