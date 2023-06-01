import os
from dotenv import load_env

load_env('misc/.env')


# FTP
FTP_HOST = 'ftp.automiq.ru'
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASSWD')

# OwnCloud
OC_URL = os.getenv('OWNCLOUD_URL')
OC_PASS = os.getenv('OWNCLOUD_PASSWD')

# Local
LOCAL = '/tmp/test-230531/'

# json
JSON_TO_COPY = 'data.json'
