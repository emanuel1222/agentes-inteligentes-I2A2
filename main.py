import os
import zipfile
import pandas as pd
from sqlalchemy import create_engine

from langchain_google_genai import ChatGoogleGenerativeAI # Alterado
from langchain_experimental.sql import SQLDatabaseChain # Mantido para compatibilidade, mas veja nota abaixo
from langchain.sql_database import SQLDatabase

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
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", temperature=0) 

    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

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
    
    db_dir = os.path.dirname(db_path) # Isso retornará "sqlite"

    # Cria o diretório se ele não existir
    if db_dir and not os.path.exists(db_dir): # Verifica se db_dir não é vazio antes de criar
        os.makedirs(db_dir)
        print(f"Diretório '{db_dir}' criado.")

    if not os.path.exists(zip_path):
        print(f"Arquivo {zip_path} não encontrado. Crie um arquivo zip com seus dados.")
        # Criando um dados.zip de exemplo para o código rodar
        print("Criando um dados.zip de exemplo com vendas.csv...")
        example_csv_content = "id,produto,valor\n1,caneta,10\n2,caderno,25\n3,caneta,12"
        with open("vendas.csv", "w") as f:
            f.write(example_csv_content)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.write("vendas.csv")
        os.remove("vendas.csv") # Limpa o CSV após zipar
        print(f"'{zip_path}' de exemplo criado. Você pode substituí-lo pelo seu arquivo real.")


    extract_zip_to_sqlite(zip_path, db_path)

    # Etapa 2: Criar agente
    agente = criar_agente(db_path)

    # Etapa 3: Perguntar
    pergunta = "Quantas tabelas existem no meu banco e qual o nome delas?"
    resposta = perguntar(agente, pergunta)
    print(f"\nPergunta: {pergunta}")
    print(f"Resposta: {resposta}")

    pergunta_2 = "Qual o valor da chave de acesso 53240150506565000113550010000000191368001919 ?"
    resposta_2 = perguntar(agente, pergunta_2)
    print(f"\nPergunta: {pergunta_2}")
    print(f"Resposta: {resposta_2}")

    pergunta_3 = "Quantos notas foram emitidas da serie '1' ?"
    resposta_3 = perguntar(agente, pergunta_3)
    print(f"\nPergunta: {pergunta_3}")
    print(f"Resposta: {resposta_3}")
    
    pergunta_4 = "Quantos foram notas foram emitidas em cada estado?"
    resposta_4 = perguntar(agente, pergunta_4)
    print(f"\nPergunta: {pergunta_4}")
    print(f"Resposta: {resposta_4}")