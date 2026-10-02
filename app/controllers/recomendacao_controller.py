"""
Módulo do controller de recomendações da API.
"""

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
    """
    Recebe os dados do usuário, anúncios e interações para retornar uma lista ordenada de recomendações.

    Args:
        request: Objeto de requisição contendo o identificador do usuário, a lista de anúncios e as interações.

    Returns:
        Lista de anúncios recomendados com seus respectivos scores calculados.
    """

    ranking = recomendacao_service.recomendar(
        uid_usuario=request.uidUsuario,
        anuncios=request.anuncios,
        interacoes=request.interacoes
    )

    return RecomendacaoAdapter.para_response(ranking)