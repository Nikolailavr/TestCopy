from misc.functions import parse_args, read_json
from services.ftp import FTPClient
from services.local import copy_local
from services.owncloud import OwnCLoudClient
from misc.consts import LOCAL, JSON_TO_COPY


def main(args):
    data = read_json(JSON_TO_COPY)
    ftp = FTPClient()
    owncloud = OwnCLoudClient()
    for item in data['files']:
        path_file = f'{args.path}/{item["name"]}'
        for way in item['endpoints']:
            match way:
                case 'ftp': ftp.copy(path=path_file, override=args.override)
                case 'owncloud': owncloud.copy(path=path_file)
                case 'folder': copy_local(src=path_file, dest=f'{LOCAL}{item["name"]}')
                case _: print(f'[WARNING] Неверное указание способа копирования файла {path_file} ({way})')


if __name__ == '__main__':
    main(parse_args())

