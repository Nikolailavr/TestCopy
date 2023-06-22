import os.path
import shutil
from abc import ABC, abstractmethod
from argparse import Namespace

from misc.consts import LOCAL
from misc.functions import logger, get_file_name
from services.connections import create_connection


class Delivery(ABC):
    """Метод доставки"""
    def __init__(self, name: str, **kwargs: dict):
        self._args = kwargs.get('args', Namespace(dry=False, override=False))
        self.paths = kwargs.get('paths', [])
        self._name = name
        self._filename = None
        self._connection = None

    def start_copy(self):
        """Старт копирования файлов"""
        if len(self.paths):
            self._connection = create_connection(self._name)
            for path in self.paths:
                self._copy(path)
            if self._connection:
                self._connection.close()

    def _copy(self, path: str):
        """Копирование файла"""
        self._filename = get_file_name(path)
        file_exist = self._exist_file()
        if self._args.dry:
            logger.info(f'[{self._name}] Здесь могло быть копирование файла '
                        f'{self._filename}')
        elif (not file_exist or self._args.override) and \
                not self._args.dry:
            try:
                logger.info(f'[{self._name}] Выполняется копирование '
                            f'{self._filename}')
                result = self._send_file(path)
            except FileNotFoundError:
                logger.error(f'[{self._name}] Файл не найден {path}')
            except IsADirectoryError:
                logger.error(f'[{self._name}] Каталог не найден')
            else:
                if result:
                    logger.info(f'[{self._name}] Файл {path} успешно '
                                f'скопирован')
                else:
                    logger.warning(f'[{self._name}] Возникли неполадки')
        elif file_exist and not self._args.override:
            logger.info(f'[{self._name}] Файл не скопирован, т.к. отключена '
                        f'перезапись')

    @abstractmethod
    def _exist_file(self):
        """Флаг существования файла"""
        ...

    @abstractmethod
    def _send_file(self, path: str):
        """Отправка файла"""
        ...


class DeliveryFTP(Delivery):
    """Доставка по FTP"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _exist_file(self) -> bool | None:
        """
        Проверка на наличие файла на сервере
        """
        filelist = []
        try:
            self._connection.session.retrlines('NLST', filelist.append)
        except Exception as ex:
            logger.error(f'Соединение разорвано :{ex}')
        else:
            for file in filelist:
                if self._filename in file:
                    return True

    def _send_file(self, path: str) -> bool | None:
        """
        Копирование файла на сервер через ftp
        """
        with open(path, 'rb') as file:
            result = self._connection.session.storbinary(
                f'STOR {self._filename}',
                file
            )
        if result.startswith('226'):
            return True
        else:
            logger.warning(f'Возможно файл не скопирован. Ответ от сервера: '
                           f'{result}')


class DeliveryOwncloud(Delivery):
    """Доставка через OwnCloud"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _exist_file(self) -> bool | None:
        for file in self._connection.session.list(path=''):
            if self._filename == file.name:
                return True

    def _send_file(self, path: str):
        self._connection.session.put_file(self._filename, path)
        return True


class DeliveryFolder(Delivery):
    """Локальный метод доставки"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._destination = None
        if not os.path.exists(LOCAL):
            os.mkdir(LOCAL)

    def _exist_file(self) -> bool | None:
        self._destination = LOCAL + '/' if not LOCAL.endswith('/') else LOCAL
        self._destination += self._filename
        return os.path.exists(self._destination)

    def _send_file(self, path: str) -> bool | None:
        shutil.copy2(path, self._destination)
        return True


def start_delivery(method: str, kwargs: dict):
    """Выбор метода доставки"""
    match method:
        case "ftp":
            DeliveryFTP(method, **kwargs).start_copy()
        case "owncloud":
            DeliveryOwncloud(method, **kwargs).start_copy()
        case "folder":
            DeliveryFolder(method, **kwargs).start_copy()
