"""
Módulo do modelo de requisição para geração de recomendações da API.
"""

from pydantic import BaseModel

from app.models.anuncio import Anuncio
from app.models.interacao import Interacao


class RecomendacaoRequest(BaseModel):
    """
    Estrutura de dados recebida na requisição com o contexto necessário para gerar recomendações.
    """
    uidUsuario: str
    anuncios: list[Anuncio]
    interacoes: list[Interacao]