"""Camada web: rotas HTML (web.py) e API JSON (api.py)."""
from ..database import get_db
from ..services.torneio_service import TorneioService


def obter_servico():
    """Cria o serviço usando a conexão do banco da requisição atual."""
    return TorneioService(get_db())
