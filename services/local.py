import os.path
import shutil

from misc.functions import logger


def copy_local(src: str, dest: str, override: bool = False) -> None:
    """
    Копирование файла в локальную директорию
    :param src: Путь к файлу который копируется
    :param dest: Путь куда копировать
    :param override: Разрешение на перезапись файла
    :return:
    """
    file_exists = os.path.exists(dest)
    if not file_exists or override:
        logger.info(f'Выполняется копирование файла {src} в {dest}')
        try:
            shutil.copy2(src, dest)
        except FileNotFoundError:
            logger.error(f'Файл не найден {src}')
        except IsADirectoryError:
            logger.error(f'Каталог не найден {dest}')
        else:
            logger.info(f'Файл {src} успешно скопирован в {dest}')
    elif file_exists and not override:
        logger.info(f'Файл не скопирован, т.к. отключена перезапись')
