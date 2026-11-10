# torneio-relampago 1.0.0 alpha 1

## Trabalho Pratico - Engenharia de Software II

### Alunos: Álvaro Lima, Daniel Rodrigues, Sarah Menks

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

