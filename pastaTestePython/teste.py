import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # Fix para encoding

from langchain_ollama import OllamaLLM  # Importação correta!
from langchain_core.prompts import ChatPromptTemplate

# Configuração do modelo
llm = OllamaLLM(model="deepseek-r1:14b")  # Note o novo nome da classe

# Prompt template
prompt = ChatPromptTemplate.from_template("Responda como um cientista: {pergunta}")
chain = prompt | llm

# Execução
resposta = chain.invoke({"pergunta": "Explique a teoria da relatividade."})
print(resposta)