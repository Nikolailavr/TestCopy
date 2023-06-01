##TestCopy

Приложение для копирования файлов на различные ресурсы через ftp, owncloud или в локальную директорию.

Для запуска понадобится Python v3.11

## Начало работы
<!-- termynal -->

```
$ git copy git@github.com:Nikolailavr/TestCopy.git
$ cd TestCopy
$ sh install.sh
```

Далее необходимо выставить приватные параметры в файле misc/.env

## Запуск
<!-- termynal -->

```
$ source venv/bin/activate
$ python3 main.py data -o
```

## Помощь
<!-- termynal -->

```
$ python3 main.py --help
```
