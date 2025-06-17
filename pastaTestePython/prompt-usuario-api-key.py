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

# Inicializar Gemini com memória
gemini = GeminiWithMemory(api_key=os.getenv("GEMINI_API_KEY")) 

def descompactar_arquivo(zip_path: str, extract_to: str) -> bool:
    if os.path.exists(extract_to) and any(f.endswith('.csv') for f in os.listdir(extract_to)):
        print(f"✓ Pasta '{extract_to}' já contém arquivos CSV. Pulando descompactação.")
        return False
    
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"✓ Arquivos descompactados em: {extract_to}")
    return True

def analyze_with_fallback(df, question: str):
    try:
        # Configuração para mostrar TODAS as colunas
        pd.set_option('display.max_columns', None)
        
        # Amostra com todas as colunas visíveis
        sample = df.sample(min(1000, len(df)))
        
        # Usando to_string() com configuração completa
        prompt = f"""
        Dados completos (amostra de {len(sample)} linhas):
        {sample.to_string(index=False, max_colwidth=20)}
        
        Pergunta: {question}
        """
        return gemini.generate_content(prompt)
        
    except Exception as e:
        # Fallback com cabeçalho completo
        cols = "\n".join(df.columns.tolist())
        return f"""
        Erro na análise: {str(e)}
        
        Cabeçalho completo:
        {cols}
        
        Por favor, refine sua pergunta.
        """

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
    
    loading = LoadingAnimation()

    # Loop de interação
    while True:
        pergunta = input(
            "\n'sair' para fechar o terminal" \
            "\n'limpar' para limpar o historico " \
            "\nDigite sua pergunta sobre os dados: "
        )
        if pergunta.lower() == 'sair':
            break

        if pergunta.lower() == 'limpar': 
            gemini.clear_history()
            continue
        
        try:
            loading.start()

            df = pd.read_csv(arquivo_selecionado, encoding='utf-8')

            resposta = analyze_with_fallback(df, pergunta)
            
            loading.stop()
            print("\nResposta:\n", resposta)
            
        except Exception as e:
            loading.stop()
            print(f"\nErro: {str(e)}")

if __name__ == "__main__":
    main()