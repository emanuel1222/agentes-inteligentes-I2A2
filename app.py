import streamlit as st
from agente import extract_zip_to_df,  agente_plano
from util import executar_plano
st.set_page_config(page_title="Análise de Dados - Chat", layout="wide")

st.sidebar.header("📂 Carregar Dados")
uploaded_file = st.sidebar.file_uploader("Envie um arquivo .zip com seus dados", type=["zip"])

df = None

if uploaded_file is not None:
    with st.spinner("Extraindo dados..."):
        df = extract_zip_to_df(uploaded_file)
    st.session_state.df = df
    st.session_state.agente_plano = agente_plano()
    st.sidebar.success("✅ Arquivo carregado com sucesso!")
    st.sidebar.write("**Dimensões do DataFrame:**", df.shape)
    st.sidebar.write("**Colunas:**", list(df.columns))
else:
    st.sidebar.warning("Envie um arquivo ZIP para iniciar a análise.")

st.subheader("desafio extra")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Digite sua pergunta sobre os dados..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.df is None:
        resposta_final = "⚠️ Por favor, envie um arquivo ZIP primeiro."
    else:
        with st.spinner("Gerando resposta..."):
            executar_plano(
                agente_plano=st.session_state.agente_plano,
                df=st.session_state.df,
                pergunta=prompt
            )
