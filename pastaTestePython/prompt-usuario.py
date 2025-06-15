import sys
import io
import zipfile
import threading
import time
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_experimental.agents import create_csv_agent
from langchain.agents.agent_types import AgentType
import os

class LoadingAnimation:
    def __init__(self):
        self._loading = False
        self._thread = None
        
    def _animate(self):
        while self._loading:
            for i in range(4):
                if not self._loading: break
                sys.stdout.write('\rProcessando' + '.' * i + '   ')
                sys.stdout.flush()
                time.sleep(0.3)
        sys.stdout.write('\r' + ' ' * 20 + '\r')  # Limpa a linha
    
    def start(self):
        self._loading = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._loading = False
        if self._thread:
            self._thread.join(timeout=0.5)

# Configuração do encoding para evitar problemas com caracteres especiais
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Descompactar o arquivo ZIP
def descompactar_arquivo(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Arquivos descompactados em: {extract_to}")

# 2. Configuração do modelo Ollama (DeepSeek-R1)
llm = OllamaLLM(model="deepseek-r1:14b")

# 3. Criar agente para CSV
def criar_agente_csv(caminho_csv):
    return create_csv_agent(
        llm,
        caminho_csv,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        allow_dangerous_code=True,
        agent_executor_kwargs={
            "handle_parsing_errors": True  # Agora vai aqui dentro
        }
    )

# 4. Processamento principal
def main():
    # Configurações de caminho
    zip_path = os.path.join("202401_NFs.zip")
    extract_to = os.path.join("dados_descompactados")
    os.makedirs(extract_to, exist_ok=True)
    
    # Descompactar arquivos
    descompactar_arquivo(zip_path, extract_to)
    
    # Listar arquivos CSV disponíveis
    arquivos_csv = [f for f in os.listdir(extract_to) if f.endswith('.csv')]
    print("\nArquivos CSV disponíveis:")
    for i, arquivo in enumerate(arquivos_csv, 1):
        print(f"{i}. {arquivo}")
    
    # Selecionar arquivo
    while True:
        try:
            escolha = int(input("\nSelecione o número do arquivo CSV que deseja analisar: ")) - 1
            if 0 <= escolha < len(arquivos_csv):
                arquivo_selecionado = os.path.join(extract_to, arquivos_csv[escolha])
                pd.read_csv(arquivo_selecionado, encoding='utf-8')  # ou encoding='latin1', 'iso-8859-1', etc

                break
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")
    
    # Criar agente para o arquivo selecionado
    agente = criar_agente_csv(arquivo_selecionado)
    
    loading = LoadingAnimation()  # Mova para dentro do main()

    # Loop de interação com o usuário
    while True:
        pergunta = input("\nDigite sua pergunta sobre os dados (ou 'sair' para encerrar): ")
        
        if pergunta.lower() == 'sair':
            break
        
        try:
            
            resposta = agente.invoke(pergunta)
            
            print("\nResposta:", resposta)

        except Exception as e:
            
            print(f"\nOcorreu um erro ao processar sua pergunta: {str(e)}")

if __name__ == "__main__":
    main()