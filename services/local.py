import os.path
import shutil

from misc.consts import LOCAL


def copy_local(src: str, dest: str, override: bool = False) -> None:
    """
    Копирование файла в локальную директорию
    :param src: Путь к файлу который копируется
    :param dest: Путь куда копировать
    :param override: Разрешение на перезапись файла
    :return:
    """
    if not os.path.exists(dest) or override:
        print(f'[INFO] Выполняется копирование файла в локальную директорию: {LOCAL}...')
        try:
            shutil.copy2(src, dest)
        except FileNotFoundError:
            print(f'[ERR] Файл не найден {src}')
        except IsADirectoryError:
            print(f'[ERR] Каталог не найден {dest}')
        else:
            print(f'[INFO] Файл {src} успешно скопирован в {dest}')
    elif os.path.exists(src) and not override:
        print(f'[INFO] Файл не скопирован, т.к. отключена перезапись')
