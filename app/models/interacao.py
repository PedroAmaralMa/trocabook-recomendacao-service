"""
Módulo de definição dos modelos e tipos de interações dos usuários.
"""

from enum import Enum

from pydantic import BaseModel


class TipoInteracao(str, Enum):
    """
    Enumeração dos tipos de interação suportados pelo sistema de recomendação.
    """
    PESQUISA = "PESQUISA"
    VISUALIZACAO = "VISUALIZACAO"
    INICIO_CONVERSA = "INICIO_CONVERSA"


class Interacao(BaseModel):
    """
    Representa o registro de uma interação realizada por um usuário na plataforma.
    """
    uidUsuario: str
    tipoInteracao: TipoInteracao
    uidLivro: str | None = None
    uidAnuncio: str | None = None
    termoPesquisa: str | None = None