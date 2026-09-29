from pydantic import BaseModel


class RecomendacaoResponse(BaseModel):
    uidAnuncio: str
    score: float