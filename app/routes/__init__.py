"""Camada web: rotas HTML (web.py) e API JSON (api.py)."""
from flask import session

from ..database import get_db
from ..services.torneio_service import TorneioService

MAX_LIBERADOS = 50  # o cookie de sessão tem ~4 KB; guardamos só os acessos mais recentes


def obter_servico():
    """Cria o serviço usando a conexão do banco da requisição atual."""
    return TorneioService(get_db())


def tem_permissao(torneio_id):
    """True se este navegador já informou a chave (ou se o torneio não tem chave)."""
    assinatura = obter_servico().assinatura_da_chave(torneio_id)
    if assinatura is None:
        return True
    return session.get("liberados", {}).get(str(torneio_id)) == assinatura


def liberar_edicao(torneio_id):
    assinatura = obter_servico().assinatura_da_chave(torneio_id)
    if assinatura is None:
        return  # torneio sem chave: nao guarda nada
    liberados = dict(session.get("liberados", {}))
    liberados.pop(str(torneio_id), None)       # reinsere no fim (mais recente)
    liberados[str(torneio_id)] = assinatura
    while len(liberados) > MAX_LIBERADOS:
        liberados.pop(next(iter(liberados)))   # descarta o mais antigo
    session["liberados"] = liberados
    session.permanent = True


def bloquear_edicao(torneio_id):
    liberados = dict(session.get("liberados", {}))
    liberados.pop(str(torneio_id), None)
    session["liberados"] = liberados