from misc.consts import LOCAL, JSON_TO_COPY
from misc.functions import parse_args, read_json, logger
from services.ftp import FTPClient
from services.local import copy_local
from services.owncloud import OwnCLoudClient


def main(args):
    data = read_json(JSON_TO_COPY)
    ftp = FTPClient()
    owncloud = OwnCLoudClient()
    logger.info('Старт работы приложения')
    count_files = len(data['files'])
    for num, item in enumerate(data['files'], 1):
        path_file = f'{args.path}/{item["name"]}'
        logger.info(f'Работа с файлом {path_file} ({num}/{count_files})')
        for way in item['endpoints']:
            match way:
                case 'ftp':
                    ftp.copy(path=path_file, override=args.override)
                case 'owncloud':
                    owncloud.copy(local_source_file=path_file, override=args.override)
                case 'folder':
                    dest = LOCAL + '/' if not LOCAL.endswith('/') else LOCAL
                    copy_local(
                        src=path_file,
                        dest=f'{dest}{item["name"]}',
                        override=args.override
                    )
                case _:
                    logger.warning(f'Неверное указание способа копирования файла {path_file} ({way})')
    logger.info(f'Работа приложения завершена')


if __name__ == '__main__':
    main(parse_args())
