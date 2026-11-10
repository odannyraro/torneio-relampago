#!/usr/bin/env bash
# Cria o ambiente virtual (se preciso), instala as dependências e inicia o servidor de desenvolvimento.
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
flask --app app run --debug