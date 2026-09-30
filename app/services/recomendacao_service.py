import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.anuncio import Anuncio
from app.models.interacao import Interacao


class RecomendacaoService:

    PESOS_INTERACOES = {
        "PESQUISA": 0.5,
        "VISUALIZACAO": 1,
        "INICIO_CONVERSA": 3
    }

    PESO_CATEGORIA = 0.75
    PESO_AUTOR = 0.25

    def recomendar(
        self,
        uid_usuario: str,
        anuncios: list[Anuncio],
        interacoes: list[Interacao]
    ):
        if not anuncios:
            return self._criar_ranking_vazio()

        df_anuncios = self._converter_anuncios_dataframe(anuncios)
        df_interacoes = self._converter_interacoes_dataframe(interacoes)

        df_interacoes["peso"] = (
            df_interacoes["tipoInteracao"]
            .map(self.PESOS_INTERACOES)
        )

        matriz_categorias, vectorizer_categorias = (
            self._vetorizar(df_anuncios["categorias"])
        )

        matriz_autores, _ = self._vetorizar(
            df_anuncios["autores"]
        )

        similaridades = self._calcular_similaridades(
            matriz_categorias,
            matriz_autores
        )

        if similaridades is None:
            return self._criar_ranking_vazio()

        interacoes_usuario = self._obter_interacoes_usuario(
            df_interacoes,
            uid_usuario
        )

        interacoes_livros = self._obter_interacoes_livros(
            interacoes_usuario
        )

        pesquisas = self._obter_interacoes_usuario(
            df_interacoes,
            uid_usuario,
            "PESQUISA"
        )

        interesses = self._calcular_interesse_por_livro(
            interacoes_livros
        )

        scores_livros = self._calcular_scores_livros(
            df_anuncios,
            interesses,
            similaridades
        )

        scores_pesquisas = self._calcular_scores_pesquisas(
            pesquisas,
            df_anuncios,
            vectorizer_categorias,
            matriz_categorias
        )

        scores_finais = scores_livros + scores_pesquisas

        livros_interagidos = interesses["uidLivro"].tolist()

        return self._montar_ranking(
            df_anuncios,
            scores_finais,
            livros_interagidos,
            uid_usuario
        )

    def _converter_anuncios_dataframe(
        self,
        anuncios: list[Anuncio]
    ) -> pd.DataFrame:

        dados = []

        for anuncio in anuncios:
            dados.append({
                "id": anuncio.id,
                "uidLivro": anuncio.uidLivro,
                "uidUsuario": anuncio.uidUsuario,
                "titulo": anuncio.titulo,
                "autores": " ".join(anuncio.autores or []),
                "categorias": " ".join(anuncio.categorias or [])
            })

        return pd.DataFrame(dados)

    def _converter_interacoes_dataframe(
            self,
            interacoes: list[Interacao]
    ) -> pd.DataFrame:

        dados = []

        for interacao in interacoes:
            dados.append({
                "uidUsuario": interacao.uidUsuario,
                "tipoInteracao": interacao.tipoInteracao.value,
                "uidLivro": interacao.uidLivro,
                "uidAnuncio": interacao.uidAnuncio,
                "termoPesquisa": interacao.termoPesquisa
            })

        return pd.DataFrame(
            dados,
            columns=[
                "uidUsuario",
                "tipoInteracao",
                "uidLivro",
                "uidAnuncio",
                "termoPesquisa"
            ]
        )

    def _vetorizar(self, dados):
        if dados.fillna("").str.strip().eq("").all():
            return None, None

        vectorizer = TfidfVectorizer()
        matriz = vectorizer.fit_transform(dados)

        return matriz, vectorizer

    def _calcular_similaridades(
            self,
            matriz_categorias,
            matriz_autores
    ):
        tem_categorias = matriz_categorias is not None
        tem_autores = matriz_autores is not None

        if tem_categorias and tem_autores:
            similaridade_categorias = cosine_similarity(
                matriz_categorias
            )

            similaridade_autores = cosine_similarity(
                matriz_autores
            )

            return (
                    similaridade_categorias * self.PESO_CATEGORIA +
                    similaridade_autores * self.PESO_AUTOR
            )

        if tem_categorias:
            return cosine_similarity(
                matriz_categorias
            )

        if tem_autores:
            return cosine_similarity(
                matriz_autores
            )

        return None

    def _obter_interacoes_usuario(
        self,
        interacoes,
        uid_usuario,
        tipo_interacao=None
    ):
        resultado = interacoes[
            interacoes["uidUsuario"] == uid_usuario
        ]

        if tipo_interacao is not None:
            resultado = resultado[
                resultado["tipoInteracao"] == tipo_interacao
            ]

        return resultado


    def _obter_interacoes_livros(
        self,
        interacoes_usuario
    ):
        return interacoes_usuario[
            interacoes_usuario["uidLivro"].notna()
        ]


    def _calcular_interesse_por_livro(
        self,
        interacoes_livros
    ):
        return (
            interacoes_livros
            .groupby("uidLivro")["peso"]
            .sum()
            .reset_index()
        )

    def _calcular_scores_livros(
        self,
        anuncios,
        interesses,
        similaridades
    ):
        scores = np.zeros(len(anuncios))

        for _, interesse in interesses.iterrows():
            uid_livro = interesse["uidLivro"]
            peso = interesse["peso"]

            indices = anuncios.index[
                anuncios["uidLivro"] == uid_livro
            ]

            if len(indices) == 0:
                continue

            indice = indices[0]

            scores += similaridades[indice] * peso

        return scores

    def _calcular_scores_pesquisas(
            self,
            pesquisas,
            anuncios,
            vectorizer_categorias,
            matriz_categorias
    ):
        scores = np.zeros(len(anuncios))

        if vectorizer_categorias is None or matriz_categorias is None:
            return scores

        for _, pesquisa in pesquisas.iterrows():
            termo = pesquisa["termoPesquisa"]

            if pd.isna(termo) or not termo.strip():
                continue

            vetor_pesquisa = vectorizer_categorias.transform(
                [termo]
            )

            similaridade = cosine_similarity(
                vetor_pesquisa,
                matriz_categorias
            )[0]

            scores += similaridade * pesquisa["peso"]

        return scores

    def _montar_ranking(
            self,
            anuncios,
            scores,
            livros_interagidos,
            uid_usuario
    ):
        ranking = anuncios.copy()

        ranking["score"] = scores

        ranking = ranking[
            ~ranking["uidLivro"].isin(livros_interagidos)
        ]

        ranking = ranking[
            ranking["uidUsuario"] != uid_usuario
            ]

        ranking = ranking[
            ranking["score"] > 0
            ]

        return ranking.sort_values(
            by="score",
            ascending=False
        )

    def _criar_ranking_vazio(self):
        return pd.DataFrame(
            columns=[
                "id",
                "uidLivro",
                "uidUsuario",
                "titulo",
                "autores",
                "categorias",
                "score"
            ]
        )