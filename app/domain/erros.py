"""Exceções de negócio usadas em todas as camadas."""


class ErroDeValidacao(ValueError):
    """Dado informado pelo usuário é inválido (a mensagem é exibida na interface)."""


class NaoEncontrado(LookupError):
    """O recurso pedido (torneio ou partida) não existe."""


class ErroDeAutorizacao(Exception):
    """Operação exige a chave do torneio."""