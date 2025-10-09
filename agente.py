import os
import zipfile
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv() 
api_key = os.getenv("GOOGLE_API_KEY")

def extract_zip_to_df(zip_path: str):
    temp_dir = "temp_data"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    for file_name in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file_name)

        if file_name.endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"Erro ao processar CSV '{file_name}': {e}")

        elif file_name.endswith(".xlsx"):
            try:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = excel_file.parse(sheet_name)
            except Exception as e:
                print(f"Erro ao processar Excel '{file_name}', planilha '{sheet_name}': {e}")

    print("Data frames criados com sucesso")
    return df

def agente_plano():

    _CUSTOM_TEMPLATE = """
    Você é um planejador de análise de dados.
    Sua função é analisar uma **pergunta** feita sobre um DataFrame Pandas (`df`)
    e a **resposta textual** que já foi gerada, para decidir **quais funções da forma `util(df, tipo)`**
    poderiam gerar artefatos visuais (tabelas ou gráficos) que **complementem ou validem a resposta**.

    ### Tipos disponíveis em `util(df, tipo)`:
    - "hist" → mostra histogramas das variáveis numéricas.
    - "min_max" → exibe valores mínimos e máximos das colunas numéricas.
    - "typeof" → mostra tipos das variáveis no dataframe.
    - "mean_median" → mostra médias e medianas.
    - "std_var" → mostra desvio padrão e variância.
    - "outliers" → identifica possíveis outliers.
    - "correlation" → mostra matriz de correlação.
    - "scatter" → cria gráficos de dispersão entre variáveis.
    - "cluster" → identifica agrupamentos nos dados.

    ### Regras:
    1. Analise tanto a pergunta quanto a resposta.
    2. Indique apenas funções que realmente **ajudariam a entender, validar ou ilustrar** a resposta.
    3. Se nenhuma função for relevante, responda exatamente:
       "Não foi possível definir um plano."
    4. Sempre siga o formato JSON abaixo.

    Formato JSON OBRIGATÓRIO:
    {{
      "pergunta": "{input_pergunta}",
      "plano": [
        {{
          "acao": "util",
          "param": "<tipo>"
        }},
        {{
          "acao": "util",
          "param": "<tipo>"
        }}
      ],
      "resposta": "<Texto explicando o resultado com sucesso, relacione com as ações do plano.>"
    }}

    Se nenhuma função for aplicável:
    {{
      "pergunta": "...",
      "resposta": "...",
      "plano": [],
      "resposta_esperada": "Não foi possível definir um plano."
    }}

    Pergunta: {input_pergunta}
    Resposta: {input_resposta}
    """

    prompt = PromptTemplate(
        input_variables=["input_pergunta", "input_resposta"],
        template=_CUSTOM_TEMPLATE,
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite-preview-06-17")

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
    )

    return chain

def agente_dados(df): 
    from langchain_experimental.agents import create_pandas_dataframe_agent
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite-preview-06-17", temperature=0)

    PROMPT_SISTESE = """
    Você é um assistente de análise de dados.
    Sua tarefa é manipular um dataframe para descobrir e montar uma resposta textual coerente para a pergunta realizada.

    REGRAS:
    1. Se os dados forem insuficientes ou incoerentes, responda como se você tivesse conseguido de forma genérica e abrangente.
    2. Explique de forma clara, objetiva e em Português.

    Pergunta do usuário: {input}
    """

    agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=False,
    input_variables=["input"],
    agent_kwargs={"prompt": PROMPT_SISTESE},
    max_iterations=4,
    max_execution_time=10,
    allow_dangerous_code=True
    )

    return agent
