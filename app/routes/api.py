"""API JSON (útil para integrações e para testar o sistema sem navegador)."""
from flask import Blueprint, jsonify, request

from ..domain.erros import ErroDeValidacao
from . import obter_servico

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.errorhandler(ErroDeValidacao)
def tratar_validacao(erro):
    return jsonify({"erro": str(erro)}), 400


@bp.get("/torneios")
def listar():
    return jsonify(obter_servico().listar_torneios())


@bp.get("/torneios/<int:torneio_id>")
def detalhar(torneio_id):
    return jsonify(obter_servico().obter_torneio(torneio_id))


@bp.post("/torneios")
def criar():
    """Corpo JSON: nome, jogo, formato, participantes (lista) e, opcionalmente, embaralhar/ida_e_volta."""
    dados = request.get_json(silent=True) or {}
    servico = obter_servico()
    torneio_id = servico.criar_torneio(
        nome=dados.get("nome"),
        jogo=dados.get("jogo"),
        formato=dados.get("formato"),
        nomes_participantes=dados.get("participantes"),
        embaralhar=bool(dados.get("embaralhar", True)),
        ida_e_volta=bool(dados.get("ida_e_volta", False)),
    )
    return jsonify(servico.obter_torneio(torneio_id)), 201


@bp.post("/torneios/<int:torneio_id>/partidas/<int:partida_id>/resultado")
def registrar_resultado(torneio_id, partida_id):
    """Corpo JSON: placar1 e placar2."""
    dados = request.get_json(silent=True) or {}
    servico = obter_servico()
    servico.registrar_resultado(torneio_id, partida_id, dados.get("placar1"), dados.get("placar2"))
    return jsonify(servico.obter_torneio(torneio_id))
