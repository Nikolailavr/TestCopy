import shutil

from services.consts import LOCAL


def copy_local(src: str, dest: str) -> None:
    """

    :param src: Путь к файлу который копируется
    :param dest: Путь куда копировать
    :return:
    """
    print(f'[INFO] Выполняется копирование файла в локальную директорию: {LOCAL}...')
    try:
        shutil.copy2(src, dest)
    except FileNotFoundError:
        print(f'[ERR] Файл не найден {src}')
    except IsADirectoryError:
        print(f'[ERR] Каталог не найден {dest}')
    else:
        print(f'[INFO] Файл {src} успешно скопирован в {dest}')
