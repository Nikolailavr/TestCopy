import datetime
import math
import os
import time
import requests
import urllib3
import xml.etree.ElementTree as ET
from six.moves.urllib import parse

from misc.consts import OwnCloud_URL, OwnCloud_Passwd
from misc.functions import logger, get_file_name


class ResponseError(Exception):
    def __init__(self, res, errorType):
        if type(res) is int:
            code = res
        else:
            code = res.status_code
            self.res = res
        Exception.__init__(self, errorType + " error: %i" % code)
        self.status_code = code


class HTTPResponseError(ResponseError):
    def __init__(self, res):
        ResponseError.__init__(self, res, "HTTP")


class FileInfo(object):
    """File information"""

    _DATE_FORMAT = '%a, %d %b %Y %H:%M:%S %Z'

    def __init__(self, path, file_type='file', attributes=None):
        self.path = path
        if path.endswith('/'):
            path = path[0:-1]
        self.name = os.path.basename(path)
        self.file_type = file_type
        self.attributes = attributes or {}

    def get_name(self):
        """Returns the base name of the file without path

        :returns: name of the file
        """
        return self.name

    def get_path(self):
        """Returns the full path to the file without name and without
        trailing slash

        :returns: path to the file
        """
        return os.path.dirname(self.path)

    def get_size(self):
        """Returns the size of the file

        :returns: size of the file
        """
        if '{DAV:}getcontentlength' in self.attributes:
            return int(self.attributes['{DAV:}getcontentlength'])
        return None

    def get_etag(self):
        """Returns the file etag

        :returns: file etag
        """
        return self.attributes['{DAV:}getetag']

    def get_content_type(self):
        """Returns the file content type

        :returns: file content type
        """
        if '{DAV:}getcontenttype' in self.attributes:
            return self.attributes['{DAV:}getcontenttype']

        if self.is_dir():
            return 'httpd/unix-directory'

        return None

    def get_last_modified(self):
        """Returns the last modified time

        :returns: last modified time
        :rtype: datetime object
        """
        return datetime.datetime.strptime(
            self.attributes['{DAV:}getlastmodified'],
            self._DATE_FORMAT
        )

    def is_dir(self):
        """Returns whether the file info is a directory

        :returns: True if it is a directory, False otherwise
        """
        return self.file_type != 'file'

    def __str__(self):
        return 'File(path=%s,file_type=%s,attributes=%s)' % \
            (self.path, self.file_type, self.attributes)

    def __repr__(self):
        return self.__str__()


class OwnCLoudClient:
    def __init__(self):
        url = urllib3.util.parse_url(OwnCloud_URL)
        self._url_osn = f'{url.scheme}://{url.host}/owncloud/'
        self._url = OwnCloud_URL
        self._session = None
        self._token = url.path.split("/")[-1]
        self._passwd = OwnCloud_Passwd
        self._url_upload = self._url_osn + 'public.php/webdav/'

    def _connect(self) -> None:
        """Создание подключения и авторизация"""
        self._session = requests.session()
        self._session.verify = True
        self._session.auth = (self._token, OwnCloud_Passwd)

    def copy(self, path: str, args, **kwargs):
        """
        Копирование файлов на сервер
        :param path: путь до файла
        :param args: аргументы запуска
        :param kwargs: optional arguments
        :return:
        """
        remote_path = get_file_name(path)
        self._connect()
        files = self._list(remote_path)
        filenames = []
        for file in files:
            filenames.append(file.name)
        file_exists = get_file_name(path) in filenames
        if (not file_exists or args.override) and not args.dry:
            logger.info(f'Выполняется копирование файла {remote_path} на сервер {self._url_osn}')
            if self._put_file(remote_path, path, **kwargs):
                logger.info(f'Файл {remote_path} успешно загружен на сервер')
            else:
                logger.error(f"Не удалось загрузить файл")
            self._session.close()
        elif args.dry:
            logger.info(f'Здесь могло быть копирование файла {remote_path} на сервер {self._url_osn}')
        elif file_exists and not args.override:
            logger.info(f'Файл не скопирован, т.к. отключена перезапись')

    def _list(self, path, depth=1, properties=None) -> list | None:
        """Returns the listing/contents of the given remote directory

        :param path: path to the remote directory
        :param depth: depth of the listing, integer or "infinity"
        :param properties: a list of properties to request (optional)
        :returns: directory listing
        :rtype: array of :class:`FileInfo` objects
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        if not path.endswith('/'):
            path += '/'

        headers = {}
        if isinstance(depth, int) or depth == "infinity":
            headers['Depth'] = str(depth)

        if properties:
            root = ET.Element('d:propfind',
                              {
                                  'xmlns:d': "DAV:",
                                  'xmlns:nc': "http://nextcloud.org/ns",
                                  'xmlns:oc': "http://owncloud.org/ns"
                              })
            prop = ET.SubElement(root, 'd:prop')
            for p in properties:
                ET.SubElement(prop, p)
            data = ET.tostring(root)
        else:
            data = None

        res = self._make_dav_request('PROPFIND', path, headers=headers, data=data)
        # first one is always the root, remove it from listing
        if res:
            return res[1:]
        return None

    def _put_file(self, remote_path, local_source_file, **kwargs):
        """
        Uploads a file using chunks. If the file is smaller than
        ``chunk_size`` it will be uploaded directly.
        :param remote_path: path to the target file. A target directory can
        also be specified instead by appending a "/"
        :param local_source_file: path to the local file to upload
        :param \*\*kwargs: optional arguments
        :returns: True if the operation succeeded, False otherwise
        :raises: HTTPResponseError in case an HTTP error status was returned
        """
        chunk_size = kwargs.get('chunk_size', 10 * 1024 * 1024)
        result = True
        transfer_id = int(time.time())

        remote_path = self._normalize_path(remote_path)
        if remote_path.endswith('/'):
            remote_path += os.path.basename(local_source_file)

        stat_result = os.stat(local_source_file)

        file_handle = open(local_source_file, 'rb', 8192)
        file_handle.seek(0, os.SEEK_END)
        size = file_handle.tell()
        file_handle.seek(0)

        headers = {}
        if kwargs.get('keep_mtime', True):
            headers['X-OC-MTIME'] = str(int(stat_result.st_mtime))

        if size == 0:
            return self._make_dav_request(
                'PUT',
                remote_path,
                data='',
                headers=headers
            )

        chunk_count = int(math.ceil(float(size) / float(chunk_size)))

        if chunk_count > 1:
            headers['OC-CHUNKED'] = '1'

        for chunk_index in range(0, int(chunk_count)):
            data = file_handle.read(chunk_size)
            if chunk_count > 1:
                chunk_name = '%s-chunking-%s-%i-%i' % \
                             (remote_path, transfer_id, chunk_count,
                              chunk_index)
            else:
                chunk_name = remote_path

            if not self._make_dav_request(
                    'PUT',
                    chunk_name,
                    data=data,
                    headers=headers
            ):
                result = False
                break

        file_handle.close()
        return result

    def _make_dav_request(self, method, path, **kwargs):
        """
        Makes a WebDAV request
        :param method: HTTP method
        :param path: remote path of the targetted file
        :param \*\*kwargs: optional arguments that ``requests.Request.request`` accepts
        :returns array of :class:`FileInfo` if the response
        contains it, or True if the operation succeded, False
        if it didn't
        """
        filename = get_file_name(path)
        res = self._session.request(
            method,
            self._url_upload + filename,
            **kwargs
        )
        if res.status_code in [200, 207]:
            return self._parse_dav_response(res)
        if res.status_code in [204, 201]:
            return True
        raise HTTPResponseError(res)

    def _parse_dav_response(self, res):
        """Parses the DAV responses from a multi-status response

        :param res: DAV response
        :returns array of :class:`FileInfo` or False if
        the operation did not succeed
        """
        if res.status_code == 207:
            tree = ET.fromstring(res.content)
            items = []
            for child in tree:
                items.append(self._parse_dav_element(child))
            return items
        return False

    def _parse_dav_element(self, dav_response):
        """Parses a single DAV element

        :param dav_response: DAV response
        :returns :class:`FileInfo`
        """
        href = parse.unquote(
            self._strip_dav_path(dav_response.find('{DAV:}href').text)
        )

        file_type = 'file'
        if href[-1] == '/':
            file_type = 'dir'

        file_attrs = {}
        attrs = dav_response.find('{DAV:}propstat')
        attrs = attrs.find('{DAV:}prop')
        for attr in attrs:
            file_attrs[attr.tag] = attr.text

        return FileInfo(href, file_type, file_attrs)

    def _strip_dav_path(self, path):
        """Removes the leading "remote.php/webdav" path from the given path

        :param path: path containing the remote DAV path "remote.php/webdav"
        :returns: path stripped of the remote DAV path
        """
        if path.startswith(self._url_upload):
            return path[len(self._url_upload):]
        return path

    @staticmethod
    def _normalize_path(path):
        """Makes sure the path starts with a "/"
        """
        if isinstance(path, FileInfo):
            path = path.path
        if len(path) == 0:
            return '/'
        if not path.startswith('/'):
            path = '/' + path
        return path
