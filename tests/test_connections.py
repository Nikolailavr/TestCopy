from . import *


def test_create_connections():
    message = 'Несоотетствие типов'
    assert type(create_connection('ftp')) is ConnectionFTP, message
    assert type(create_connection('owncloud')) is ConnectionOwnCloud, message
    assert create_connection('temp') is None, message
    assert create_connection('') is None, message
