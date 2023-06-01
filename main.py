from services.functions import parse_args, read_json
from services.ftp import copy_ftp
from services.local import copy_local
from services.owncloud import copy_owncloud
from services.consts import LOCAL, JSON_TO_COPY


def main(args):
    if args.override:
        print(f'Override')
    if args.dry:
        print('Dry')
    data = read_json(JSON_TO_COPY)
    for item in data['files']:
        path_file = f'{args.path}/{item["name"]}'
        for way in item['endpoints']:
            match way:
                case 'ftp': copy_ftp(path=path_file)
                case 'owncloud': copy_owncloud(path=path_file)
                case 'folder': copy_local(src=path_file, dest=f'{LOCAL}{item["name"]}')
                case _: print(f'[WARNING] Неверное указание способа копирования файла {path_file} ({way})')


if __name__ == '__main__':
    main(parse_args())

