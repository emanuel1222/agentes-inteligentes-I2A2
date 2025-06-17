import requests
import json

class GeminiWithMemory:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        self.history = []
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self._setup_analyst_context()

    def _setup_analyst_context(self):
        """Contexto permanente do analista de planilhas"""
        self.system_context = {
            "role": "system",
            "parts": [{
                "text": """Você é um analista especializado em Excel/CSVs com regras estritas:
                1. Para valores específicos: informe linha/coluna exatas
                2. Para 'primeiro/último': SEMPRE verifique todo o dataset
                3. Formato de resposta:
                   📍 Localização: (Linha X, Coluna Y)
                   🔍 Valor: [dado exato]
                   📊 Análise: [contexto]
                   ⚠️ Limitações: [avisos]"""
            }]
        }

    def generate_content(self, prompt: str) -> str:
        # Adiciona contexto do histórico (últimas 3 interações)
        context = "\n".join([f"Contexto: {h}" for h in self.history[-3:]]) if self.history else ""
        full_prompt = f"{context}\nPergunta: {prompt}" if context else prompt
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }
        
        response = requests.post(
            f"{self.base_url}?key={self.api_key}",
            headers=headers,
            data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            answer = result["candidates"][0]["content"]["parts"][0]["text"]
            self.history.append(f"Usuário: {prompt}\nIA: {answer}")  # Armazena no histórico
            return answer
        else:
            raise Exception(f"Erro na API Gemini: {response.text}")
        
    def clear_history(self):
        """Limpa todo o histórico de conversação"""
        self.history.clear()
        print("Histórico de memória foi resetado.")