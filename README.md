# Projeto VR Mensal

Este projeto processa planilhas contidas em um arquivo ZIP, carrega os dados em um banco SQLite, 
faz consultas usando um LLM (Google Gemini via LangChain) e gera uma planilha final com os valores de VR para cada funcionário.

## Estrutura de Pastas
````
meu_projeto_vr/
├── data/
│ └── desafio-4.zip
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

bash
Copy code

## Como Rodar

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv

source .venv/bin/activate   # Linux/Mac

.venv\Scripts\activate      # Windows
````

2. Instale as dependências:

````
pip install -r requirements.txt
````

3. Crie um arquivo .env na raiz do projeto com sua chave da API do Google:

````
GOOGLE_API_KEY=sua_chave_aqui
````

4. Coloque o arquivo desafio-4.zip dentro da pasta data/.

5. Execute o projeto:

````
python -m src.main
````