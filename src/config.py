import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ZIP_PATH = "data/Desafio 4 - Dados.zip"
DB_PATH = "sqlite/tarefa_4.db"
