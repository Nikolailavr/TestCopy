import os
from dotenv import load_dotenv


load_dotenv('misc/.env')

# FTP
FTP_HOST = 'ftp.automiq.ru'
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASSWD')

# OwnCloud
OwnCloud_URL = os.getenv('OWNCLOUD_URL')
OwnCloud_Passwd = os.getenv('OWNCLOUD_PASSWD')

# Local
LOCAL = '/tmp/test-230531'

# json
JSON_TO_COPY = 'data.json'
