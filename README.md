# Trocabook — Serviço de Recomendação

Serviço de recomendação desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros usados.

Este projeto é responsável pela aplicação de técnicas de **mineração de dados** para analisar as interações realizadas pelos usuários e gerar recomendações personalizadas de anúncios de livros disponíveis no Trocabook.

O serviço é desenvolvido em **Python** e disponibiliza uma API REST utilizando **FastAPI**, permitindo sua integração com os demais componentes do Trocabook.

---

## Objetivo

O objetivo do serviço é identificar os interesses dos usuários a partir de suas interações com a plataforma e utilizar essas informações para recomendar anúncios de livros com características semelhantes aos seus interesses.

Atualmente são consideradas três formas de interação:

- **PESQUISA** — pesquisas realizadas pelo usuário;
- **VISUALIZACAO** — visualização dos detalhes de um anúncio;
- **INICIO_CONVERSA** — início de uma conversa relacionada a um anúncio.

Cada interação possui um peso diferente de acordo com o nível de interesse que ela representa.

| Interação | Peso |
|---|---:|
| Pesquisa | 0.5 |
| Visualização | 1 |
| Início de conversa | 3 |

Os valores estão sendo avaliados experimentalmente e poderão ser ajustados durante a evolução do sistema e posterior validação com dados reais.

---

## Sistema de Recomendação

A abordagem inicial utiliza recomendação baseada nas características dos livros e no histórico de interações do usuário.

O processo segue as seguintes etapas:

1. Coleta das interações do usuário;
2. Aplicação dos pesos de cada tipo de interação;
3. Representação textual das características dos livros utilizando **TF-IDF**;
4. Cálculo da similaridade entre os livros utilizando **similaridade do cosseno**;
5. Construção do perfil de interesse do usuário;
6. Cálculo do score de recomendação;
7. Remoção dos livros com os quais o usuário já interagiu diretamente;
8. Remoção dos anúncios pertencentes ao próprio usuário;
9. Ordenação dos anúncios pelo score obtido.

### Características dos livros

Nesta etapa inicial são consideradas:

- Categorias;
- Autores.

Quando as duas características estão disponíveis, a similaridade entre os livros é calculada utilizando os seguintes pesos experimentais:

| Característica | Peso |
|---|---:|
| Categoria | 0.75 |
| Autor | 0.25 |

Caso apenas uma das características esteja disponível, ela passa a representar 100% da similaridade de conteúdo.

Dessa forma:

- Categoria e autor disponíveis: 75% categoria e 25% autor;
- Somente categoria disponível: 100% categoria;
- Somente autor disponível: 100% autor;
- Nenhuma das duas características disponível: não há informação de conteúdo suficiente para gerar similaridade.

Os pesos de categoria e autor são experimentais e serão avaliados posteriormente com dados reais da plataforma.

---

## Influência das Pesquisas

As pesquisas também são utilizadas como um sinal de interesse do usuário.

O termo pesquisado é transformado utilizando o mesmo modelo **TF-IDF** aplicado às categorias dos livros.

Em seguida, a similaridade entre o termo pesquisado e as categorias dos anúncios disponíveis é calculada utilizando **similaridade do cosseno**.

O resultado contribui para o score final da recomendação de acordo com o peso definido para a interação de pesquisa.

Nesta implementação inicial, as pesquisas são comparadas somente com as categorias.

Essa abordagem ainda é experimental e poderá ser expandida futuramente para considerar outras informações, como título e demais características dos livros.

---

## API REST

O serviço disponibiliza um endpoint para geração das recomendações personalizadas.

### Gerar recomendações

```http
POST /recomendacoes
```

A requisição recebe:

- `uidUsuario` — identificador do usuário para o qual será gerada a recomendação;
- `anuncios` — anúncios atualmente disponíveis na plataforma;
- `interacoes` — histórico de interações utilizado para identificar os interesses do usuário.

Exemplo:

```json
{
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
  "interacoes": [
    {
      "uidUsuario": "U1",
      "tipoInteracao": "VISUALIZACAO",
      "uidLivro": "L1",
      "uidAnuncio": "A1",
      "termoPesquisa": null
    }
  ]
}
```

O processamento da requisição é realizado pelo `RecomendacaoService` e o resultado interno é convertido pelo `RecomendacaoAdapter` para o contrato de resposta da API.

---

## Resultado da Recomendação

O algoritmo gera um ranking de anúncios ordenado pelo score de recomendação calculado para o usuário.

Cada item retornado pela API é representado por:

- `uidAnuncio` — identificador do anúncio recomendado;
- `score` — pontuação calculada pelo algoritmo.

Exemplo:

```json
[
  {
    "uidAnuncio": "A2",
    "score": 4.5
  },
  {
    "uidAnuncio": "A3",
    "score": 3.2
  }
]
```

O serviço de recomendação não é responsável por armazenar ou apresentar os dados completos dos anúncios.

O sistema principal do Trocabook permanece responsável pela persistência dos dados e pela recuperação das informações necessárias para exibição dos anúncios recomendados.

---

## Experimento

O diretório `notebooks/` contém o experimento utilizado para desenvolver e validar a abordagem inicial do sistema de recomendação.

```text
notebooks/
└── experimento_recomendacao.ipynb
```

O notebook utiliza um conjunto de dados controlado para permitir a análise do comportamento do algoritmo antes de sua integração com os dados reais do Trocabook.

O experimento contempla:

- definição de um conjunto controlado de livros;
- simulação das interações dos usuários;
- aplicação dos pesos das interações;
- vetorização das categorias e autores utilizando TF-IDF;
- cálculo da similaridade do cosseno;
- combinação das similaridades de categoria e autor;
- influência das pesquisas;
- cálculo dos scores;
- construção do ranking de recomendação.

Posteriormente, o algoritmo será avaliado utilizando dados reais coletados pela plataforma.

---

## Estrutura do Projeto

```text
trocabook-recomendacao-service/
│
├── app/
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── recomendacao_adapter.py
│   │
│   ├── controllers/
│   │   ├── requests/
│   │   │   ├── __init__.py
│   │   │   └── recomendacao_request.py
│   │   │
│   │   ├── responses/
│   │   │   ├── __init__.py
│   │   │   └── recomendacao_response.py
│   │   │
│   │   ├── __init__.py
│   │   └── recomendacao_controller.py
│   │
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── recomendacao_exception.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── anuncio.py
│   │   └── interacao.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── recomendacao_service.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── notebooks/
│   └── experimento_recomendacao.ipynb
│
├── tests/
│   ├── __init__.py
│   ├── test_recomendacao_adapter.py
│   ├── test_recomendacao_controller.py
│   └── test_recomendacao_service.py
│
├── test_main.http
├── requirements.txt
└── README.md
```

### Responsabilidades

- `adapters/` — conversão dos resultados internos do algoritmo para os contratos de resposta da API;
- `controllers/` — definição dos endpoints REST;
- `controllers/requests/` — contratos dos dados recebidos pela API;
- `controllers/responses/` — contratos dos dados retornados pela API;
- `exceptions/` — exceções específicas utilizadas pelo serviço;
- `models/` — modelos de domínio utilizados pelo algoritmo;
- `services/` — regras e algoritmos responsáveis pela geração das recomendações;
- `notebooks/` — experimentos relacionados à mineração de dados e ao desenvolvimento do algoritmo;
- `tests/` — testes automatizados do serviço, adapter e endpoints da API.

---

## Fluxo da Recomendação

O fluxo interno de uma requisição de recomendação é:

```text
POST /recomendacoes
        │
        ▼
RecomendacaoRequest
        │
        ▼
RecomendacaoController
        │
        ▼
RecomendacaoService
        │
        ▼
Processamento com Pandas,
TF-IDF e similaridade
        │
        ▼
Ranking em DataFrame
        │
        ▼
RecomendacaoAdapter
        │
        ▼
RecomendacaoResponse
        │
        ▼
Resposta JSON
```

O uso do adapter permite manter as estruturas utilizadas internamente pelo algoritmo separadas dos contratos expostos pela API.

---

## Logs e Tratamento de Exceções

O serviço utiliza o módulo `logging` do Python para registrar os principais pontos do processamento da recomendação.

São registrados eventos relacionados a:

- início e conclusão da geração das recomendações;
- conversão dos anúncios e interações;
- vetorização com TF-IDF;
- cálculo das similaridades;
- identificação das interações do usuário;
- cálculo dos scores;
- filtros aplicados durante a montagem do ranking;
- situações em que determinadas informações não estão disponíveis;
- erros inesperados durante o processamento.

Os níveis de log são utilizados de acordo com a finalidade da informação:

- `INFO` — eventos principais do fluxo e fallbacks relevantes;
- `WARNING` — ausência de informações que limita ou impede determinada etapa do algoritmo;
- `DEBUG` — detalhes internos utilizados para rastreabilidade do processamento;
- `ERROR` — falhas inesperadas registradas durante o processamento.

Falhas inesperadas durante a geração das recomendações são convertidas para `RecomendacaoException`.

O FastAPI possui um handler responsável por tratar essa exceção e retornar uma resposta HTTP controlada:

```json
{
  "detail": "Não foi possível gerar as recomendações."
}
```

Nesse cenário, a API retorna o status HTTP `500`.

Erros relacionados à validação dos dados da requisição são tratados pelo FastAPI e Pydantic, retornando o status HTTP `422` quando o contrato de entrada é inválido.

---

## Tratamento de Casos Especiais

O serviço possui tratamentos para situações que podem ocorrer durante o processamento dos dados.

### Usuário sem interações

Caso não existam interações suficientes para identificar os interesses do usuário, o serviço retorna um ranking vazio.

Uma estratégia de recomendação para usuários sem histórico poderá ser implementada futuramente.

### Ausência de anúncios

Caso nenhum anúncio esteja disponível, o serviço retorna um ranking vazio.

### Anúncios do próprio usuário

Anúncios pertencentes ao usuário que está recebendo as recomendações são removidos do ranking.

### Livro sem anúncio disponível

Interações antigas podem fazer referência a livros que não possuem mais anúncios disponíveis.

Essas interações são ignoradas durante o cálculo, evitando que dados históricos inválidos interrompam o processamento.

### Ausência de categorias ou autores

O algoritmo permite que um anúncio não possua uma das características utilizadas na recomendação.

Caso apenas categorias estejam disponíveis, a similaridade é calculada exclusivamente com categorias.

Caso apenas autores estejam disponíveis, a similaridade é calculada exclusivamente com autores.

Caso não existam informações suficientes de categoria ou autor para realizar a vetorização, o serviço retorna um ranking vazio.

---

## Testes Automatizados

O serviço possui testes automatizados desenvolvidos utilizando **pytest**.

Atualmente são testados o algoritmo de recomendação, o adapter e os endpoints REST da API.

Entre os cenários testados estão:

- geração de recomendações;
- exclusão de livros já utilizados no histórico de interesse;
- recomendação de livros semelhantes;
- priorização do livro com maior similaridade;
- exclusão dos anúncios pertencentes ao próprio usuário;
- ausência de interações;
- ausência de anúncios;
- interações referentes a livros que não estão mais anunciados;
- anúncios sem informações de autor e categoria;
- recomendação utilizando somente categorias;
- recomendação utilizando somente autores;
- tratamento de erros inesperados pelo `RecomendacaoService`;
- conversão do ranking para `RecomendacaoResponse`;
- preservação da ordem do ranking durante a conversão;
- conversão de ranking vazio;
- retorno de recomendações através do endpoint REST;
- retorno de lista vazia quando não existem anúncios;
- validação de requisições inválidas com status HTTP `422`;
- tratamento de falhas internas com status HTTP `500`.

Atualmente, a suíte possui **19 testes automatizados**.

A execução atual da suíte apresenta:

```text
19 passed
```

Para executar todos os testes:

```bash
pytest -v
```

---

## Tecnologias

O projeto utiliza:

- Python;
- FastAPI;
- Pandas;
- NumPy;
- Scikit-learn;
- Pydantic;
- Jupyter Notebook;
- Uvicorn;
- Pytest;
- HTTPX2 para suporte aos testes da API com `TestClient`.

---

## Executando o projeto

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
```

Entre no diretório:

```bash
cd trocabook-recomendacao-service
```

### 2. Crie um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux/macOS

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute os testes

```bash
pytest -v
```

### 6. Execute a API

```bash
uvicorn app.main:app --reload
```

A aplicação será iniciada localmente na porta `8000`.

A documentação automática do FastAPI pode ser utilizada para visualizar e testar os endpoints disponíveis.

---

## Integração com o Trocabook

A arquitetura planejada prevê a comunicação entre o sistema principal do Trocabook e este serviço através de uma API REST.

```text
Trocabook
(Spring Boot)
     │
     │ REST
     ▼
Serviço de Recomendação
(FastAPI)
     │
     ▼
Processamento das interações
     │
     ▼
Ranking personalizado
     │
     ▼
uidAnuncio + score
```

O **Spring Boot** continuará responsável pelos dados da aplicação.

O sistema principal enviará ao serviço de recomendação os anúncios disponíveis e as interações necessárias para o processamento.

O serviço em Python será responsável por executar o algoritmo de recomendação e retornar o ranking personalizado.

Dessa forma, o serviço de recomendação não precisa acessar diretamente o banco de dados principal do Trocabook.

---

## Evoluções Planejadas

Algumas funcionalidades poderão ser adicionadas durante a evolução do serviço:

- integração do serviço com o sistema principal do Trocabook;
- validação do algoritmo utilizando dados reais;
- avaliação experimental dos pesos utilizados nas interações;
- avaliação dos pesos utilizados para categorias e autores;
- utilização de métricas específicas para sistemas de recomendação;
- expansão da influência das pesquisas para considerar outras características além das categorias;
- estratégia de recomendação para usuários sem histórico de interações;
- controle da quantidade de anúncios referentes ao mesmo livro no ranking;
- utilização futura da avaliação dos vendedores como critério de seleção entre anúncios do mesmo livro.

Essas funcionalidades serão implementadas e avaliadas conforme a disponibilidade de dados reais da plataforma.

---

## Status

**Em desenvolvimento.**

Até o momento:

- [x] Estrutura inicial do serviço FastAPI;
- [x] Experimento inicial de recomendação;
- [x] Definição dos pesos das interações;
- [x] Vetorização com TF-IDF;
- [x] Similaridade do cosseno;
- [x] Ranking baseado nas interações do usuário;
- [x] Influência de pesquisas no ranking;
- [x] Implementação dos modelos da API;
- [x] Implementação dos contratos de Request e Response;
- [x] Implementação do serviço de recomendação;
- [x] Implementação do adapter de recomendação;
- [x] Implementação de logs para rastreabilidade;
- [x] Tratamento de exceções do serviço;
- [x] Criação do endpoint REST de recomendação;
- [x] Testes automatizados do serviço e do adapter;
- [x] Testes automatizados do endpoint REST;
- [ ] Integração com o Trocabook;
- [ ] Validação com dados reais.

---

## Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**.