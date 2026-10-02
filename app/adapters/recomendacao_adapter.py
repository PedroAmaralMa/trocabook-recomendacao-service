"""
Módulo de adaptação de dados de recomendação para os formatos de resposta da API.
"""

import pandas as pd

from app.controllers.responses.recomendacao_response import RecomendacaoResponse


class RecomendacaoAdapter:
    """
    Responsável por transformar estruturas internas de recomendação em objetos de resposta da API.
    """

    @staticmethod
    def para_response(
        ranking: pd.DataFrame
    ) -> list[RecomendacaoResponse]:
        """
        Converte o DataFrame de ranking calculado em uma lista de respostas de recomendação.

        Args:
            ranking: DataFrame contendo as colunas 'id' e 'score' dos anúncios recomendados.

        Returns:
            Lista de objetos RecomendacaoResponse formatados para a API.
        """

        return [
            RecomendacaoResponse(
                uidAnuncio=linha["id"],
                score=float(linha["score"])
            )
            for _, linha in ranking.iterrows()
        ]