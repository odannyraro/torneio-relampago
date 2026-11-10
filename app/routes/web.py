"""Rotas das páginas HTML."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..domain.erros import ErroDeValidacao
from . import obter_servico

bp = Blueprint("web", __name__)


@bp.get("/")
def index():
    """Lista os torneios existentes."""
    return render_template("index.html", torneios=obter_servico().listar_torneios())


@bp.route("/torneios/novo", methods=["GET", "POST"])
def novo_torneio():
    """Formulário de criação (GET) e criação do torneio (POST)."""
    if request.method == "GET":
        return render_template("novo.html", form={"embaralhar": "on"})

    try:
        torneio_id = obter_servico().criar_torneio(
            nome=request.form.get("nome", ""),
            jogo=request.form.get("jogo", ""),
            formato=request.form.get("formato", ""),
            nomes_participantes=request.form.get("participantes", ""),
            embaralhar="embaralhar" in request.form,
            ida_e_volta="ida_e_volta" in request.form,
        )
    except ErroDeValidacao as erro:
        flash(str(erro), "erro")
        # Devolve o formulário preenchido para o usuário só corrigir o que errou.
        return render_template("novo.html", form=request.form), 400

    flash("Torneio criado! Boa sorte a todos.", "sucesso")
    return redirect(url_for("web.ver_torneio", torneio_id=torneio_id))


@bp.get("/torneios/<int:torneio_id>")
def ver_torneio(torneio_id):
    """Mostra a chave (mata-mata) ou a tabela e as rodadas (pontos corridos)."""
    return render_template("torneio.html", torneio=obter_servico().obter_torneio(torneio_id))


@bp.post("/torneios/<int:torneio_id>/partidas/<int:partida_id>/resultado")
def registrar_resultado(torneio_id, partida_id):
    """Salva o placar informado no formulário da partida."""
    try:
        obter_servico().registrar_resultado(
            torneio_id, partida_id, request.form.get("placar1"), request.form.get("placar2")
        )
        flash("Resultado salvo.", "sucesso")
    except ErroDeValidacao as erro:
        flash(str(erro), "erro")
    return redirect(url_for("web.ver_torneio", torneio_id=torneio_id))


@bp.post("/torneios/<int:torneio_id>/excluir")
def excluir_torneio(torneio_id):
    """Apaga o torneio e volta para a lista."""
    obter_servico().excluir_torneio(torneio_id)
    flash("Torneio excluído.", "sucesso")
    return redirect(url_for("web.index"))


@bp.get("/saude")
def saude():
    """Verificação simples usada por plataformas de deploy para saber se o app está no ar."""
    return {"status": "ok"}
