from src.config import ZIP_PATH, DB_PATH
from src.extractor import extract_zip_to_sqlite
from src.agent import criar_agente
from src.processing import (
    construir_sind_dict,
    adicionar_estados_ao_sind_dict,
    preencher_valores_sind_dict,
    obter_listas_auxiliares,
    calcular_vr,
    salvar_resultado
)
import time

def main():
    print("📦 Extraindo ZIP e criando banco de dados...")
    extract_zip_to_sqlite(ZIP_PATH, DB_PATH)

    print("🤖 Criando agente LLM...")
    agent = criar_agente(DB_PATH)

    print("🧱 Construindo dicionário de sindicatos...")
    sind_dict = construir_sind_dict(agent)
    sind_dict = adicionar_estados_ao_sind_dict(sind_dict)
    sind_dict = preencher_valores_sind_dict(agent, sind_dict)

    print("📑 Coletando listas auxiliares...")
    listas_auxiliares = obter_listas_auxiliares(agent)

    print("📊 Calculando VR para funcionários...")
    df = calcular_vr(agent, sind_dict, listas_auxiliares)

    print("💾 Salvando resultado em Excel...")
    salvar_resultado(df)

    print("\n✅ Processo finalizado com sucesso!")

if __name__ == "__main__":
    main()
