"""Validação e normalização dos dados informados pelo usuário."""
import re

from .erros import ErroDeValidacao

MATA_MATA = "mata_mata"
PONTOS_CORRIDOS = "pontos_corridos"
FORMATOS = (MATA_MATA, PONTOS_CORRIDOS)

MIN_PARTICIPANTES = 2
MAX_PARTICIPANTES = 32
TAMANHO_MAX_NOME = 40
PLACAR_MAXIMO = 999
PONTUACAO_MAXIMA = 9223372036854775807


def validar_nome_torneio(nome):
    """Remove espaços das pontas e exige um nome de até TAMANHO_MAX_NOME caracteres."""
    nome = (nome or "").strip()
    if not nome:
        raise ErroDeValidacao("Informe o nome do torneio.")
    if len(nome) > TAMANHO_MAX_NOME:
        raise ErroDeValidacao(f"O nome do torneio deve ter no máximo {TAMANHO_MAX_NOME} caracteres.")
    return nome


def validar_jogo(jogo):
    """O jogo é opcional (ex.: FIFA, Mario Kart), mas tem o mesmo limite de tamanho."""
    jogo = (jogo or "").strip()
    if len(jogo) > TAMANHO_MAX_NOME:
        raise ErroDeValidacao(f"O nome do jogo deve ter no máximo {TAMANHO_MAX_NOME} caracteres.")
    return jogo


def validar_formato(formato):
    """O formato precisa ser 'mata_mata' ou 'pontos_corridos'."""
    if formato not in FORMATOS:
        raise ErroDeValidacao("Escolha um formato válido: mata-mata ou pontos corridos.")
    return formato


def validar_pontuacoes(pontos_vitoria, pontos_empate):
    """Valida as pontuações inteiras de vitória e empate dos pontos corridos."""
    valores = []
    for valor in (pontos_vitoria, pontos_empate):
        if isinstance(valor, bool) or not (
            isinstance(valor, int)
            or isinstance(valor, str) and re.fullmatch(r"[+-]?\d+", valor.strip())
        ):
            raise ErroDeValidacao("As pontuações devem ser números inteiros.")
        try:
            inteiro = int(valor)
        except ValueError:
            raise ErroDeValidacao("As pontuações devem ser números inteiros.") from None
        if inteiro > PONTUACAO_MAXIMA:
            raise ErroDeValidacao("A pontuação não pode exceder o limite permitido.")
        valores.append(inteiro)

    vitoria, empate = valores
    if vitoria <= 0:
        raise ErroDeValidacao("A pontuação de vitória deve ser maior que zero.")
    if empate < 0:
        raise ErroDeValidacao("A pontuação de empate deve ser maior ou igual a zero.")
    if vitoria <= empate:
        raise ErroDeValidacao("A pontuação de vitória deve ser maior que a de empate.")
    return vitoria, empate


def normalizar_participantes(nomes):
    """Limpa a lista de participantes e garante as regras de quantidade e unicidade.

    - ignora linhas vazias e espaços repetidos;
    - não aceita nomes repetidos (sem diferenciar maiúsculas de minúsculas);
    - exige entre MIN_PARTICIPANTES e MAX_PARTICIPANTES nomes.
    """
    if isinstance(nomes, str):
        nomes = nomes.splitlines()  # aceita o texto de um campo com um nome por linha

    limpos = []
    vistos = set()
    for nome in nomes or []:
        nome = " ".join(str(nome).split())  # tira espaços das pontas e duplicados no meio
        if not nome:
            continue
        if len(nome) > TAMANHO_MAX_NOME:
            raise ErroDeValidacao(
                f"Cada nome deve ter no máximo {TAMANHO_MAX_NOME} caracteres: '{nome[:15]}...'."
            )
        chave = nome.casefold()
        if chave in vistos:
            raise ErroDeValidacao(f"O participante '{nome}' foi informado mais de uma vez.")
        vistos.add(chave)
        limpos.append(nome)

    if len(limpos) < MIN_PARTICIPANTES:
        raise ErroDeValidacao(f"Informe pelo menos {MIN_PARTICIPANTES} participantes.")
    if len(limpos) > MAX_PARTICIPANTES:
        raise ErroDeValidacao(f"O limite é de {MAX_PARTICIPANTES} participantes por torneio.")
    return limpos


def validar_placar(placar1, placar2, permite_empate):
    """Converte os placares para inteiros e confere se são válidos.

    Em mata-mata (permite_empate=False) alguém precisa vencer, então o empate é recusado.
    """
    try:
        gols1, gols2 = int(placar1), int(placar2)
    except (TypeError, ValueError):
        raise ErroDeValidacao("Os placares devem ser números inteiros.") from None

    if gols1 < 0 or gols2 < 0:
        raise ErroDeValidacao("Os placares não podem ser negativos.")
    if gols1 > PLACAR_MAXIMO or gols2 > PLACAR_MAXIMO:
        raise ErroDeValidacao(f"O placar máximo permitido é {PLACAR_MAXIMO}.")
    if gols1 == gols2 and not permite_empate:
        raise ErroDeValidacao("No mata-mata não pode haver empate: informe um vencedor.")
    return gols1, gols2


def validar_chave(chave):
    chave = (chave or "").strip()
    if len(chave) < 4:
        raise ErroDeValidacao("A chave de edição deve ter pelo menos 4 caracteres.")
    if len(chave) > 64:
        raise ErroDeValidacao("A chave de edição pode ter no máximo 64 caracteres.")
    return chave