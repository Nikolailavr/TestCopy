from misc.consts import JSON_TO_COPY
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
    if args.dry:
        logger.warning('Сухой режим работы')
    for num, item in enumerate(data['files'], 1):
        path_file = f'{args.path}/{item["name"]}'
        logger.info(f'Работа с файлом {path_file} ({num}/{count_files})')
        for way in item['endpoints']:
            match way:
                case 'ftp':
                    ftp.copy(path=path_file, args=args)
                case 'owncloud':
                    owncloud.copy(path=path_file, args=args)
                case 'folder':
                    copy_local(path=path_file, args=args)
                case _:
                    logger.warning(f'Неверное указание способа копирования файла {path_file} ({way})')
    logger.info(f'Работа приложения завершена')


if __name__ == '__main__':
    main(parse_args())
