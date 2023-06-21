from . import *
from argparse import Namespace


data = {
    'args': Namespace(dry=False, override=True),
    'paths': [
        'data/file1.txt',
        'data/file2.txt',
        'data/file3.txt'
    ]
}


def test_start_delivery_by_ftp():
    start_delivery('ftp', data)
    ftp = DeliveryFTP('ftp', **data)
    ftp._connection = create_connection('ftp')
    for path in data['paths']:
        ftp._filename = path.split('/')[-1]
        assert ftp._exist_file() is True


def test_start_delivery_by_owncloud():
    start_delivery('owncloud', data)
    owncoud = DeliveryOwncloud('owncloud', **data)
    owncoud._connection = create_connection('owncloud')
    for path in data['paths']:
        owncoud._filename = path.split('/')[-1]
        assert owncoud._exist_file() is True


def test_start_delivery_by_folder():
    start_delivery('folder', data)
    folder = DeliveryFolder('folder', **data)
    for path in data['paths']:
        folder._filename = path.split('/')[-1]
        assert folder._exist_file() is True
