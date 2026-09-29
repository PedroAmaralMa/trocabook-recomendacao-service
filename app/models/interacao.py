from enum import Enum

from pydantic import BaseModel


class TipoInteracao(str, Enum):
    PESQUISA = "PESQUISA"
    VISUALIZACAO = "VISUALIZACAO"
    INICIO_CONVERSA = "INICIO_CONVERSA"


class Interacao(BaseModel):
    uidUsuario: str
    tipoInteracao: TipoInteracao
    uidLivro: str | None = None
    uidAnuncio: str | None = None
    termoPesquisa: str | None = None