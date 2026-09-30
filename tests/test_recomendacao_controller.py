from fastapi.testclient import TestClient

from app.main import app
from app.services.recomendacao_service import RecomendacaoService


client = TestClient(app)


def test_deve_retornar_recomendacoes():
    payload = {
        "uidUsuario": "U1",
        "anuncios": [
            {
                "id": "A1",
                "uidLivro": "L1",
                "uidUsuario": "V1",
                "titulo": "Harry Potter e a Pedra Filosofal",
                "autores": ["J. K. Rowling"],
                "categorias": ["fantasia", "aventura"],
                "tipoNegociacao": "TROCA"
            },
            {
                "id": "A2",
                "uidLivro": "L2",
                "uidUsuario": "V2",
                "titulo": "Harry Potter e a Câmara Secreta",
                "autores": ["J. K. Rowling"],
                "categorias": ["fantasia", "aventura"],
                "tipoNegociacao": "VENDA"
            }
        ],
        "interacoes": [
            {
                "uidUsuario": "U1",
                "tipoInteracao": "VISUALIZACAO",
                "uidLivro": "L1",
                "uidAnuncio": "A1",
                "termoPesquisa": None
            }
        ]
    }

    response = client.post(
        "/recomendacoes",
        json=payload
    )

    assert response.status_code == 200

    dados = response.json()

    assert len(dados) == 1
    assert dados[0]["uidAnuncio"] == "A2"
    assert dados[0]["score"] > 0


def test_deve_retornar_lista_vazia_quando_nao_houver_anuncios():
    payload = {
        "uidUsuario": "U1",
        "anuncios": [],
        "interacoes": []
    }

    response = client.post(
        "/recomendacoes",
        json=payload
    )

    assert response.status_code == 200
    assert response.json() == []


def test_deve_retornar_422_quando_request_for_invalido():
    payload = {
        "anuncios": [],
        "interacoes": []
    }

    response = client.post(
        "/recomendacoes",
        json=payload
    )

    assert response.status_code == 422


def test_deve_retornar_500_quando_ocorrer_erro_na_recomendacao(
    monkeypatch
):
    def simular_erro(*args, **kwargs):
        raise ValueError(
            "Erro interno simulado"
        )

    monkeypatch.setattr(
        RecomendacaoService,
        "_converter_anuncios_dataframe",
        simular_erro
    )

    payload = {
        "uidUsuario": "U1",
        "anuncios": [
            {
                "id": "A1",
                "uidLivro": "L1",
                "uidUsuario": "V1",
                "titulo": "Livro 1",
                "autores": ["Autor A"],
                "categorias": ["fantasia"],
                "tipoNegociacao": "TROCA"
            }
        ],
        "interacoes": []
    }

    response = client.post(
        "/recomendacoes",
        json=payload
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Não foi possível gerar as recomendações."
    }