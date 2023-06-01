#!/bin/bash

rm -rf venv
python3 -m venv venv
source venv/bin/activate
sh .pip.install
deactivate

if [ -e misc/.env ]; then
  echo
else
  cp misc/.env.example misc/.env
  echo 'Скопирован файл misc/.env для дальнейшей настройки приватных параметров'
  echo
  echo 'Осталось внести необходимые приватные параметры в файл misc/.env'
fi
