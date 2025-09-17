# Projeto VR Mensal

Este projeto processa planilhas contidas em um arquivo ZIP, carrega os dados em um banco SQLite, 
faz consultas usando um LLM (Google Gemini via LangChain) e gera uma planilha final com os valores de VR para cada funcionário.

# Como a solução foi construida
A aplicação foi estruturada em quatro etapas principais:

Carregamento dos dados (LOAD)
Os arquivos ZIP são extraídos e os dados contidos nas planilhas são carregados em um banco de dados SQLite. -> extractor.py.

Criação do agente de consultas
É criado um agente utilizando LangChain que permite consultar a base de dados SQLite de forma interativa, facilitando a extração de informações necessárias para o processamento. -> agent.py

Processamento dos dados
Com os dados carregados, o agente é utilizado para consultar a base. Em seguida, os dados são organizados, agregados e filtrados de acordo com as regras definidas no enunciado. -> processing.py

Geração da planilha final
Por fim, os dados processados são consolidados e exportados para um arquivo de saída, gerando a planilha VR MENSAL 05.2025 com os valores correspondentes a cada funcionário. -> processing.py 

## Estrutura de Pastas
````

├── data/
│ └── Desafio 4 - Dados.zip
├── src/
│ ├── config.py
│ ├── database.py
│ ├── extractor.py
│ ├── agent.py
│ ├── processing.py
│ └── main.py
├── requirements.txt
└── README.md
````

## Como Rodar

1. Crie e ative um ambiente virtual:

```` bash
python -m venv .venv

source .venv/bin/activate   # Linux/Mac

.venv\Scripts\activate      # Windows
````

2. Instale as dependências:

```` bash
pip install -r requirements.txt
````

3. Crie um arquivo .env na raiz do projeto com sua chave da API do Google:

```` 
GOOGLE_API_KEY=sua_chave_aqui
````

4. Execute o projeto:

````
python -m src.main
````

5. Diagrama do fluxo:

```mermaid
graph TD
    A[▶️ Início] --> B{1. Extração de Dados};
    B --> C{2. Criação do Agente};
    C --> D{3. Processamento de Sindicatos};
    D --> E{4. Obtenção de Dados Auxiliares};
    E --> F{5. Cálculo Principal};
    F --> G{6. Salvamento do Resultado};
    G --> H[✅ Fim];

    subgraph "Etapa 1: Extração"
        B_1["Arquivo ZIP de entrada<br>(ZIP_PATH)"] --> B_2["Executa<br>extract_zip_to_sqlite"];
        B_2 --> B_3["Banco de Dados SQLite<br>(DB_PATH)"];
    end

    subgraph "Etapa 2: Agente"
        C_1["Banco de Dados SQLite<br>(DB_PATH)"] --> C_2["Executa<br>criar_agente"];
        C_2 --> C_3["Agente LLM<br>(agent)"];
    end

    subgraph "Etapa 3: Sindicatos"
        D_1["Agente LLM"] --> D_2["constrói sind_dict"];
        D_2 --> D_3["adiciona estados"];
        D_3 --> D_4["preenche valores"];
        D_4 --> D_5["Dicionário de Sindicatos<br>(sind_dict)"];
    end

    subgraph "Etapa 4: Auxiliares"
        E_1["Agente LLM"] --> E_2["Executa<br>obter_listas_auxiliares"];
        E_2 --> E_3["Listas Auxiliares"];
    end

    subgraph "Etapa 5: Cálculo VR"
        F_1["Agente LLM"] --> F_4;
        F_2["sind_dict"] --> F_4;
        F_3["Listas Auxiliares"] --> F_4["Executa<br>calcular_vr"];
        F_4 --> F_5["DataFrame com Resultados<br>(df)"];
    end

    subgraph "Etapa 6: Saída"
        G_1["DataFrame com Resultados<br>(df)"] --> G_2["Executa<br>salvar_resultado"];
        G_2 --> G_3["Arquivo Excel"];
    end

    B_3 --> C_1;
    C_3 --> D_1 & E_1 & F_1;
    D_5 --> F_2;
    E_3 --> F_3;
    F_5 --> G_1;
```
