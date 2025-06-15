import sys
import io
import zipfile
import pandas as pd
import os
from dotenv import load_dotenv
from loading_animation import LoadingAnimation
from gemini_with_memory import GeminiWithMemory

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Carrega variáveis do .env
load_dotenv()

def descompactar_arquivo(zip_path: str, extract_to: str) -> bool:
    if os.path.exists(extract_to) and any(f.endswith('.csv') for f in os.listdir(extract_to)):
        print(f"✓ Pasta '{extract_to}' já contém arquivos CSV. Pulando descompactação.")
        return False
    
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✓ Arquivos descompactados em: {extract_to}")
    return True



def main():
    # Configurações
    zip_path = os.path.join("202401_NFs.zip")
    extract_to = os.path.join("dados_descompactados")
    
    # Descompactação (se necessário)
    descompactar_arquivo(zip_path, extract_to)
    
    # Listar CSVs
    arquivos_csv = [f for f in os.listdir(extract_to) if f.endswith('.csv')]
    print("\nArquivos CSV disponíveis:")
    for i, arquivo in enumerate(arquivos_csv, 1):
        print(f"{i}. {arquivo}")
    
    # Selecionar arquivo
    while True:
        try:
            escolha = int(input("\nSelecione o número do arquivo CSV: ")) - 1
            if 0 <= escolha < len(arquivos_csv):
                arquivo_selecionado = os.path.join(extract_to, arquivos_csv[escolha])
                pd.read_csv(arquivo_selecionado, encoding='utf-8')  # Validação
                break
            else:
                print("Número inválido.")
        except ValueError:
            print("Digite um número válido.")
    
    # Inicializar Gemini com memória
    gemini = GeminiWithMemory(api_key=os.getenv("GEMINI_API_KEY")) 
    loading = LoadingAnimation()

    # Loop de interação
    while True:
        pergunta = input("\nDigite sua pergunta sobre os dados (ou 'sair'): ")
        if pergunta.lower() == 'sair':
            break
        
        try:
            loading.start()
            
            # Carrega amostra do CSV para contexto
            df = pd.read_csv(arquivo_selecionado, encoding='utf-8')
            sample = df.head(5).to_string(index=False)
            
            # Combina pergunta + dados CSV
            prompt_completo = f"""
            Dados CSV (amostra de 5 linhas):
            {sample}

            Pergunta: {pergunta}
            """
            
            resposta = gemini.generate_content(prompt_completo)
            loading.stop()
            print("\nResposta:\n", resposta)
            
        except Exception as e:
            loading.stop()
            print(f"\nErro: {str(e)}")

if __name__ == "__main__":
    main()