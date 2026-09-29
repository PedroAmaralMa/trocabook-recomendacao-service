from pydantic import BaseModel

from app.models.anuncio import Anuncio
from app.models.interacao import Interacao


class RecomendacaoRequest(BaseModel):
    uidUsuario: str
    anuncios: list[Anuncio]
    interacoes: list[Interacao]