import os.path
import shutil
from abc import ABC, abstractmethod
from argparse import Namespace

from misc.consts import LOCAL
from misc.functions import logger, get_file_name
from services.connections import create_connect


class Deliver(ABC):
    def __init__(self, name: str, **kwargs: dict):
        self._args = kwargs.get('args', Namespace(dry=False, override=False))
        self.paths = kwargs.get('paths', [])
        self._name = name
        self._filename = None
        self._file_exist = None
        self._destination = None
        self._connection = None

    def start_copy(self):
        if len(self.paths):
            self._connection = create_connect(self._name)
            for path in self.paths:
                self.copy(path)
            if self._connection:
                self._connection.close()

    def copy(self, path: str):
        self._filename = get_file_name(path)
        self._file_exist = self.exist_file()
        if self._args.dry:
            logger.info(f'[{self._name}] Здесь могло быть копирование файла '
                        f'{self._filename}')
        elif (not self._file_exist or self._args.override) and \
                not self._args.dry:
            try:
                logger.info(f'[{self._name}] Выполняется копирование '
                            f'{self._filename}')
                result = self.send_file(path)
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
        elif self._file_exist and not self._args.override:
            logger.info(f'[{self._name}] Файл не скопирован, т.к. отключена '
                        f'перезапись')

    @abstractmethod
    def exist_file(self):
        ...

    @abstractmethod
    def send_file(self, path: str):
        ...


class DeliverFTP(Deliver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def exist_file(self) -> bool | None:
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

    def send_file(self, path: str) -> bool | None:
        """
        Копирование файла на сервер через ftp
        """
        with open(path, 'rb') as file:
            result = self._connection.session.storbinary(f'STOR {self._filename}', file)
        if result.startswith('226'):
            return True
        else:
            logger.warning(f'Возможно файл не скопирован. Ответ от сервера: '
                           f'{result}')


class DeliverOwncloud(Deliver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def exist_file(self) -> bool | None:
        for file in self._connection.session.list(path=''):
            if self._filename == file.name:
                return True

    def send_file(self, path: str):
        self._connection.session.copy(path, self._filename)
        return True


class DeliverFolder(Deliver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def exist_file(self) -> bool | None:
        self._destination = LOCAL + '/' if not LOCAL.endswith('/') else LOCAL
        self._destination += self._filename
        return os.path.exists(self._destination)

    def send_file(self, path: str) -> bool | None:
        shutil.copy2(path, self._destination)
        return True


def start_delivery(method: str, kwargs: dict):
    match method:
        case "ftp":
            DeliverFTP(method, **kwargs).start_copy()
        case "owncloud":
            DeliverOwncloud(method, **kwargs).start_copy()
        case "folder":
            DeliverFolder(method, **kwargs).start_copy()
