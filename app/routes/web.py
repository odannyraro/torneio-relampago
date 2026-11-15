"""Rotas das páginas HTML."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..domain.erros import ErroDeValidacao
from . import obter_servico
from . import bloquear_edicao, liberar_edicao, obter_servico, tem_permissao

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
            chave=request.form.get("chave", "") if "proteger_com_chave" in request.form else None,
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
    torneio = obter_servico().obter_torneio(torneio_id)
    torneio["pode_editar"] = tem_permissao(torneio_id)
    return render_template("torneio.html", torneio=torneio)

@bp.post("/torneios/<int:torneio_id>/partidas/<int:partida_id>/resultado")
def registrar_resultado(torneio_id, partida_id):
    """Salva o placar informado no formulário da partida."""
    if not tem_permissao(torneio_id):
        flash("Informe a chave do torneio para editar.", "erro")
        return redirect(url_for("web.ver_torneio", torneio_id=torneio_id))
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
    if not tem_permissao(torneio_id):
        flash("Informe a chave do torneio para excluir.", "erro")
        return redirect(url_for("web.ver_torneio", torneio_id=torneio_id))
    obter_servico().excluir_torneio(torneio_id)
    flash("Torneio excluído.", "sucesso")
    return redirect(url_for("web.index"))


@bp.post("/torneios/<int:torneio_id>/desbloquear")
def desbloquear(torneio_id):
    if obter_servico().verificar_chave(torneio_id, request.form.get("chave", "")):
        liberar_edicao(torneio_id)
        flash("Edição liberada neste navegador.", "sucesso")
    else:
        flash("Chave incorreta.", "erro")
    return redirect(url_for("web.ver_torneio", torneio_id=torneio_id))

@bp.post("/torneios/<int:torneio_id>/bloquear")
def bloquear(torneio_id):
    bloquear_edicao(torneio_id)
    flash("Edição bloqueada neste navegador.", "sucesso")
    return redirect(url_for("web.ver_torneio", torneio_id=torneio_id))


@bp.get("/saude")
def saude():
    """Verificação simples usada por plataformas de deploy para saber se o app está no ar."""
    return {"status": "ok"}
