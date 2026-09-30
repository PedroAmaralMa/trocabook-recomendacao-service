import pandas as pd

from app.adapters.recomendacao_adapter import RecomendacaoAdapter
from app.controllers.responses.recomendacao_response import RecomendacaoResponse


def test_deve_converter_ranking_para_response():
    ranking = pd.DataFrame([
        {
            "id": "A1",
            "uidLivro": "L1",
            "score": 4.5
        },
        {
            "id": "A2",
            "uidLivro": "L2",
            "score": 3.2
        }
    ])

    resultado = RecomendacaoAdapter.para_response(ranking)

    assert len(resultado) == 2
    assert isinstance(resultado[0], RecomendacaoResponse)

    assert resultado[0].uidAnuncio == "A1"
    assert resultado[0].score == 4.5

    assert resultado[1].uidAnuncio == "A2"
    assert resultado[1].score == 3.2

def test_deve_manter_ordem_do_ranking():
    ranking = pd.DataFrame([
        {
            "id": "A3",
            "score": 5.0
        },
        {
            "id": "A1",
            "score": 3.0
        },
        {
            "id": "A2",
            "score": 1.0
        }
    ])

    resultado = RecomendacaoAdapter.para_response(ranking)

    assert [item.uidAnuncio for item in resultado] == [
        "A3",
        "A1",
        "A2"
    ]

def test_deve_retornar_lista_vazia_quando_ranking_estiver_vazio():
    ranking = pd.DataFrame(
        columns=["id", "score"]
    )

    resultado = RecomendacaoAdapter.para_response(ranking)

    assert resultado == []