import requests
import urllib3

from misc.consts import OwnCloud_URL, OwnCloud_Passwd


class OwnCLoudClient:

    def __init__(self):
        """
        Instantiates a client
        """
        url = urllib3.util.parse_url(OwnCloud_URL)
        self._url_osn = f'{url.scheme}://{url.host}/owncloud/'
        self._url = OwnCloud_URL
        self._session = None
        self._token = None
        self._passwd = OwnCloud_Passwd
        self._url_upload = self._url_osn + 'public.php/webdav/'

    def _connect(self) -> bool | None:
        try:
            self._session = requests.session()
            self._token = self._get_token()
            print(self._token)
            return self._anon_login()
        except Exception as ex:
            print(f'[ERR] {ex}')
            raise ex

    def _anon_login(self) -> bool | None:
        # self._session.auth = (self._token, OwnCloud_Passwd)
        payload = {
            'password': OwnCloud_Passwd,
            'requesttoken': self._token
        }
        try:
            response = self._session.post(self._url + 'authenticate', data=payload)
            print(response.text)
        except Exception as ex:
            self._session.close()
            print(f'[ERR] Неудачная попытка аутентификации')
            print(f'[ERR] {ex}')
        else:
            if response.ok:
                print(f'[INFO] Успешная авторизация')
                return True

    def copy(self, path: str):
        try:
            if self._connect():
                with open(path, 'rb') as file:
                    files = {'file': file}
                    try:
                        response = self._session.post(self._url_upload, files=files)
                    except Exception as ex:
                        raise ex
                    else:
                        if response.ok:
                            print(f'[INFO] Файл {path} успешно загружен на сервер')
            else:
                print(f'[ERR] Неудачная попытка соединения')
        except Exception as ex:
            print(f'[ERR] {ex}')
        finally:
            self._session.close()

    def _get_token(self) -> str:
        try:
            response = self._session.get(self._url)
            find_text = 'data-requesttoken='
            pos_1 = response.text.find(find_text)
            pos_1 = response.text.find('"', pos_1) + 1
            pos_2 = response.text.find('"', pos_1)
            return response.text[pos_1:pos_2].replace(find_text, '')
        except Exception as ex:
            print(f'[ERR] {ex}')
            raise ex


def copy_owncloud(path: str) -> None:
    with open(path, 'rb') as file:
        try:
            files = {'file': file}
            with requests.Session() as session:
                first_resp = session.get(OwnCloud_URL)
                find_text = 'data-requesttoken='
                pos_1 = first_resp.text.find(find_text)
                pos_1 = first_resp.text.find('"', pos_1) + 1
                pos_2 = first_resp.text.find('"', pos_1)
                request_token = first_resp.text[pos_1:pos_2].replace(find_text, '')
                payload = {
                    'password': OwnCloud_Passwd,
                    'requesttoken': request_token
                }
                upload = session.post(f'{OwnCloud_URL}/authenticate', data=payload, files=files)
                # upload = session.put(OC_URL, files=files)
        except ConnectionError:
            print(f'[ERR] Не удалось соединиться с сервером {OwnCloud_URL}')
        except Exception as ex:
            raise ex
        else:
            print(upload.status_code)
            if upload.ok:
                print(f'[INFO] Файл {path} успешно скопирован на сервер {OwnCloud_URL}')
            else:
                print(f'[ERR] Не удалось отправить файл на сервер {OwnCloud_URL} (status code={upload.status_code})')
