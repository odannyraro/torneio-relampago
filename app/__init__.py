"""Torneio Relâmpago: gerador de campeonatos (mata-mata e pontos corridos).

`create_app` é a "fábrica" da aplicação Flask: cada chamada devolve uma instância
nova, o que permite configurar um banco diferente para cada teste.
"""
from flask import Flask, jsonify, render_template, request

from . import database
from .cli import comando_seed_demo, semear_demonstracao, comando_definir_chave
from .config import Config
from .domain.erros import NaoEncontrado
from .routes import api, web


def create_app(config_overrides=None):
    """Cria e configura a aplicação."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    if app.config["PRODUCAO"] and app.config["SECRET_KEY"].startswith("chave-de-desenvolvimento"):
        raise RuntimeError("Defina a variável de ambiente SECRET_KEY em produção.")

    database.init_app(app)
    app.register_blueprint(web.bp)
    app.register_blueprint(api.bp)
    app.cli.add_command(comando_seed_demo)
    app.cli.add_command(comando_definir_chave)
    _registrar_tratadores_de_erro(app)

    if app.config["SEED_DEMO"]:
        with app.app_context():
            semear_demonstracao(database.get_db())
    return app


def _registrar_tratadores_de_erro(app):
    """Páginas amigáveis (ou JSON, nas rotas /api) para recurso inexistente."""

    @app.errorhandler(NaoEncontrado)
    @app.errorhandler(404)
    def nao_encontrado(erro):
        mensagem = str(erro) if isinstance(erro, NaoEncontrado) else "Página não encontrada."
        if request.path.startswith("/api/"):
            return jsonify({"erro": mensagem}), 404
        return render_template("erro.html", mensagem=mensagem), 404
