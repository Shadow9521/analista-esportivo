# ✅ Novo app com 3 fases: odds > checklist > resultado final
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from PIL import Image
import base64

# ------------------------- Funções auxiliares -------------------------
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

# ------------------------- Configuração -------------------------
st.set_page_config(page_title="Analista Esportivo Inteligente", layout="wide")
background_image_base64 = get_base64_image("ChatGPTima.png")
st.markdown(f"""
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
    input, textarea {{ background-color: #111; color: white; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="padding: 30px; color: white">
<h1>⚽ Analista Esportivo Inteligente</h1>
<p>Preencha os dados de mercado e siga as etapas para análise.</p>
</div>
""", unsafe_allow_html=True)

# ------------------------- Sessão e Fases -------------------------
if 'fase' not in st.session_state:
    st.session_state.fase = 1
if 'etapa' not in st.session_state:
    st.session_state.etapa = 0
if 'respostas' not in st.session_state:
    st.session_state.respostas = []

# ------------------------- FASE 1: Inserir odds -------------------------
if st.session_state.fase == 1:
    st.header("🔢 Etapa 1: Informações do jogo e Odds")
    col1, col2 = st.columns([4, 1])
    with col1:
        time_casa = st.text_input("Time da Casa", "Brasil")
        time_fora = st.text_input("Time Visitante", "Argentina")
        odd_vitoria = st.number_input("Odd Vitória (Casa)", value=1.80, step=0.01)
        odd_empate = st.number_input("Odd Empate", value=3.20, step=0.01)
        odd_derrota = st.number_input("Odd Vitória (Visitante)", value=4.00, step=0.01)
    with col2:
        banca = st.number_input("💼 Banca (R$)", value=100.0, step=10.0)

    if st.button("➡️ Continuar para Checklist"):
        st.session_state.fase = 2
        st.rerun()

# ------------------------- FASE 2: Checklist -------------------------
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
    ("Quem tem melhor ataque?", 4)
]

if st.session_state.fase == 2:
    etapa = st.session_state.etapa
    respostas = st.session_state.respostas

    st.header(f"🧠 Etapa 2: Checklist {etapa + 1}/{len(fatores)}")

    if etapa < len(fatores):
        pergunta, peso = fatores[etapa]
        escolha = st.radio(f"{pergunta}", ["Nenhum", "Casa", "Visitante"], key=f"etapa_{etapa}")
        if st.button("Próxima"):
            if escolha == "Casa":
                respostas.append((peso, f"⬆️ {pergunta} → Casa (+{peso}%)"))
            elif escolha == "Visitante":
                respostas.append((-peso, f"⬇️ {pergunta} → Visitante (+{peso}%)"))
            else:
                respostas.append((0, f"⚖️ {pergunta} → Nenhuma vantagem"))
            st.session_state.etapa += 1
            st.session_state.respostas = respostas
            st.rerun()
        st.progress(etapa / len(fatores))
    else:
        st.session_state.fase = 3
        st.rerun()

# ------------------------- FASE 3: Resultado Final -------------------------
if st.session_state.fase == 3:
    st.header("📊 Etapa 3: Resultado da Análise")
    respostas = st.session_state.respostas
    for _, msg in respostas:
        st.markdown(f"- {msg}")

    saldo_casa = sum([peso for peso, msg in respostas if '⬆️' in msg])
    saldo_fora = sum([-peso for peso, msg in respostas if '⬇️' in msg])

    prob_casa = max(0, 50 + saldo_casa)
    prob_fora = max(0, 50 + saldo_fora)
    total = prob_casa + prob_fora
    vitoria = round((prob_casa / total) * 100, 1) if total > 0 else 50
    derrota = round((prob_fora / total) * 100, 1) if total > 0 else 50
    empate = round(100 - vitoria - derrota, 1)

    st.subheader("📈 Probabilidades e Odds Justas")
    df_prob = pd.DataFrame({
        "Resultado": ["Vitória Casa", "Empate", "Vitória Visitante"],
        "Probabilidade (%)": [vitoria, empate, derrota],
        "Odd Justa": [calcular_odds(vitoria), calcular_odds(empate), calcular_odds(derrota)],
        "Odd Mercado": [odd_vitoria, odd_empate, odd_derrota]
    })
    st.dataframe(df_prob, use_container_width=True)

    st.plotly_chart(px.pie(df_prob, names='Resultado', values='Probabilidade (%)', title='Distribuição de Probabilidades'), use_container_width=True)

    st.subheader("💡 Fórmula de Kelly")
    ev = (vitoria / 100) * odd_vitoria - 1
    kelly = kelly_formula(vitoria / 100, odd_vitoria - 1)
    stake = banca * kelly

    col1, col2, col3 = st.columns(3)
    col1.metric("Valor Esperado (EV)", f"{ev:.2f}")
    col2.metric("Stake Kelly (%)", f"{kelly * 100:.1f}%")
    col3.metric("Stake (R$)", f"R$ {stake:.2f}")

    st.markdown("---")
    if st.button("🔁 Recomeçar"):
        st.session_state.fase = 1
        st.session_state.etapa = 0
        st.session_state.respostas = []
        st.rerun()
