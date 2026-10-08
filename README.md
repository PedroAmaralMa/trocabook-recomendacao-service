# Trocabook — Serviço de Recomendação

Serviço de recomendação desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros usados.

Este projeto é responsável pela aplicação de técnicas de **mineração de dados** para analisar as interações realizadas pelos usuários e gerar recomendações personalizadas de anúncios de livros disponíveis no Trocabook.

O serviço é desenvolvido em **Python** e disponibiliza uma API REST utilizando **FastAPI**, permitindo sua integração com o sistema principal do Trocabook desenvolvido em **Spring Boot**.

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

Os valores foram definidos experimentalmente e poderão ser ajustados durante a evolução do sistema e posterior validação com dados reais.

---

## Sistema de Recomendação

A abordagem utiliza recomendação baseada nas características dos livros e no histórico de interações do usuário.

O processo segue as seguintes etapas:

1. Coleta das interações do usuário;
2. Aplicação dos pesos de cada tipo de interação;
3. Representação textual das características dos livros utilizando **TF-IDF**;
4. Cálculo da similaridade entre os livros utilizando **similaridade do cosseno**;
5. Construção do perfil de interesse do usuário;
6. Análise dos termos pesquisados pelo usuário;
7. Cálculo do score de recomendação;
8. Remoção dos anúncios finalizados do ranking final;
9. Remoção dos livros com os quais o usuário já interagiu diretamente;
10. Remoção dos anúncios pertencentes ao próprio usuário;
11. Remoção dos anúncios sem score positivo;
12. Ordenação dos anúncios pelo score obtido.

Os anúncios com status `FINALIZADO` podem participar das etapas de processamento e cálculo das recomendações como dados históricos. Entretanto, somente anúncios com status `ATIVO` podem compor o ranking final retornado pelo serviço.

### Características dos livros

Para calcular a similaridade de conteúdo entre os livros são consideradas:

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

Os pesos de categoria e autor são experimentais e poderão ser avaliados posteriormente com dados reais da plataforma.

---

## Influência das Pesquisas

As pesquisas realizadas no Trocabook também são utilizadas como um sinal de interesse do usuário.

Para permitir que a pesquisa influencie livros relacionados a diferentes características, é criada uma representação textual específica para pesquisa combinando:

- Título;
- Autores;
- Categorias.

O conteúdo textual de cada livro é representado utilizando **TF-IDF**.

O termo pesquisado pelo usuário é transformado utilizando o mesmo `TfidfVectorizer` responsável pela representação do conteúdo de pesquisa dos livros.

Em seguida, é calculada a **similaridade do cosseno** entre o vetor correspondente ao termo pesquisado e a matriz de conteúdo dos livros.

O resultado obtido contribui para o score final da recomendação de acordo com o peso definido para a interação `PESQUISA`.

Essa estratégia permite, por exemplo, que uma pesquisa possa influenciar a recomendação por correspondência com o título, autor ou categoria de um livro.

---

## API REST

O serviço disponibiliza um endpoint para geração das recomendações personalizadas.

### Gerar recomendações

```http
POST /recomendacoes
```

A requisição recebe:

- `uidUsuario` — identificador do usuário para o qual será gerada a recomendação;
- `anuncios` — anúncios utilizados pelo algoritmo, incluindo anúncios ativos e finalizados que podem contribuir para a identificação dos interesses do usuário;
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
      "tipoNegociacao": "TROCA",
      "status": "ATIVO"
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

O algoritmo gera um ranking de anúncios ativos ordenado pelo score de recomendação calculado para o usuário.

Anúncios finalizados podem contribuir para o cálculo das recomendações como dados históricos, mas são removidos antes da construção do ranking final retornado pela API.

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

O notebook utiliza um conjunto de dados controlado para permitir a análise do comportamento do algoritmo antes de sua utilização com os dados da aplicação.

O experimento contempla:

- definição de um conjunto controlado de livros;
- simulação das interações dos usuários;
- aplicação dos pesos das interações;
- vetorização das categorias e autores utilizando TF-IDF;
- cálculo da similaridade do cosseno;
- combinação das similaridades de categoria e autor;
- construção do perfil de interesse do usuário;
- criação de uma representação textual para pesquisa utilizando título, autores e categorias;
- influência das pesquisas no score;
- cálculo dos scores;
- construção do ranking de recomendação;
- remoção de livros já utilizados no histórico de interesse;
- remoção dos anúncios pertencentes ao próprio usuário.

O notebook documenta as principais etapas utilizadas na construção e avaliação experimental do algoritmo.

A validação do comportamento do sistema com um volume maior de dados reais da plataforma permanece como uma etapa futura.

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
Cálculo dos scores
        │
        ▼
Aplicação dos filtros
do ranking
        │
        ▼
Ranking de anúncios ativos
em DataFrame
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

No sistema principal do Trocabook, esse cenário pode ser tratado utilizando anúncios aleatórios quando necessário.

### Ausência de anúncios

Caso nenhum anúncio esteja disponível, o serviço retorna um ranking vazio.

### Anúncios do próprio usuário

Anúncios pertencentes ao usuário que está recebendo as recomendações são removidos do ranking.

### Anúncios finalizados

Anúncios com status `FINALIZADO` podem ser utilizados durante o cálculo das recomendações como dados históricos, permitindo que interações anteriores continuem contribuindo para a identificação dos interesses do usuário.

Entretanto, somente anúncios com status `ATIVO` podem compor o ranking final retornado pelo serviço.

Dessa forma, um anúncio finalizado pode contribuir para identificar livros semelhantes aos interesses anteriores do usuário sem ser apresentado como uma opção disponível para troca ou venda.

### Livros já utilizados no histórico de interesse

Livros com os quais o usuário já interagiu diretamente são removidos do ranking final para evitar que o sistema continue recomendando itens que já fizeram parte do histórico utilizado para identificar seus interesses.

### Livro sem anúncio disponível

Interações antigas podem fazer referência a livros que não possuem mais anúncios disponíveis.

Essas interações são ignoradas durante o cálculo, evitando que dados históricos inválidos interrompam o processamento.

### Ausência de categorias ou autores

O algoritmo permite que um anúncio não possua uma das características utilizadas na recomendação.

Caso apenas categorias estejam disponíveis, a similaridade de conteúdo é calculada exclusivamente com categorias.

Caso apenas autores estejam disponíveis, a similaridade de conteúdo é calculada exclusivamente com autores.

Caso não existam informações suficientes de categoria ou autor para realizar a vetorização necessária, o serviço retorna um ranking vazio.

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
- influência de pesquisa por título na recomendação;
- exclusão de anúncios finalizados do ranking;
- utilização de anúncios finalizados no cálculo de recomendações sem incluí-los no ranking final;
- tratamento de erros inesperados pelo `RecomendacaoService`;
- conversão do ranking para `RecomendacaoResponse`;
- preservação da ordem do ranking durante a conversão;
- conversão de ranking vazio;
- retorno de recomendações através do endpoint REST;
- retorno de lista vazia quando não existem anúncios;
- validação de requisições inválidas com status HTTP `422`;
- tratamento de falhas internas com status HTTP `500`.

Atualmente, a suíte possui **22 testes automatizados**.

A execução atual da suíte apresenta:

```text
22 passed
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
- HTTPX para suporte aos testes da API com `TestClient`.

---

## Executando o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/PedroAmaralMa/trocabook-recomendacao-service.git
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
python -m uvicorn app.main:app --reload
```

A aplicação será iniciada localmente na porta `8000`.

A documentação automática do FastAPI pode ser utilizada para visualizar e testar os endpoints disponíveis.

---

## Integração com o Trocabook

O serviço de recomendação está integrado ao sistema principal do Trocabook através de uma API REST.

O sistema principal, desenvolvido em **Spring Boot**, permanece responsável pela persistência e recuperação dos dados da aplicação.

O fluxo de integração ocorre da seguinte forma:

```text
Trocabook
(Spring Boot)
     │
     │ anúncios + interações
     │ REST
     ▼
Serviço de Recomendação
(FastAPI)
     │
     ▼
Processamento das interações
e características dos livros
     │
     ▼
Ranking personalizado
     │
     ▼
uidAnuncio + score
     │
     ▼
Trocabook
(Spring Boot)
     │
     ▼
Recuperação e ordenação
dos anúncios
```

O Spring Boot envia ao serviço de recomendação:

- identificador do usuário;
- anúncios ativos e finalizados necessários ao cálculo da recomendação;
- histórico de interações do usuário.

Os anúncios finalizados podem contribuir para a identificação dos interesses do usuário a partir de dados históricos, porém são removidos do ranking final pelo serviço de recomendação.

O serviço Python processa essas informações e retorna apenas o ranking contendo o identificador dos anúncios ativos recomendados e seus respectivos scores.

Dessa forma, o serviço de recomendação não acessa diretamente o **Firebase**, mantendo a responsabilidade pela persistência no sistema principal.

### Cache das recomendações

Para reduzir chamadas repetidas ao serviço Python e melhorar o desempenho da aplicação, o sistema principal utiliza cache para armazenar temporariamente o ranking de recomendações de cada usuário.

O cache armazena os identificadores dos anúncios e seus respectivos scores, enquanto os dados completos dos anúncios continuam sendo responsabilidade do sistema principal.

A estratégia permite reutilizar um ranking calculado anteriormente sem executar novamente todo o processamento de recomendação a cada acesso do usuário.

A atualização do ranking ocorre de acordo com o tempo de expiração configurado no sistema principal.

### Indisponibilidade do serviço

A indisponibilidade do serviço de recomendação não deve impedir a utilização das páginas principais do Trocabook.

O sistema principal possui estratégias de fallback para esses casos.

Na **Home**, caso não seja possível obter um ranking personalizado, são apresentados anúncios aleatórios.

Na página de **Livros**, caso o serviço esteja indisponível, a lista completa de anúncios continua sendo apresentada utilizando sua ordenação original.

Dessa forma, o sistema de recomendação funciona como um recurso adicional de personalização sem se tornar um ponto obrigatório para o funcionamento do catálogo.

### Utilização das recomendações

As recomendações são utilizadas atualmente em dois contextos principais.

#### Home

A Home apresenta uma quantidade limitada de anúncios recomendados ao usuário.

O ranking retornado pelo serviço é utilizado para selecionar os anúncios com maior score.

#### Catálogo de livros

Na página de Livros, todos os anúncios ativos continuam disponíveis.

O ranking de recomendação é utilizado para reorganizar a listagem, posicionando primeiro os anúncios presentes no ranking personalizado.

Os anúncios ativos que não fazem parte do ranking continuam sendo exibidos após os itens recomendados.

Essa estratégia permite personalizar a navegação sem remover opções disponíveis do catálogo.

---

## Evoluções Planejadas

Algumas melhorias poderão ser avaliadas durante a evolução do serviço:

- validação do algoritmo utilizando um volume maior de dados reais;
- avaliação experimental dos pesos utilizados nas interações;
- avaliação dos pesos utilizados para categorias e autores;
- utilização de métricas específicas para sistemas de recomendação;
- avaliação de estratégias específicas para usuários sem histórico de interações;
- controle da quantidade de anúncios referentes ao mesmo livro no ranking;
- utilização futura da avaliação dos vendedores como critério adicional de seleção entre anúncios do mesmo livro;
- avaliação de novas características que possam contribuir para a personalização das recomendações.

Essas funcionalidades poderão ser implementadas e avaliadas conforme a disponibilidade de dados e a evolução da plataforma.

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
- [x] Pesquisa considerando título, autores e categorias;
- [x] Implementação dos modelos da API;
- [x] Implementação dos contratos de Request e Response;
- [x] Implementação do serviço de recomendação;
- [x] Implementação do adapter de recomendação;
- [x] Implementação de logs para rastreabilidade;
- [x] Tratamento de exceções do serviço;
- [x] Criação do endpoint REST de recomendação;
- [x] Testes automatizados do serviço e do adapter;
- [x] Testes automatizados do endpoint REST;
- [x] Teste da influência de pesquisa por título;
- [x] Tratamento de anúncios ativos e finalizados no sistema de recomendação;
- [x] Testes do comportamento de anúncios finalizados no ranking;
- [x] Integração com o sistema principal do Trocabook;
- [x] Utilização das recomendações na Home;
- [x] Ordenação personalizada do catálogo de livros;
- [x] Cache das recomendações no sistema principal;
- [x] Fallback em caso de indisponibilidade do serviço de recomendação;
- [ ] Validação do algoritmo com um volume maior de dados reais.

---

## Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**.