from multiprocessing import Pool
from argparse import Namespace

from misc.consts import JSON_TO_COPY
from misc.functions import parse_args, logger, check_env, PrepareJSON
from services.deliveries import start_delivery

args = parse_args()
files_prepare = PrepareJSON()


class CopyFiles:
    def __init__(
            self,
            args_: Namespace = Namespace(
                dry=False, override=False, path='')
    ):
        self.args = args_

    def start(self):
        data = files_prepare.read_json(JSON_TO_COPY)
        if data:
            filenames = files_prepare.get_list_files(data, self.args)
            methods = []
            if self.args.dry:
                logger.warning('Сухой режим работы')
            for method in filenames.keys():
                methods.append(
                    [method, {'args': self.args, 'paths': filenames[method]}]
                )
            with Pool(processes=3) as pool:
                pool.starmap(start_delivery, methods)


def main():
    logger.info('--- Старт работы приложения ---')
    CopyFiles(args_=args).start()
    logger.info(f'--- Работа приложения завершена ---')


if __name__ == '__main__':
    check_env()
    main()
