import os.path
import shutil

from misc.functions import logger, get_file_name
from misc.consts import LOCAL


def copy_local(path: str, args) -> None:
    """
    Копирование файла в локальную директорию
    :param path: Путь к файлу который копируется
    :param dest: Путь куда копировать
    :param override: Разрешение на перезапись файла
    :return:
    """
    dest = LOCAL + '/' if not LOCAL.endswith('/') else LOCAL
    dest += get_file_name(path)
    if args.dry:
        logger.info(f'Здесь могло быть копирование файла {path} в {dest}')
    else:
        file_exists = os.path.exists(dest)
        if not file_exists or args.override:
            logger.info(f'Выполняется копирование файла {path} в {dest}')
            try:
                shutil.copy2(path, dest)
            except FileNotFoundError:
                logger.error(f'Файл не найден {path}')
            except IsADirectoryError:
                logger.error(f'Каталог не найден {dest}')
            else:
                logger.info(f'Файл {path} успешно скопирован в {dest}')
        elif file_exists and not args.override:
            logger.info(f'Файл не скопирован, т.к. отключена перезапись')
