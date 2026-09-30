from fastapi import APIRouter

from app.adapters.recomendacao_adapter import RecomendacaoAdapter
from app.controllers.requests.recomendacao_request import RecomendacaoRequest
from app.controllers.responses.recomendacao_response import RecomendacaoResponse
from app.services.recomendacao_service import RecomendacaoService


router = APIRouter(
    prefix="/recomendacoes",
    tags=["Recomendações"]
)

recomendacao_service = RecomendacaoService()


@router.post(
    "",
    response_model=list[RecomendacaoResponse]
)
def recomendar(
    request: RecomendacaoRequest
) -> list[RecomendacaoResponse]:

    ranking = recomendacao_service.recomendar(
        uid_usuario=request.uidUsuario,
        anuncios=request.anuncios,
        interacoes=request.interacoes
    )

    return RecomendacaoAdapter.para_response(ranking)