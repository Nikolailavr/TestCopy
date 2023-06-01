from ftplib import FTP

from misc.consts import FTP_HOST, FTP_USER, FTP_PASS
from misc.functions import logger


class FTPClient:
    def __init__(self):
        self._session = None
        self._filename = None

    def _connect(self) -> bool | None:
        """
        Создание подключения по FTP
        :return: True при успешном соединении
        """
        self._session = FTP()
        try:
            self._session.connect(FTP_HOST)
            self._session.login(FTP_USER, FTP_PASS)
        except Exception as ex:
            self._session.close()
            logger.error(f'Нет соединения с сервером {FTP_HOST}')
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
                logger.info(f'Выполняю копирование файла {self._filename} по ftp')
                try:
                    with open(path, 'rb') as file:
                        result = self._session.storbinary(f'STOR {self._filename}', file)
                except FileNotFoundError:
                    logger.error(f'Файл {self._filename} не найден')
                except ConnectionRefusedError:
                    logger.error(f'Соединение разорвано')
                except Exception as ex:
                    logger.error('Не удалось отправить файл :(')
                    raise ex  # Для отладки
                else:
                    if result.startswith('226'):
                        logger.info(f'Файл {self._filename} успешно скопирован на {FTP_HOST}')
                    else:
                        logger.warning(f'Возможно файл не скопирован. Ответ от сервера: {result}')
                finally:
                    self._session.close()
            elif file_exists and not override:
                logger.info(f'Файл не скопирован, т.к. отключена перезапись')

    def _exists_file(self, filename: str) -> bool | None:
        """
        Проверка на наличие файла на сервере
        :param filename: Имя файла
        """
        filelist = []
        try:
            self._session.retrlines('NLST', filelist.append)
        except Exception as ex:
            logger.error(f'Соединение разорвано :{ex}')
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
