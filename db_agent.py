import os
import zipfile
import pandas as pd
from sqlalchemy import create_engine

from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_experimental.sql import SQLDatabaseChain 
from langchain.sql_database import SQLDatabase
from langchain.prompts.prompt import PromptTemplate

from dotenv import load_dotenv

load_dotenv() 
api_key = os.getenv("GOOGLE_API_KEY")


def extract_zip_to_sqlite(zip_path: str, db_path: str):
    # Cria conexão com SQLite
    engine = create_engine(f'sqlite:///{db_path}')

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
                table_name = os.path.splitext(file_name)[0]
                df.to_sql(table_name, engine, if_exists='replace', index=False)
                print(f"Tabela '{table_name}' criada a partir de '{file_name}'.")
            except Exception as e:
                print(f"Erro ao processar CSV '{file_name}': {e}")


        elif file_name.endswith(".xlsx"):
            try:
                excel_file = pd.ExcelFile(file_path)
                for sheet_name in excel_file.sheet_names:
                    df = excel_file.parse(sheet_name)
                    # Limpar nome da tabela (remover espaços, caracteres especiais)
                    base_table_name = os.path.splitext(file_name)[0].replace(" ", "_").replace("-", "_")
                    clean_sheet_name = sheet_name.replace(" ", "_").replace("-", "_")
                    table_name = f"{base_table_name}_{clean_sheet_name}"
                    df.to_sql(table_name, engine, if_exists='replace', index=False)
                    print(f"Tabela '{table_name}' criada a partir da planilha '{sheet_name}' de '{file_name}'.")
            except Exception as e:
                print(f"Erro ao processar Excel '{file_name}', planilha '{sheet_name}': {e}")
    
    print("Banco de dados criado com sucesso!")

def criar_agente(db_path: str):
    # Usar ChatGoogleGenerativeAI com o modelo Gemini
    
    _CUSTOM_TEMPLATE = """
    Você é um assistente de dados. Dada uma pergunta, primeiro crie uma query {dialect} correta, depois analise o resultado da query e responda, direta e compreensível por humanos.

    Use o seguinte formato:

    Pergunta: "Aqui vai a pergunta"
    SQLQuery: "Consulta SQL"
    SQLResult: "Resultado da consulta"
    Resposta: "Resposta final aqui, de forma natural"

    Apenas use as tabelas abaixo:

    {table_info}

    Pergunta: {input}
    """

    CUSTOM_PROMPT = PromptTemplate(
    input_variables=["input", "table_info", "dialect"],
    template=_CUSTOM_TEMPLATE
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", temperature=0) 

    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=CUSTOM_PROMPT, verbose=True)

    return db_chain

def perguntar(db_chain, pergunta: str):
    try:
        resposta = db_chain.run(pergunta)
        return resposta
    except Exception as e:
        print(f"Erro ao executar a pergunta: {e}")
        # Tentar obter mais detalhes se for um erro de SQL gerado pelo LLM
        if "SQL:" in str(e) and "Error:" in str(e):
            print("Possívelmente o LLM gerou um SQL inválido.")
        return "Desculpe, não consegui processar sua pergunta devido a um erro."


if __name__ == "__main__":
    zip_path = "data/202401_NFs.zip"
    db_path = "sqlite/i2a2.db"

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if not os.path.exists(zip_path):
        print(f"Arquivo {zip_path} não encontrado.")
        exit()

    extract_zip_to_sqlite(zip_path, db_path)