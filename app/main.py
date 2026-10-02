"""
Ponto de entrada da aplicação FastAPI do serviço de recomendação.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers.recomendacao_controller import router as recomendacao_router
from app.exceptions.recomendacao_exception import RecomendacaoException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
app = FastAPI(
    title="Trocabook - Serviço de Recomendação",
    version="1.0.0"
)

app.include_router(recomendacao_router)


@app.exception_handler(RecomendacaoException)
async def recomendacao_exception_handler(
    request: Request,
    exc: RecomendacaoException
):
    """
    Manipula exceções do tipo RecomendacaoException retornando resposta HTTP 500 padronizada.

    Args:
        request: Objeto de requisição HTTP do FastAPI.
        exc: Instância da exceção RecomendacaoException capturada.

    Returns:
        JSONResponse com status code 500 e mensagem de detalhe do erro.
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc)
        }
    )


@app.get("/")
def root():
    """
    Retorna uma mensagem de status e identificação do serviço.
    """
    return {
        "message": "Trocabook - Serviço de Recomendação"
    }