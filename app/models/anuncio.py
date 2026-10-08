"""
Módulo de definição do modelo de dados de anúncio de livro.
"""

from pydantic import BaseModel


class Anuncio(BaseModel):
    """
    Representa um anúncio de livro cadastrado no sistema para recomendação.
    """
    id: str
    uidLivro: str
    uidUsuario: str
    titulo: str
    autores: list[str]
    categorias: list[str]
    tipoNegociacao: str
    status: str