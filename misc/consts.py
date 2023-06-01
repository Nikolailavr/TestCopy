import os
from dotenv import load_dotenv


load_dotenv('misc/.env')

# FTP
# FTP_HOST = 'ftp.automiq.ru'
# FTP_USER = os.getenv('FTP_USER')
# FTP_PASS = os.getenv('FTP_PASSWD')
FTP_HOST = '172.16.120.155'
FTP_USER = 'user'
FTP_PASS = 'user123'

# OwnCloud
OwnCloud_URL = os.getenv('OWNCLOUD_URL')
OwnCloud_Passwd = os.getenv('OWNCLOUD_PASSWD')

# Local
LOCAL = '/tmp/test-230531'

# json
JSON_TO_COPY = 'data.json'
