# Análise de Dados - Chat (Desafio 5)

Este repositório contém uma aplicação em Streamlit que usa agentes (LangChain + Google Generative AI) para analisar um conjunto de dados enviado pelo usuário (ZIP com CSV/XLSX). A aplicação gera uma resposta textual e um plano de visualizações automáticas (histogramas, correlação, boxplots, etc.) e exibe gráficos e tabelas no próprio chat.

## Estrutura do projeto

- `app.py` - Interface Streamlit e fluxo principal (upload do ZIP, chat e execução do plano).
- `agente.py` - Cria agentes: um agente que interage com o DataFrame e outro que gera o plano de visualizações.
- `util.py` - Funções utilitárias para gerar tabelas e gráficos a partir do DataFrame.
- `requirements.txt` - Dependências Python do projeto.

## Pré-requisitos

- Python 3.10+ (ou compatível com as dependências do `requirements.txt`).
- Conta e chave de API do Google Generative AI (armazenar em variável de ambiente `GOOGLE_API_KEY`).
- Windows PowerShell (os exemplos de comando abaixo usam PowerShell).

## Instalação (Windows / PowerShell)

1. Abra o PowerShell na pasta do projeto (por exemplo `c:\i2a2\desafio 5`).

2. (Recomendado) Crie e ative um ambiente virtual:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```powershell
python -m pip install --upgrade pip; pip install -r requirements.txt
```

4. Configure a variável de ambiente com sua chave do Google Generative AI (exemplo temporário na sessão do PowerShell):

```powershell
$env:GOOGLE_API_KEY = "sua_chave_aqui"
```
Observação: para persistir a variável entre sessões, configure nas variáveis de ambiente do Windows.
4.1 Ou Adicione o arquivo .env na raiz do projeto e adicione a variavel `GOOGLE_API_KEY`

## Como executar

Execute a aplicação Streamlit:

```powershell
streamlit run app.py
```

- A interface abrirá no navegador (normalmente http://localhost:8501).
- No painel lateral, envie um arquivo ZIP contendo ao menos um arquivo CSV ou XLSX.
- Após o upload, use o chat (campo inferior) para digitar perguntas sobre os dados.
- A aplicação executará um agente para gerar a resposta textual e outro para sugerir um plano de visualizações (funções `util(df, tipo)`).

## Formato do ZIP esperado

- O ZIP deve conter arquivos `.csv` ou `.xlsx`. O primeiro CSV/XLSX encontrado será lido como DataFrame.
- Colunas numéricas são usadas automaticamente para gerar estatísticas e gráficos.

