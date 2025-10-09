import pandas as pd
import itertools
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import json
import re
import multiprocessing

from scipy.stats import kurtosis, skew

from agente import agente_dados

def util(df: pd.DataFrame, tipo: str = None):
    df_num = df.select_dtypes(include=np.number)

    if tipo == "typeof":
      result = df.dtypes.to_frame()
      return result, None

    if tipo == "hist":
      fig, ax = plt.subplots(figsize=(20, 20))
      df_num.hist(ax=ax, bins=20) 
      return None, fig

    elif tipo == "min_max":
        result = df_num.agg(['min', 'max'])
        return plot_min_max(df_num)

    elif tipo == "mean_median":
        result = df_num.agg(['mean', 'median'])
        return None, plot_boxplot(df_num)

    elif tipo == "std_var":
        result = df_num.agg(['std', 'var'])
        return plot_dispersion(result)

    elif tipo == "outliers":
        z_scores = (df_num - df_num.mean()) / df_num.std()
        mask = (np.abs(z_scores) > 3)
        result = df[mask.any(axis=1)]  # mantém apenas linhas com algum outlier
        return result, None

    elif tipo == "correlation":
        corr = df_num.corr()
        fig, ax = plt.subplots(figsize=(20, 16))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax)
        ax.set_title("Matriz de Correlação")
        return None, fig

    elif tipo == "cluster":
        stats = []
        for col in df_num.columns:
            data = df_num[col].dropna()
            if len(data) < 5:
                continue
            k = kurtosis(data)
            s = skew(data)
            has_cluster = abs(s) > 1 or k > 3  # regra simples para indicar cluster
            stats.append({
                "variavel": col,
                "possui_cluster": "Sim" if has_cluster else "Não",
                "curtose": k,
                "assimetria": s
            })

        if not stats:
            return pd.DataFrame([{"resultado": "Dados insuficientes"}]), None

        result = pd.DataFrame(stats)

        # ✅ Correção aqui — cria fig e ax corretamente
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(result["variavel"], result["curtose"])
        ax.set_title("Curtose das variáveis (indício de clusters)")
        ax.set_xticklabels(result["variavel"], rotation=45)
        plt.tight_layout()

        return result, fig

    elif tipo == "scatter":
        colunas = df_num.columns
        colunas_sortidas = np.random.choice(colunas, size=min(4, len(colunas)), replace=False)
        pares = list(itertools.combinations(colunas_sortidas, 2))

        n_colunas_por_linha = 3
        n_linhas = math.ceil(len(pares) / n_colunas_por_linha)

        fig, axes = plt.subplots(n_linhas, n_colunas_por_linha, figsize=(20, 5 * n_linhas))
        axes = axes.flatten()

        for i, (x_col, y_col) in enumerate(pares):
            axes[i].scatter(df_num[x_col], df_num[y_col])
            axes[i].set_xlabel(x_col)
            axes[i].set_ylabel(y_col)
            axes[i].set_title(f'{x_col} x {y_col}')

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()
        return None, fig

    else:
        return None, None

def plot_min_max(df_num):
    result = df_num.agg(['min', 'max'])
    fig, ax = plt.subplots(figsize=(10, 6))
    
    width = 0.35
    indices = range(len(result.columns))
    
    # barras min e max
    ax.bar([i - width/2 for i in indices], result.loc['min'], width, label='Min', color='skyblue')
    ax.bar([i + width/2 for i in indices], result.loc['max'], width, label='Max', color='orange')
    
    # linha zero
    ax.axhline(0, color='black', linewidth=0.8)
    
    # rótulos do eixo X
    ax.set_xticks(indices)
    ax.set_xticklabels(result.columns, rotation=45, ha='right')
    ax.set_ylabel('Valores')
    ax.set_title('Valores Mínimos e Máximos por Coluna (Escala Symlog)')
    ax.legend()
    
    # escala simétrica log
    ax.set_yscale('symlog', linthresh=1)  # linthresh define a região linear perto de zero
    
    # adiciona valores nas barras
    for i, v in enumerate(result.loc['min']):
        va = 'bottom' if v >= 0 else 'top'
        ax.text(i - width/2, v, f"{v:.2f}", ha='center', va=va, fontsize=8)
    for i, v in enumerate(result.loc['max']):
        ax.text(i + width/2, v, f"{v:.2f}", ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    return None, fig

def plot_dispersion(df_num):
    stats = df_num.agg(['std', 'var']).T

    fig, ax = plt.subplots(figsize=(10, 6))
    stats.plot(kind='bar', ax=ax)

    ax.set_yscale('symlog', linthresh=1)  # linthresh define a zona "linear" perto de 0

    ax.set_title('Desvio Padrão e Variância por Coluna', fontsize=14, fontweight='bold')
    ax.set_xlabel('Colunas')
    ax.set_ylabel('Valor')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    return stats, fig 

def plot_boxplot(df_num):
    fig, ax = plt.subplots(figsize=(10, 6))

    # cria o boxplot
    df_num.boxplot(ax=ax)

    # aplica escala simétrica logarítmica
    ax.set_yscale('symlog', linthresh=1)  # linthresh define a zona "linear" perto de 0

    # título e rótulos
    ax.set_title('Boxplot com Escala Logarítmica Simétrica (symlog)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Valor (escala simétrica log)', fontsize=12)

    # grade e estilo
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    return 

def executar_plano(agente_plano, df, pergunta: str):
    """
    Executa os agentes e exibe o resultado diretamente no Streamlit.
    - Mostra a resposta textual principal
    - Mostra o plano sugerido pelo segundo agente
    - Executa as funções util(df, tipo) e exibe gráficos/tabelas no chat
    """

    with st.chat_message("assistant"):
        # 1️⃣ Executa o agente de dados
        st.markdown("🔹 **Analisando dados...**")
        raw_resposta = run_with_timeout_process(df, pergunta, timeout_sec=10)
        print("raw_resposta", raw_resposta)

        # garante que seja string
        if isinstance(raw_resposta, dict):
            resposta_textual = raw_resposta.get("output", str(raw_resposta)) or str(raw_resposta)
        else:
            resposta_textual = str(raw_resposta)

        # 2️⃣ Executa o agente de plano
        st.markdown("🔹 **Gerando plano de visualizações...**")
        plano_json = agente_plano.invoke({
            "input_pergunta": pergunta,
            "input_resposta": resposta_textual
        })

        # Tenta limpar o JSON
        try:
            json_text = limpar_json(plano_json)
            plano = json.loads(json_text)
        except Exception as e:
            print("json_text", plano_json)
            st.warning(f"⚠️ Erro ao converter plano em JSON: {e}")
            st.code(plano_json)
            plano = {"plano": []}

        # Exibe plano textual
        if plano and plano.get("plano"):
            for passo in plano["plano"]:
                print(f"- `util(df, '{passo.get('param')}')`")
                #st.write(f"- `util(df, '{passo.get('param')}')`")
            ##st.markdown({plano.get('resposta_esperada', '')})

        # 3️⃣ Executa e mostra as funções util(df, tipo)
        for passo in plano["plano"]:
            tipo = passo.get("param")
            try:
                df_result, grafico = util(df, tipo)

                if df_result is not None:
                    st.dataframe(df_result)

                if grafico is not None:
                    st.pyplot(grafico)

            except Exception as e:
                st.error(f"❌ Erro ao executar `util(df, '{tipo}')`: {e}")
        st.markdown(f"**🧠 Resposta:** {resposta_textual}")

        st.success("✅ Execução concluída com sucesso.")

def limpar_json(texto):
    """
    Remove blocos markdown e tenta extrair o JSON puro do texto.
    Aceita string ou dict (extraindo 'text' se for dict).
    """
    if not texto:
        return "{}"

    # se for dict, tenta pegar o campo 'text' ou 'output'
    if isinstance(texto, dict):
        texto = texto.get("text") or texto.get("output") or str(texto)

    # remove blocos tipo ```json ... ``` ou ``` ... ```
    texto_limpo = re.sub(r"```(?:json)?", "", texto, flags=re.IGNORECASE).strip()

    # tenta extrair apenas o JSON (caso tenha texto antes/depois)
    match = re.search(r"\{.*\}", texto_limpo, flags=re.DOTALL)
    if match:
        return match.group(0)
    return texto_limpo.strip()

def run_agent_in_process(df, pergunta):
    agente = agente_dados(df)         # cria o agente aqui dentro
    return agente.invoke({"input": pergunta})

def run_with_timeout_process(df, pergunta, timeout_sec=10):
    with multiprocessing.Pool(1) as pool:
        result = pool.apply_async(run_agent_in_process, args=(df, pergunta))
        try:
            return result.get(timeout=timeout_sec)
        except multiprocessing.TimeoutError:
            return "⚠️ Tempo limite excedido. Não foi possível gerar a resposta."
