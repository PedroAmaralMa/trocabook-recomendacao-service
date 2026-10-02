"""
Módulo do modelo de resposta de recomendações da API.
"""

from pydantic import BaseModel


class RecomendacaoResponse(BaseModel):
    """
    Representa o item de recomendação retornado pela API contendo o anúncio e sua pontuação.
    """
    uidAnuncio: str
    score: float