"""Comandos de linha de comando e dados de demonstração.

Uso:  flask --app app seed-demo
"""
import random

import click
from flask.cli import with_appcontext

from .database import get_db
from .domain.validacao import MATA_MATA, PONTOS_CORRIDOS
from .services.torneio_service import TorneioService


def semear_demonstracao(conexao):
    """Cria dois torneios de exemplo se o banco estiver vazio. Devolve quantos foram criados."""
    servico = TorneioService(conexao, sorteio=random.Random(2026))
    if servico.listar_torneios():
        return 0

    copa = servico.criar_torneio(
        "Copa do Fim de Semana", "FIFA", MATA_MATA,
        ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Fábio"], embaralhar=False,
    )
    liga = servico.criar_torneio(
        "Liga Kart", "Mario Kart", PONTOS_CORRIDOS,
        ["Ana", "Bruno", "Carla", "Diego"], embaralhar=False,
    )

    # Alguns resultados para a demonstração já aparecer preenchida.
    primeira_da_copa = next(p for p in servico.obter_torneio(copa)["partidas"] if p["pode_registrar"])
    servico.registrar_resultado(copa, primeira_da_copa["id"], 3, 1)
    for partida in servico.obter_torneio(liga)["partidas"][:3]:
        servico.registrar_resultado(liga, partida["id"], 2, 1)
    return 2


@click.command("seed-demo")
@with_appcontext  # get_db() precisa do contexto da aplicação
def comando_seed_demo():
    """Cria torneios de demonstração (somente se o banco estiver vazio)."""
    criados = semear_demonstracao(get_db())
    click.echo(f"{criados} torneio(s) de demonstração criado(s).")


@click.command("definir-chave")
@click.argument("torneio_id", type=int)
@click.password_option("--chave", prompt="Nova chave", confirmation_prompt=True)
@with_appcontext
def comando_definir_chave(torneio_id, chave):
    """Define (ou troca) a chave de edição de um torneio."""
    TorneioService(get_db()).definir_chave(torneio_id, chave)
    click.echo("Chave definida.")