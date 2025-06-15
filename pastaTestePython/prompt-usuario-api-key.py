import sys
import io
import zipfile
import threading
import time
import pandas as pd
import requests  # Para chamar a API do Gemini
import json
import os
from typing import Optional

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
def descompactar_arquivo(zip_path: str, extract_to: str) -> None:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Arquivos descompactados em: {extract_to}")

# 2. Classe para interagir com a API do Gemini
class GeminiCSVAnalyzer:
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    def analyze_csv(self, csv_path: str, question: str, max_rows: int = 10) -> str:
        # Lê o CSV e extrai amostras (evitar enviar arquivos muito grandes)
        df = pd.read_csv(csv_path, encoding='utf-8')
        sample_data = df.head(max_rows).to_string(index=False)
        
        # Monta o prompt com contexto do CSV
        prompt = f"""
        Você é um assistente especializado em análise de dados. 
        Abaixo está uma amostra de um arquivo CSV (limite de {max_rows} linhas):

        {sample_data}

        Responda à seguinte pergunta baseada nos dados:
        Pergunta: {question}

        Dê uma resposta direta, clara e, se possível, com números ou insights específicos.
        """
        
        # Chama a API Gemini
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(
            f"{self.base_url}?key={self.api_key}",
            headers=headers,
            data=json.dumps(data)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Erro na API Gemini: {response.text}")

# 3. Processamento principal
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
                break
            else:
                print("Número inválido. Tente novamente.")
        except ValueError:
            print("Por favor, digite um número válido.")
    
    # Inicializar o Gemini (substitui o Ollama)
    gemini = GeminiCSVAnalyzer(api_key="SUA_CHAVE_DA_API_GEMINI")  # Substitua pela sua chave!
    loading = LoadingAnimation()

    # Loop de interação
    while True:
        pergunta = input("\nDigite sua pergunta sobre os dados (ou 'sair' para encerrar): ")
        if pergunta.lower() == 'sair':
            break
        
        try:
            loading.start()
            resposta = gemini.analyze_csv(arquivo_selecionado, pergunta)
            loading.stop()
            print("\nResposta Gemini:\n", resposta)
        except Exception as e:
            loading.stop()
            print(f"\nErro: {str(e)}")

if __name__ == "__main__":
    main()