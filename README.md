# NFL Big Data Bowl - Análise de Dados com Algoritmos Avançados

Projeto desenvolvido como parte da disciplina de **Algoritmos Avançados** no curso de **Engenharia de Software**. O objetivo é aplicar conceitos avançados de algoritmos e estruturas de dados para realizar análises exploratórias e preditivas sobre os dados disponibilizados pela competição [NFL Big Data Bowl](https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/overview).

## Objetivo

O propósito deste projeto é analisar os dados de tracking de jogadores durante jogadas da NFL para extrair informações relevantes, identificar padrões e propor insights que possam contribuir com a compreensão do jogo e o desenvolvimento de modelos preditivos.

## O que este projeto faz?

* Carrega e organiza os datasets fornecidos pela NFL (jogadas, jogadores, tracking, etc.).
* Realiza análise exploratória dos dados (visualizações, estatísticas descritivas).
* Aplica algoritmos e estruturas de dados eficientes para tratar grandes volumes de informação.
* (Opcional) Implementa modelos de aprendizado de máquina simples para previsão de jogadas ou métricas como Yards Gained.
* Gera relatórios ou gráficos explicativos com base nos dados processados.

## Estrutura do Projeto

```
nfl-big-data-bowl/
│
├── input/                  # Datasets CSV (adicionados manualmente)
├── requirements.txt       # Dependências do projeto
├── README.md              # Este arquivo
└── main.py                # Script principal de execução
```

## ⚙️ Como Rodar o Projeto

### 1. Clone o repositório

```bash
git clone https://github.com/carlosManoelWendorff1/bigdata-bowl.git
cd bigdata-bowl
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
source venv/bin/activate
venv\Scripts\activate.bat
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Baixe os datasets

Você pode baixar os dados da competição diretamente do [Kaggle](https://www.kaggle.com/competitions/nfl-big-data-bowl-2024/data) e colocar os arquivos `.csv` na pasta `input/`.

### 5. Execute a análise

```bash
python main.py
```

## Tecnologias e Ferramentas

* Python 3.10+
* Pandas / NumPy
* Matplotlib / Seaborn / Plotly
* Scikit-learn (opcional para modelagem)

## Conceitos Aplicados

* Análise exploratória de dados (EDA)
* Algoritmos eficientes para filtragem, agregação e análise
* (Opcional) Regressão linear, KNN, Decision Trees
* Manipulação eficiente de dados tabulares
* Visualização de movimentação espacial (jogadores no campo)

## Autores

* Gabriel Eduardo da Silva Rosa;
* Jefferson Salomon;
* Carlos Wendorff;
