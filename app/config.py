"""Configurações da aplicação.

Os valores podem ser sobrescritos por variáveis de ambiente, o que facilita
o deploy em plataformas de nuvem (Render, Fly.io etc.).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Configuração padrão (desenvolvimento local)."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")
    # Caminho do arquivo SQLite. Em produção, aponte para um volume persistente.
    DATABASE = os.environ.get("TORNEIO_DB", str(BASE_DIR / "data" / "torneio.db"))
    # Se "1", cria torneios de demonstração quando o banco está vazio.
    SEED_DEMO = os.environ.get("SEED_DEMO", "0") == "1"
    TESTING = False
    # "1" em produção: ativa cookie Secure e exige SECRET_KEY real.
    PRODUCAO = os.environ.get("PRODUCAO", "0") == "1"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"   # também protege os POSTs contra CSRF de outros sites
    SESSION_COOKIE_SECURE = PRODUCAO
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30  # 30 dias
