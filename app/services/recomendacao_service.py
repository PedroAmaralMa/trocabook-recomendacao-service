import logging

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.exceptions.recomendacao_exception import RecomendacaoException

from app.models.anuncio import Anuncio
from app.models.interacao import Interacao


logger = logging.getLogger(__name__)


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
        logger.info(
            "Iniciando recomendação para usuário %s. "
            "Anúncios recebidos: %d. Interações recebidas: %d.",
            uid_usuario,
            len(anuncios),
            len(interacoes)
        )

        try:
            if not anuncios:
                logger.info(
                    "Nenhum anúncio disponível para o usuário %s. "
                    "Retornando ranking vazio.",
                    uid_usuario
                )
                return self._criar_ranking_vazio()

            df_anuncios = self._converter_anuncios_dataframe(
                anuncios
            )

            df_interacoes = self._converter_interacoes_dataframe(
                interacoes
            )

            logger.debug(
                "Aplicando pesos em %d interações.",
                len(df_interacoes)
            )

            df_interacoes["peso"] = (
                df_interacoes["tipoInteracao"]
                .map(self.PESOS_INTERACOES)
            )

            matriz_categorias, vectorizer_categorias = (
                self._vetorizar(
                    df_anuncios["categorias"],
                    "categorias"
                )
            )

            matriz_autores, _ = self._vetorizar(
                df_anuncios["autores"],
                "autores"
            )

            similaridades = self._calcular_similaridades(
                matriz_categorias,
                matriz_autores
            )

            if similaridades is None:
                logger.warning(
                    "Não foi possível calcular similaridades para o "
                    "usuário %s por ausência de categorias e autores. "
                    "Retornando ranking vazio.",
                    uid_usuario
                )
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

            scores_finais = (
                    scores_livros +
                    scores_pesquisas
            )

            logger.debug(
                "Scores finais calculados para %d anúncios.",
                len(scores_finais)
            )

            livros_interagidos = (
                interesses["uidLivro"].tolist()
            )

            ranking = self._montar_ranking(
                df_anuncios,
                scores_finais,
                livros_interagidos,
                uid_usuario
            )

            logger.info(
                "Recomendação concluída para usuário %s. "
                "Quantidade de recomendações: %d.",
                uid_usuario,
                len(ranking)
            )

            return ranking

        except Exception as erro:
            logger.exception(
                "Erro inesperado ao gerar recomendações "
                "para o usuário %s.",
                uid_usuario
            )

            raise RecomendacaoException(
                "Não foi possível gerar as recomendações."
            ) from erro

    def _converter_anuncios_dataframe(
        self,
        anuncios: list[Anuncio]
    ) -> pd.DataFrame:

        logger.debug(
            "Convertendo %d anúncios para DataFrame.",
            len(anuncios)
        )

        dados = []

        for anuncio in anuncios:
            dados.append({
                "id": anuncio.id,
                "uidLivro": anuncio.uidLivro,
                "uidUsuario": anuncio.uidUsuario,
                "titulo": anuncio.titulo,
                "autores": " ".join(
                    anuncio.autores or []
                ),
                "categorias": " ".join(
                    anuncio.categorias or []
                )
            })

        dataframe = pd.DataFrame(dados)

        logger.debug(
            "Conversão de anúncios concluída. "
            "Registros no DataFrame: %d.",
            len(dataframe)
        )

        return dataframe

    def _converter_interacoes_dataframe(
        self,
        interacoes: list[Interacao]
    ) -> pd.DataFrame:

        logger.debug(
            "Convertendo %d interações para DataFrame.",
            len(interacoes)
        )

        dados = []

        for interacao in interacoes:
            dados.append({
                "uidUsuario": interacao.uidUsuario,
                "tipoInteracao": (
                    interacao.tipoInteracao.value
                ),
                "uidLivro": interacao.uidLivro,
                "uidAnuncio": interacao.uidAnuncio,
                "termoPesquisa": (
                    interacao.termoPesquisa
                )
            })

        dataframe = pd.DataFrame(
            dados,
            columns=[
                "uidUsuario",
                "tipoInteracao",
                "uidLivro",
                "uidAnuncio",
                "termoPesquisa"
            ]
        )

        logger.debug(
            "Conversão de interações concluída. "
            "Registros no DataFrame: %d.",
            len(dataframe)
        )

        return dataframe

    def _vetorizar(
        self,
        dados,
        tipo_dado: str
    ):
        logger.debug(
            "Iniciando vetorização TF-IDF de %s.",
            tipo_dado
        )

        if (
            dados
            .fillna("")
            .str.strip()
            .eq("")
            .all()
        ):
            logger.warning(
                "Vetorização de %s ignorada: "
                "nenhum dado textual disponível.",
                tipo_dado
            )

            return None, None

        vectorizer = TfidfVectorizer()

        matriz = vectorizer.fit_transform(
            dados
        )

        logger.debug(
            "Vetorização de %s concluída. "
            "Documentos: %d. Termos: %d.",
            tipo_dado,
            matriz.shape[0],
            matriz.shape[1]
        )

        return matriz, vectorizer

    def _calcular_similaridades(
        self,
        matriz_categorias,
        matriz_autores
    ):
        logger.debug(
            "Iniciando cálculo das similaridades."
        )

        tem_categorias = (
            matriz_categorias is not None
        )

        tem_autores = (
            matriz_autores is not None
        )

        if tem_categorias and tem_autores:
            logger.debug(
                "Calculando similaridade com categorias "
                "e autores. Pesos: categoria=%.2f, autor=%.2f.",
                self.PESO_CATEGORIA,
                self.PESO_AUTOR
            )

            similaridade_categorias = (
                cosine_similarity(
                    matriz_categorias
                )
            )

            similaridade_autores = (
                cosine_similarity(
                    matriz_autores
                )
            )

            similaridades = (
                similaridade_categorias
                * self.PESO_CATEGORIA
                +
                similaridade_autores
                * self.PESO_AUTOR
            )

            logger.debug(
                "Similaridade combinada calculada."
            )

            return similaridades

        if tem_categorias:
            logger.info(
                "Autores indisponíveis. "
                "Similaridade será calculada somente "
                "com categorias."
            )

            return cosine_similarity(
                matriz_categorias
            )

        if tem_autores:
            logger.info(
                "Categorias indisponíveis. "
                "Similaridade será calculada somente "
                "com autores."
            )

            return cosine_similarity(
                matriz_autores
            )

        logger.warning(
            "Não existem categorias ou autores "
            "disponíveis para cálculo de similaridade."
        )

        return None

    def _obter_interacoes_usuario(
        self,
        interacoes,
        uid_usuario,
        tipo_interacao=None
    ):
        logger.debug(
            "Buscando interações do usuário %s. Tipo: %s.",
            uid_usuario,
            tipo_interacao or "TODAS"
        )

        resultado = interacoes[
            interacoes["uidUsuario"]
            == uid_usuario
        ]

        if tipo_interacao is not None:
            resultado = resultado[
                resultado["tipoInteracao"]
                == tipo_interacao
            ]

        logger.debug(
            "Encontradas %d interações para o usuário %s. "
            "Tipo: %s.",
            len(resultado),
            uid_usuario,
            tipo_interacao or "TODAS"
        )

        return resultado

    def _obter_interacoes_livros(
        self,
        interacoes_usuario
    ):
        logger.debug(
            "Filtrando interações associadas diretamente "
            "a livros."
        )

        resultado = interacoes_usuario[
            interacoes_usuario[
                "uidLivro"
            ].notna()
        ]

        logger.debug(
            "Encontradas %d interações associadas "
            "diretamente a livros.",
            len(resultado)
        )

        return resultado

    def _calcular_interesse_por_livro(
        self,
        interacoes_livros
    ):
        logger.debug(
            "Calculando interesse agregado por livro "
            "a partir de %d interações.",
            len(interacoes_livros)
        )

        interesses = (
            interacoes_livros
            .groupby("uidLivro")["peso"]
            .sum()
            .reset_index()
        )

        logger.debug(
            "Interesse calculado para %d livros.",
            len(interesses)
        )

        return interesses

    def _calcular_scores_livros(
        self,
        anuncios,
        interesses,
        similaridades
    ):
        logger.debug(
            "Calculando scores baseados em %d "
            "livros de interesse.",
            len(interesses)
        )

        scores = np.zeros(
            len(anuncios)
        )

        for _, interesse in interesses.iterrows():
            uid_livro = interesse["uidLivro"]
            peso = interesse["peso"]

            indices = anuncios.index[
                anuncios["uidLivro"]
                == uid_livro
            ]

            if len(indices) == 0:
                logger.debug(
                    "Livro %s possui interação, mas não "
                    "possui anúncio disponível. Ignorando.",
                    uid_livro
                )

                continue

            indice = indices[0]

            scores += (
                similaridades[indice]
                * peso
            )

        logger.debug(
            "Cálculo dos scores por livros concluído."
        )

        return scores

    def _calcular_scores_pesquisas(
        self,
        pesquisas,
        anuncios,
        vectorizer_categorias,
        matriz_categorias
    ):
        logger.debug(
            "Calculando influência de %d pesquisas "
            "nos scores.",
            len(pesquisas)
        )

        scores = np.zeros(
            len(anuncios)
        )

        if (
            vectorizer_categorias is None
            or matriz_categorias is None
        ):
            logger.debug(
                "Influência das pesquisas ignorada: "
                "não existe vetorização de categorias."
            )

            return scores

        pesquisas_processadas = 0

        for _, pesquisa in pesquisas.iterrows():
            termo = pesquisa[
                "termoPesquisa"
            ]

            if (
                pd.isna(termo)
                or not termo.strip()
            ):
                logger.debug(
                    "Pesquisa sem termo válido ignorada."
                )

                continue

            vetor_pesquisa = (
                vectorizer_categorias
                .transform([termo])
            )

            similaridade = (
                cosine_similarity(
                    vetor_pesquisa,
                    matriz_categorias
                )[0]
            )

            scores += (
                similaridade
                * pesquisa["peso"]
            )

            pesquisas_processadas += 1

        logger.debug(
            "Cálculo dos scores de pesquisa concluído. "
            "Pesquisas processadas: %d.",
            pesquisas_processadas
        )

        return scores

    def _montar_ranking(
        self,
        anuncios,
        scores,
        livros_interagidos,
        uid_usuario
    ):
        logger.debug(
            "Iniciando montagem do ranking. "
            "Anúncios candidatos: %d. "
            "Livros já interagidos: %d.",
            len(anuncios),
            len(livros_interagidos)
        )

        ranking = anuncios.copy()

        ranking["score"] = scores

        quantidade_inicial = len(ranking)

        ranking = ranking[
            ~ranking["uidLivro"].isin(
                livros_interagidos
            )
        ]

        logger.debug(
            "Removidos %d anúncios relacionados "
            "a livros já interagidos.",
            quantidade_inicial - len(ranking)
        )

        quantidade_antes_proprios = len(
            ranking
        )

        ranking = ranking[
            ranking["uidUsuario"]
            != uid_usuario
        ]

        logger.debug(
            "Removidos %d anúncios pertencentes "
            "ao próprio usuário.",
            quantidade_antes_proprios
            - len(ranking)
        )

        quantidade_antes_score = len(
            ranking
        )

        ranking = ranking[
            ranking["score"] > 0
        ]

        logger.debug(
            "Removidos %d anúncios sem score positivo.",
            quantidade_antes_score
            - len(ranking)
        )

        ranking = ranking.sort_values(
            by="score",
            ascending=False
        )

        logger.debug(
            "Ranking final montado com %d anúncios.",
            len(ranking)
        )

        return ranking

    def _criar_ranking_vazio(
        self
    ):
        logger.debug(
            "Criando estrutura de ranking vazio."
        )

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