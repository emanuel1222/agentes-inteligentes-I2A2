import os
import zipfile
import pandas as pd
from sqlalchemy import create_engine

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

        try:
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                # Lê sem cabeçalho para inspecionar a primeira linha
                df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

                # Verifica se a primeira linha tem apenas a primeira coluna preenchida
                first_row = df_raw.iloc[0]
                if first_row.notna().sum() == 1 and pd.notna(first_row[0]):
                    header_row = 1  # Usa a segunda linha como cabeçalho
                else:
                    header_row = 0  # Mantém a primeira linha como cabeçalho

                # Lê o DataFrame novamente com o cabeçalho correto
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

                # Remove linhas totalmente vazias e linhas com a primeira coluna vazia
                df = df.dropna(how='all')
                df = df[df.iloc[:,0].notna()]

                # Limpar nome da tabela (remover espaços, caracteres especiais)
                base_table_name = os.path.splitext(file_name)[0].replace(" ", "_").replace("-", "_")
                if file_name == 'VR MENSAL 05.2025.xlsx':
                    print(f"Ignorando arquivo '{file_name}' conforme regra de exclusão.")
                    continue
                clean_sheet_name = sheet_name.replace(" ", "_").replace("-", "_")
                table_name = f"{base_table_name}_{clean_sheet_name}"

                df.to_sql(table_name, engine, if_exists='replace', index=False)
                print(f"Tabela '{table_name}' criada a partir da planilha '{sheet_name}' de '{file_name}'.")
        except Exception as e:
            print(f"Erro ao processar Excel: {e}")

    print("Banco de dados criado com sucesso!")