# 📚 Trocabook — Serviço de Recomendação

Serviço de recomendação de livros desenvolvido para o **Trocabook**, uma plataforma voltada à troca e venda de livros usados.

Este projeto é responsável pela aplicação de técnicas de **mineração de dados** para analisar as interações realizadas pelos usuários e gerar recomendações personalizadas de livros.

O serviço está sendo desenvolvido em **Python** e será disponibilizado através de uma API utilizando **FastAPI**, permitindo sua integração com os demais componentes do Trocabook.

---

## 🎯 Objetivo

O objetivo do serviço é identificar os interesses dos usuários a partir de suas interações com a plataforma e utilizar essas informações para recomendar livros com características semelhantes.

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

Os valores estão sendo avaliados experimentalmente e poderão ser ajustados durante a evolução do sistema.

---

## 🧠 Sistema de Recomendação

A abordagem inicial utiliza recomendação baseada nas características dos livros e no histórico de interações do usuário.

O processo experimental segue as seguintes etapas:

1. Coleta das interações do usuário;
2. Aplicação dos pesos de cada tipo de interação;
3. Representação textual das características dos livros utilizando **TF-IDF**;
4. Cálculo da similaridade entre livros utilizando **similaridade do cosseno**;
5. Construção do perfil de interesse do usuário;
6. Cálculo do score de recomendação;
7. Remoção dos livros com os quais o usuário já interagiu diretamente;
8. Ordenação dos livros pelo score obtido.

### Características dos livros

Nesta etapa inicial são consideradas:

- Categorias;
- Autores.

A similaridade entre os livros é calculada utilizando os seguintes pesos experimentais:

| Característica | Peso |
|---|---:|
| Categoria | 0.75 |
| Autor | 0.25 |

---

## 🔎 Influência das Pesquisas

As pesquisas também são utilizadas como um sinal de interesse.

O termo pesquisado é transformado utilizando o mesmo modelo TF-IDF aplicado às categorias dos livros. A similaridade entre o termo e as categorias contribui para o score final da recomendação.

Essa abordagem ainda é experimental e poderá ser expandida para considerar outras informações, como título e demais características dos livros.

---

## 🧪 Experimento

O diretório `notebooks/` contém o experimento utilizado para desenvolver e validar a abordagem inicial do sistema de recomendação.

```text
notebooks/
└── experimento_recomendacao.ipynb
```

O notebook utiliza um conjunto de dados controlado para permitir a análise do comportamento do algoritmo antes de sua integração com os dados reais do Trocabook.

---

## 🏗️ Estrutura do Projeto

```text
trocabook-recomendacao-service/
│
├── app/
│   ├── controllers/
│   ├── models/
│   ├── services/
│   ├── __init__.py
│   └── main.py
│
├── notebooks/
│   └── experimento_recomendacao.ipynb
│
├── tests/
├── requirements.txt
└── README.md
```

### Responsabilidades

- `controllers/` — endpoints da API;
- `models/` — modelos utilizados na comunicação com a API;
- `services/` — regras e algoritmos de recomendação;
- `notebooks/` — experimentos de mineração de dados;
- `tests/` — testes automatizados.

---

## 🛠️ Tecnologias

- Python
- FastAPI
- Pandas
- NumPy
- Scikit-learn
- Jupyter Notebook
- Uvicorn

---

## ▶️ Executando o projeto

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

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute a API

```bash
uvicorn app.main:app --reload
```

A aplicação será iniciada localmente na porta `8000`.

---

## 🔗 Integração com o Trocabook

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
```

O Spring Boot continuará responsável pelos dados da aplicação, enquanto este serviço ficará responsável pelo processamento necessário para geração das recomendações.

---

## 🚧 Status

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
- [ ] Implementação do serviço de recomendação;
- [ ] Criação dos endpoints REST;
- [ ] Integração com o Trocabook;
- [ ] Testes automatizados;
- [ ] Validação com dados reais.

---

## 📚 Projeto Trocabook

O Trocabook é um projeto acadêmico desenvolvido com o objetivo de incentivar a reutilização de livros por meio de uma plataforma que possibilita a troca e venda de livros usados.

O projeto está relacionado ao **Objetivo de Desenvolvimento Sustentável 12 (ODS 12) — Consumo e Produção Responsáveis**.