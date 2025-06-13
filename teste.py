
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from PIL import Image
import base64

# Funções auxiliares
def calcular_odds(prob):
    return round(1 / (prob / 100), 2) if prob > 0 else float('inf')

def kelly_formula(p, b):
    return max(((p * (b + 1) - 1) / b), 0)

def export_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Analise')
    return output.getvalue()

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Configuração inicial
st.set_page_config(page_title="Analista Esportivo Inteligente", layout="wide")

# 🔻 Imagem de fundo
background_image_base64 = get_base64_image("ChatGPTima.png")
st.markdown(
    f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{background_image_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }}
    .block-container {{
        background-color: rgba(0, 0, 0, 0.75);
        padding: 2rem;
        border-radius: 15px;
    }}
    input, textarea {{
        background-color: #111;
        color: white;
    }}
    </style>
    ''',
    unsafe_allow_html=True
)

# 🔻 Cabeçalho
st.markdown(
    '''
    <div style="padding: 30px; border-radius: 10px; color: white; margin-bottom: 30px;">
        <h1>⚽ Analista Esportivo Inteligente</h1>
        <p>Chat de análise esportiva com inteligência artificial.</p>
    </div>
    ''',
    unsafe_allow_html=True
)

# Chat de análise
st.subheader("🤖 Chat de Análise")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

prompt = st.chat_input("Digite o nome dos times ou sua dúvida de análise...")

if prompt:
    st.session_state.chat_history.append(("Usuário", prompt))
    if "x" in prompt.lower() or "vs" in prompt.lower():
        resposta = "Buscando dados dos times... (integração futura com SofaScore, Transfermarkt etc.)"
    else:
        resposta = "Ainda não entendi. Por favor, digite algo como: 'Flamengo x Palmeiras'"
    st.session_state.chat_history.append(("Sistema", resposta))

for autor, msg in st.session_state.chat_history:
    with st.chat_message("user" if autor == "Usuário" else "assistant"):
        st.markdown(msg)
