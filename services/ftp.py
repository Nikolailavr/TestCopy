from ftplib import FTP

from misc.consts import FTP_HOST, FTP_USER, FTP_PASS


class FTPClient:
    def __init__(self):
        self._session = None
        self._filename = None

    def _connect(self) -> bool | None:
        """
        Создание подключения по FTP
        :return: True при успешном соединении
        """
        try:
            self._session = FTP(host=FTP_HOST, user=FTP_USER, passwd=FTP_PASS)
        except Exception as ex:
            self._session.close()
            print(f'[ERR] Нет соединения с сервером {FTP_HOST}')
            raise ex
        else:
            return True

    def copy(self, path: str, override: bool = False) -> None:
        """
        Копирование файла на сервер через ftp
        :param path: Путь до файла
        :param override: Разрешение на перезапись файла
        :return:
        """
        self._get_file_name(path)
        if self._connect():
            file_exists = self._exists_file(self._filename)
            if not file_exists or override:
                print(f'[INFO] Выполняю копирование файла {path} по ftp...')
                try:
                    with open(path, 'rb') as file:
                        self._session.storbinary(f'STOR {self._filename}', file)
                except FileNotFoundError:
                    print(f'[ERR] Файл {path} не найден')
                except ConnectionRefusedError:
                    print(f'[ERR] Соединение разорвано')
                except Exception as ex:
                    print('[ERR] Не удалось отправить файл :(')
                    raise ex  # Для отладки
                else:
                    print(f'[INFO] Файл {path} успешно скопирован на {FTP_HOST}')
                finally:
                    self._session.close()
            elif file_exists and not override:
                print(f'[INFO] Файл не скопирован, т.к. отключена перезапись')

    def _exists_file(self, filename: str) -> bool | None:
        """
        Проверка на наличие файла на сервере
        :param filename: Имя файла
        """
        filelist = []
        try:
            # self._session.retrlines('LIST', filelist.append)
            result = self._session.retrlines(f'RETR {filename}', print)
        except Exception as ex:
            print(f'[ERR] Соединение разорвано')
        else:
            for file in filelist:
                if filename in file:
                    return True

    def _get_file_name(self, path: str) -> None:
        """
        Получаем имя файла из полного пути
        :param path: Путь до файла
        """
        pos = path.rfind('/')
        if pos != -1:
            self._filename = path[pos + 1:]
        else:
            self._filename = path
