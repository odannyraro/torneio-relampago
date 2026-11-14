<h1 align="center">Torneio Relâmpago</h1>

<p align="center">
  <a href="https://github.com/odannyraro/torneio-relampago/actions/">
    <img src="https://github.com/odannyraro/torneio-relampago/actions/workflows/ci.yml/badge.svg" alt="Status dos Testes">
  </a>
  <img src="https://img.shields.io/badge/versão-1.0.0--alpha.1-blue" alt="Versão">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Web-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/cobertura-80%25+-brightgreen" alt="Cobertura">
</p>

---
Sistema web para criação, organização e gerenciamento de torneios em formato relâmpago. Desenvolvido como Trabalho Prático da disciplina de Engenharia de Software II (DCC/UFMG).

Alunos: Álvaro Lima, Daniel Rodrigues, Sarah Menks

## Sobre o sistema

O Torneio Relâmpago tem como objetivo simplificar a logística de competições de curta duração, automatizando o fluxo desde a inscrição dos participantes até a definição do campeão.

Acesse o projeto pelo site: [https://torneio-relampago.onrender.com/](https://torneio-relampago.onrender.com/)

### Funcionalidades principais
* _Gerenciamento de torneios:_ Criação e configuração de campeonatos com regras personalizadas. 
* _Controle de participantes:_ Cadastro de jogadores ou equipes e validação de vagas.
* _Geração de chaves e partidas:_ Montagem automática dos confrontos e atualização de rodadas em tempo real.
* _Registro de placares:_ Inserção de resultados com avanço automático dos vencedores nas fases seguintes.

## Como executar o sistema

Linux/macOS:

```bash
./run_app.sh
```

Windows (PowerShell) ou manualmente:

```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Acesse http://127.0.0.1:5000. Para criar torneios de exemplo: `flask --app app seed-demo`.

Variáveis de ambiente opcionais: `TORNEIO_DB` (caminho do arquivo SQLite), `SECRET_KEY`, `SEED_DEMO=1`.

## Execução dos testes

Instale as dependências de desenvolvimento e o navegador do Playwright (só na primeira vez):

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
```

Testes de unidade com cobertura (falha se ficar abaixo de 80%):

```bash
python -m pytest tests/unit --cov=app --cov-report=term-missing --cov-fail-under=80
```

Testes end-to-end:

```bash
python -m pytest tests/e2e
```

Relatório de cobertura em HTML (opcional): `python -m pytest tests/unit --cov=app --cov-report=html` e abra `htmlcov/index.html`.

## Uso de Inteligência Artificial
