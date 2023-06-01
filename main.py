from misc.consts import JSON_TO_COPY
from misc.functions import parse_args, read_json, logger, timer
from services.ftp import FTPClient
from services.local import copy_local
from services.owncloud import OwnCLoudClient

args = parse_args()


@timer
def main():
    logger.info('Старт работы приложения')
    data = read_json(JSON_TO_COPY)
    if data:
        ftp = FTPClient()
        owncloud = OwnCLoudClient()
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


@timer
def main_other():
    logger.info('Старт работы приложения')
    data = read_json(JSON_TO_COPY)
    if data:
        ftp = FTPClient()
        owncloud = OwnCLoudClient()
        filenames = {
            'ftp': [],
            'owncloud': [],
            'folder': [],
        }
        if args.dry:
            logger.warning('Сухой режим работы')
        for num, item in enumerate(data['files'], 1):
            path_file = f'{args.path}/{item["name"]}'
            for way in item['endpoints']:
                filenames[way].append(path_file)
        for key in filenames.keys():
            for value in filenames[key]:
                match key:
                    case 'ftp':
                        ftp.copy(path=value, args=args)
                    case 'owncloud':
                        owncloud.copy(path=value, args=args)
                    case 'folder':
                        copy_local(path=value, args=args)

    logger.info(f'Работа приложения завершена')


if __name__ == '__main__':
    if args.method:
        main_other()
    else:
        main()
