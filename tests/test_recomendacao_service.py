from app.models.anuncio import Anuncio
from app.models.interacao import Interacao, TipoInteracao
from app.services.recomendacao_service import RecomendacaoService


def criar_anuncios():
    return [
        Anuncio(
            id="A1",
            uidLivro="L1",
            uidUsuario="V1",
            titulo="Harry Potter e a Pedra Filosofal",
            autores=["J. K. Rowling"],
            categorias=["fantasia", "aventura"],
            tipoNegociacao="TROCA"
        ),
        Anuncio(
            id="A2",
            uidLivro="L2",
            uidUsuario="V2",
            titulo="Harry Potter e a Câmara Secreta",
            autores=["J. K. Rowling"],
            categorias=["fantasia", "aventura"],
            tipoNegociacao="TROCA"
        ),
        Anuncio(
            id="A3",
            uidLivro="L3",
            uidUsuario="V3",
            titulo="O Hobbit",
            autores=["J. R. R. Tolkien"],
            categorias=["fantasia", "aventura"],
            tipoNegociacao="VENDA"
        ),
        Anuncio(
            id="A4",
            uidLivro="L4",
            uidUsuario="V4",
            titulo="Dom Casmurro",
            autores=["Machado de Assis"],
            categorias=["romance", "literatura brasileira"],
            tipoNegociacao="TROCA"
        ),
        Anuncio(
            id="A5",
            uidLivro="L5",
            uidUsuario="V5",
            titulo="Clean Code",
            autores=["Robert Martin"],
            categorias=["programacao", "tecnologia"],
            tipoNegociacao="VENDA"
        )
    ]

def criar_interacoes():
    return [
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.VISUALIZACAO,
            uidLivro="L1",
            uidAnuncio="A1",
            termoPesquisa=None
        ),
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.INICIO_CONVERSA,
            uidLivro="L1",
            uidAnuncio="A1",
            termoPesquisa=None
        ),
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.PESQUISA,
            uidLivro=None,
            uidAnuncio=None,
            termoPesquisa="fantasia"
        )
    ]

def test_deve_gerar_recomendacoes():
    service = RecomendacaoService()

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=criar_anuncios(),
        interacoes=criar_interacoes()
    )

    assert not ranking.empty

def test_nao_deve_recomendar_livro_ja_interagido():
    service = RecomendacaoService()

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=criar_anuncios(),
        interacoes=criar_interacoes()
    )

    assert "L1" not in ranking["uidLivro"].values


def test_deve_recomendar_livro_semelhante():
    service = RecomendacaoService()

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=criar_anuncios(),
        interacoes=criar_interacoes()
    )

    assert "L2" in ranking["uidLivro"].values


def test_livro_mais_semelhante_deve_ter_maior_score():
    service = RecomendacaoService()

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=criar_anuncios(),
        interacoes=criar_interacoes()
    )

    assert ranking.iloc[0]["uidLivro"] == "L2"

def test_nao_deve_recomendar_anuncio_do_proprio_usuario():
    service = RecomendacaoService()

    anuncios = criar_anuncios()

    anuncios.append(
        Anuncio(
            id="A6",
            uidLivro="L6",
            uidUsuario="U1",
            titulo="Outro Livro de Fantasia",
            autores=["Autor Teste"],
            categorias=["fantasia", "aventura"],
            tipoNegociacao="TROCA"
        )
    )

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=anuncios,
        interacoes=criar_interacoes()
    )

    assert "A6" not in ranking["id"].values

def test_deve_aceitar_lista_de_interacoes_vazia():
    service = RecomendacaoService()

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=criar_anuncios(),
        interacoes=[]
    )

    assert ranking.empty

def test_deve_retornar_ranking_vazio_quando_nao_existirem_anuncios():
    service = RecomendacaoService()

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=[],
        interacoes=[]
    )

    assert ranking.empty

def test_deve_ignorar_interacao_com_livro_sem_anuncio():
    service = RecomendacaoService()

    interacoes = [
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.VISUALIZACAO,
            uidLivro="L999",
            uidAnuncio="A999",
            termoPesquisa=None
        ),
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.PESQUISA,
            uidLivro=None,
            uidAnuncio=None,
            termoPesquisa="fantasia"
        )
    ]

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=criar_anuncios(),
        interacoes=interacoes
    )

    assert not ranking.empty

def test_deve_tratar_anuncios_sem_autores_e_categorias():
    service = RecomendacaoService()

    anuncios = [
        Anuncio(
            id="A1",
            uidLivro="L1",
            uidUsuario="V1",
            titulo="Livro 1",
            autores=[],
            categorias=[],
            tipoNegociacao="TROCA"
        ),
        Anuncio(
            id="A2",
            uidLivro="L2",
            uidUsuario="V2",
            titulo="Livro 2",
            autores=[],
            categorias=[],
            tipoNegociacao="VENDA"
        )
    ]

    interacoes = [
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.VISUALIZACAO,
            uidLivro="L1",
            uidAnuncio="A1",
            termoPesquisa=None
        )
    ]

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=anuncios,
        interacoes=interacoes
    )

    assert ranking.empty


def test_deve_recomendar_quando_somente_categorias_estiverem_disponiveis():
    service = RecomendacaoService()

    anuncios = [
        Anuncio(
            id="A1",
            uidLivro="L1",
            uidUsuario="V1",
            titulo="Livro 1",
            autores=[],
            categorias=["fantasia"],
            tipoNegociacao="TROCA"
        ),
        Anuncio(
            id="A2",
            uidLivro="L2",
            uidUsuario="V2",
            titulo="Livro 2",
            autores=[],
            categorias=["fantasia"],
            tipoNegociacao="VENDA"
        ),
        Anuncio(
            id="A3",
            uidLivro="L3",
            uidUsuario="V3",
            titulo="Livro 3",
            autores=[],
            categorias=["tecnologia"],
            tipoNegociacao="VENDA"
        )
    ]

    interacoes = [
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.VISUALIZACAO,
            uidLivro="L1",
            uidAnuncio="A1",
            termoPesquisa=None
        )
    ]

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=anuncios,
        interacoes=interacoes
    )

    assert not ranking.empty
    assert ranking.iloc[0]["uidLivro"] == "L2"

def test_deve_recomendar_quando_somente_autores_estiverem_disponiveis():
    service = RecomendacaoService()

    anuncios = [
        Anuncio(
            id="A1",
            uidLivro="L1",
            uidUsuario="V1",
            titulo="Livro 1",
            autores=["Autor A"],
            categorias=[],
            tipoNegociacao="TROCA"
        ),
        Anuncio(
            id="A2",
            uidLivro="L2",
            uidUsuario="V2",
            titulo="Livro 2",
            autores=["Autor A"],
            categorias=[],
            tipoNegociacao="VENDA"
        ),
        Anuncio(
            id="A3",
            uidLivro="L3",
            uidUsuario="V3",
            titulo="Livro 3",
            autores=["Autor B"],
            categorias=[],
            tipoNegociacao="VENDA"
        )
    ]

    interacoes = [
        Interacao(
            uidUsuario="U1",
            tipoInteracao=TipoInteracao.VISUALIZACAO,
            uidLivro="L1",
            uidAnuncio="A1",
            termoPesquisa=None
        )
    ]

    ranking = service.recomendar(
        uid_usuario="U1",
        anuncios=anuncios,
        interacoes=interacoes
    )

    assert not ranking.empty
    assert ranking.iloc[0]["uidLivro"] == "L2"