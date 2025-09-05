from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain.sql_database import SQLDatabase
from langchain.prompts.prompt import PromptTemplate

def criar_agente(db_path: str):
    # Usar ChatGoogleGenerativeAI com o modelo Gemini

    _CUSTOM_TEMPLATE = """
    Você é um assistente de dados. Responsavel por retornar dados brutos SQLResult para uma proxima etapa do pipe. Dada uma pergunta, primeiro crie uma query {dialect} correta, depois analise o resultado da query e SEMPRE responda de forma direta apenas o SQLResult.

    Use o seguinte formato:

    SQLResult: "Resultado da consulta"

    Apenas use as tabelas abaixo:

    {table_info}

    Pergunta: {input}
    """

    CUSTOM_PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect"],
    template=_CUSTOM_TEMPLATE
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite-preview-06-17", temperature=0)

    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=CUSTOM_PROMPT, verbose=True, return_direct=True)

    return db_chain
