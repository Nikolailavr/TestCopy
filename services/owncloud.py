import requests
from requests.auth import HTTPBasicAuth

from services.consts import OC_URL, OC_PASS


class Client:

    def __init__(self, url, **kwargs):
        """Instantiates a client

        :param url: URL of the target ownCloud instance
        :param verify_certs: True (default) to verify SSL certificates, False otherwise
        :param dav_endpoint_version: None (default) to force using a specific endpoint version
        instead of relying on capabilities
        :param debug: set to True to print debugging messages to stdout, defaults to False
        """
        if not url.endswith('/'):
            url += '/'

        self.url = url
        self._session = None
        self._debug = kwargs.get('debug', False)
        self._verify_certs = kwargs.get('verify_certs', True)
        self._dav_endpoint_version = kwargs.get('dav_endpoint_version', True)

        self._capabilities = None
        self._version = None
        self._davpath = None
        self._webdav_url = None

    def login(self, user_id, password):
        """Authenticate to ownCloud.
        This will create a session on the server.

        :param user_id: user id
        :param password: password
        :raises: HTTPResponseError in case an HTTP error status was returned
        """

        self._session = requests.session()
        self._session.verify = self._verify_certs
        self._session.auth = (user_id, password)

        try:
            self._update_capabilities()

            url_components = self.url
            if self._dav_endpoint_version == 1:
                self._davpath = url_components.path + 'remote.php/dav/files/' + parse.quote(user_id)
                self._webdav_url = self.url + 'remote.php/dav/files/' + parse.quote(user_id)
            else:
                self._davpath = url_components.path + 'remote.php/webdav'
                self._webdav_url = self.url + 'remote.php/webdav'

        except Exception as e:
            self._session.close()
            self._session = None
            raise e

    def logout(self) -> True:
        """
        Log out the authenticated user and close the session.
        :returns: True if the operation succeeded
        """
        self._session.close()
        return True

    def anon_login(self, folder_token, folder_password=''):
        self._session = requests.session()
        self._session.verify = self._verify_certs
        self._session.auth = (folder_token, folder_password)
        self._davpath = self.url + 'public.php/webdav'
        self._webdav_url = self.url + 'public.php/webdav'

    def _update_capabilities(self):
        res = self._make_ocs_request(
            'GET',
            self.OCS_SERVICE_CLOUD,
            'capabilities'
        )
        if res.status_code == 200:
            tree = ET.fromstring(res.content)
            self._check_ocs_status(tree)

            data_el = tree.find('data')
            apps = {}
            for app_el in data_el.find('capabilities'):
                app_caps = {}
                for cap_el in app_el:
                    app_caps[cap_el.tag] = cap_el.text
                apps[app_el.tag] = app_caps

            self._capabilities = apps

            version_el = data_el.find('version/string')
            edition_el = data_el.find('version/edition')
            self._version = version_el.text
            if edition_el.text is not None:
                self._version += '-' + edition_el.text

            if 'dav' in apps and 'chunking' in apps['dav']:
                chunking_version = float(apps['dav']['chunking'])
                if self._dav_endpoint_version > chunking_version:
                    self._dav_endpoint_version = None

                if self._dav_endpoint_version is None and chunking_version >= 1.0:
                    self._dav_endpoint_version = 1
                else:
                    self._dav_endpoint_version = 0

            return self._capabilities



def copy_owncloud(path: str) -> None:
    with open(path, 'rb') as file:
        try:
            files = {'file': file}
            with requests.Session() as session:
                first_resp = session.get(OC_URL)
                find_text = 'data-requesttoken='
                pos_1 = first_resp.text.find(find_text)
                pos_1 = first_resp.text.find('"', pos_1) + 1
                pos_2 = first_resp.text.find('"', pos_1)
                request_token = first_resp.text[pos_1:pos_2].replace(find_text, '')
                payload = {
                    'password': OC_PASS,
                    'requesttoken': request_token
                }
                upload = session.post(f'{OC_URL}/authenticate', data=payload, files=files)
                # upload = session.put(OC_URL, files=files)
        except ConnectionError:
            print(f'[ERR] Не удалось соединиться с сервером {OC_URL}')
        except Exception as ex:
            raise ex
        else:
            print(upload.status_code)
            if upload.ok:
                print(f'[INFO] Файл {path} успешно скопирован на сервер {OC_URL}')
            else:
                print(f'[ERR] Не удалось отправить файл на сервер {OC_URL} (status code={upload.status_code})')
