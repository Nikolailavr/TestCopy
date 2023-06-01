from ftplib import FTP

from services.consts import FTP_HOST, FTP_USER, FTP_PASS


def copy_ftp(path: str) -> None:
    """
    Копирование файла на сервер через ftp
    :param path: Путь до файла
    :return:
    """
    print(f'[INFO] Выполняю копирование файла {path} по ftp...')
    try:
        with FTP(host=FTP_HOST, user=FTP_USER, passwd=FTP_PASS) as ftp:
            with open(path, 'rb') as file:
                ftp.storbinary(f'STOR {path}', file)
    except FileNotFoundError:
        print(f'[ERR] Файл {path} не найден')
    except ConnectionRefusedError:
        print(f'[ERR] Нет соединения с сервером {FTP_HOST}')
    except Exception as ex:
        print('[ERR] Не удалось отправить файл :(')
        raise ex                                    # Для отладки
    else:
        print(f'[INFO] Файл {path} успешно скопирован на {FTP_HOST}')
