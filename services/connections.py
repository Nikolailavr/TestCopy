from abc import ABC, abstractmethod
from ftplib import FTP
from owncloud import Client

from misc.consts import FTP_HOST, FTP_USER, FTP_PASS, \
    OwnCloud_URL, OwnCloud_Token, OwnCloud_Passwd
from misc.functions import logger


class Connection(ABC):
    """Создание подключения"""
    def __init__(self, name: str, **kwargs):
        self.session = None
        try:
            self._connect()
        except ConnectionError:
            logger.error(f'[{name}] Нет соединения с сервером')
        except Exception as ex:
            logger.error(f'[{name}] {ex}')  # Для отладки
            exit(0)

    @abstractmethod
    def _connect(self):
        ...

    @abstractmethod
    def close(self):
        ...


class ConnectionFTP(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _connect(self):
        """
        Создание подключения по FTP
        """
        self.session = FTP()
        self.session.connect(FTP_HOST)
        self.session.login(FTP_USER, FTP_PASS)

    def close(self):
        self.session.close()


class ConnectionOwnCloud(Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _connect(self):
        """
        Создание подключения OwnCloud
        """
        self.session = Client(url=OwnCloud_URL)
        self.session.anon_login(OwnCloud_Token, OwnCloud_Passwd)

    def close(self):
        self.session.logout()


def create_connection(name: str, *args, **kwargs) -> Connection | None:
    """Выбор соединения"""
    match name:
        case 'ftp':
            return ConnectionFTP(name, *args, **kwargs)
        case 'owncloud':
            return ConnectionOwnCloud(name, *args, **kwargs)
