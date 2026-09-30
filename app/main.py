from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers.recomendacao_controller import router as recomendacao_router
from app.exceptions.recomendacao_exception import RecomendacaoException


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
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc)
        }
    )


@app.get("/")
def root():
    return {
        "message": "Trocabook - Serviço de Recomendação"
    }