from pydantic import BaseModel


class Anuncio(BaseModel):
    id: str
    uidLivro: str
    uidUsuario: str
    titulo: str
    autores: list[str]
    categorias: list[str]
    tipoNegociacao: str