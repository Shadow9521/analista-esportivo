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

# 🔻 Imagem de fundo na página inteira
background_image_base64 = get_base64_image("ChatGPTima.png")
st.markdown(
    f"""
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
    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stTextArea > div > textarea,
    .stRadio label,
    .stDownloadButton,
    .stButton button,
    .stMarkdown,
    .stMetric label,
    .stDataFrame,
    .stSelectbox label,
    .stSubheader,
    .stHeader {{
        color: white !important;
    }}
    input, textarea {{
        background-color: #111;
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 🔻 Cabeçalho
st.markdown(
    """
    <div style="padding: 30px; border-radius: 10px; color: white; margin-bottom: 30px;">
        <h1>⚽ Analista Esportivo Inteligente</h1>
        <p>Preencha os dados abaixo para começar a análise:</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 🔻 Entrada de dados
col_titulo, col_banca = st.columns([5, 1])
with col_titulo:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        time_casa = st.text_input("Time da Casa", "Brasil")
    with col_b:
        time_empate = st.text_input("Empate", "Empate", disabled=True)
    with col_c:
        time_fora = st.text_input("Time Visitante", "Argentina")

    col_d, col_e, col_f = st.columns(3)
    with col_d:
        odd_vitoria = st.number_input("Odd Vitória (Casa)", value=1.80, step=0.01)
    with col_e:
        odd_empate = st.number_input("Odd Empate", value=3.20, step=0.01)
    with col_f:
        odd_derrota = st.number_input("Odd Vitória (Visitante)", value=4.00, step=0.01)

with col_banca:
    st.markdown("#### 💼 Banca")
    banca = st.number_input("", value=100.0, step=10.0, label_visibility="collapsed")
    st.markdown("<small>Saldo da Banca (R$)</small>", unsafe_allow_html=True)

# 🔻 Checklist de Análise
fatores = [
    ("Quem tem o melhor goleiro?", 3),
    ("Quem tem os melhores zagueiros?", 3),
    ("Quem tem os melhores laterais?", 2),
    ("Quem tem os melhores volantes?", 2),
    ("Quem tem os melhores meias e atacantes?", 3),
    ("Quem tem jogadores mais habilidosos?", 2),
    ("Quem tem jogadores mais disciplinados taticamente?", 2),
    ("Quem joga em liga mais competitiva?", 3),
    ("Quem tem melhor técnico?", 3),
    ("Quem tem melhor ataque?", 4),
    ("Quem tem melhor defesa?", 4),
    ("Quem tem mais posse de bola durante os jogos?", 2),
    ("Quem tem mais camisa/tradição?", 2),
    ("Quem fez mais investimento no elenco?", 2),
    ("Quem joga em casa?", 3),
    ("Quem vem melhor nos últimos 5 jogos?", 4),
    ("É jogo de mata-mata, classificação ou liderança?", 2),
    ("Pode chover durante o jogo?", 1),
    ("O gramado é bom ou ruim?", 1)
]

st.subheader(f"✅ CHECKLIST DE ANÁLISE DO JOGO: {time_casa} x {time_fora}")
st.markdown("### 🧠 Responda cada critério de forma interativa:")

# Inicialização de estado
if 'etapa' not in st.session_state:
    st.session_state.etapa = 0
if 'respostas' not in st.session_state:
    st.session_state.respostas = []
if 'avancar' not in st.session_state:
    st.session_state.avancar = False

etapa = st.session_state.etapa
respostas = st.session_state.respostas

# Probabilidade parcial durante o checklist
probabilidade_base = 50 + sum([peso for peso, _ in respostas])
vitoria = min(90, max(10, probabilidade_base))
empate = 100 - vitoria - 20
derrota = 100 - vitoria - empate
odds_justas = {
    "Vitória": calcular_odds(vitoria),
    "Empate": calcular_odds(empate),
    "Derrota": calcular_odds(derrota)
}

data_grafico = pd.DataFrame({
    "Resultado": [time_casa, "Empate", time_fora],
    "Probabilidade": [vitoria, empate, derrota],
    "Odd": [odds_justas["Vitória"], odds_justas["Empate"], odds_justas["Derrota"]]
})

fig_bar = px.bar(
    data_grafico,
    x="Resultado",
    y="Probabilidade",
    text="Odd",
    color="Resultado",
    color_discrete_sequence=["#00cc96", "#636efa", "#ef553b"],
    title="Probabilidade Parcial Estimada + Odds Justas"
)
fig_bar.update_traces(texttemplate="Odd: %{text:.2f}", textposition="outside")
fig_bar.update_layout(yaxis_range=[0, 100], height=400)
st.plotly_chart(fig_bar, use_container_width=True)

if etapa < len(fatores):
    pergunta, peso = fatores[etapa]
    st.markdown(f"**{etapa + 1}/{len(fatores)}** - {pergunta}")
    escolha = st.radio("Quem leva vantagem?", ["Nenhum", time_casa, time_fora], key=f"etapa_{etapa}")

    if st.button("Próxima", key=f"btn_{etapa}"):
        st.session_state.avancar = True

    if st.session_state.avancar:
        if escolha == time_casa:
            respostas.append((peso, f"⬆️ {pergunta} → {time_casa} (+{peso}%)"))
        elif escolha == time_fora:
            respostas.append((-peso, f"⬇️ {pergunta} → {time_fora} (+{peso}%)"))
        else:
            respostas.append((0, f"⚖️ {pergunta} → Nenhuma vantagem (0%)"))
        st.session_state.etapa += 1
        st.session_state.respostas = respostas
        st.session_state.avancar = False
        st.rerun()

    st.progress(etapa / len(fatores))
