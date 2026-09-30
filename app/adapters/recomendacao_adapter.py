import pandas as pd

from app.controllers.responses.recomendacao_response import RecomendacaoResponse


class RecomendacaoAdapter:

    @staticmethod
    def para_response(
        ranking: pd.DataFrame
    ) -> list[RecomendacaoResponse]:

        return [
            RecomendacaoResponse(
                uidAnuncio=linha["id"],
                score=float(linha["score"])
            )
            for _, linha in ranking.iterrows()
        ]