from multiprocessing import Pool
from misc.consts import JSON_TO_COPY
from misc.functions import parse_args, read_json, logger, check_env
from services.deliveries import start_delivery

args = parse_args()


def main():
    logger.info('--- Старт работы приложения ---')
    data = read_json(JSON_TO_COPY)
    if data:
        filenames = {
            'ftp': [],
            'owncloud': [],
            'folder': [],
        }
        methods = []
        if args.dry:
            logger.warning('Сухой режим работы')
        for item in data['files']:
            path_file = f'{args.path}/{item["name"]}'
            for way in item['endpoints']:
                filenames[way].append(path_file)
        for method in filenames:
            methods.append(
                [method, {'args': args, 'paths': filenames[method]}]
            )
        with Pool(processes=3) as pool:
            pool.starmap(start_delivery, methods)
    logger.info(f'--- Работа приложения завершена ---')


if __name__ == '__main__':
    check_env()
    main()
