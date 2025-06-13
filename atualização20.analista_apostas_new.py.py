# ✅ App completo com checklist manual + automático (Streamlit + scraping)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from PIL import Image
import base64
import requests
from bs4 import BeautifulSoup
import random

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

# ------------------------- Scraping automático -------------------------
def buscar_valor_elenco(url_time):
    headers = {'User-Agent': 'Mozilla/5.0'}
    html = requests.get(url_time, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    valor_div = soup.find("div", class_="dataMarktwert")
    if valor_div:
        return valor_div.get_text(strip=True)
    return "Não encontrado"

def comparar_valores(val_a, val_b, time_casa, time_fora):
    def converter(valor_str):
        if "mi" in valor_str:
            return float(valor_str.replace("€", "").replace("mi.", "").replace(",", ".").strip()) * 1_000_000
        elif "mil" in valor_str:
            return float(valor_str.replace("€", "").replace("mil.", "").replace(",", ".").strip()) * 1_000
        else:
            return 0

    va = converter(val_a)
    vb = converter(val_b)
    if va > vb:
        return +2, f"⬆️ Elenco mais valioso → {time_casa} ({val_a} vs {val_b})", val_a, val_b
    elif vb > va:
        return -2, f"⬇️ Elenco mais valioso → {time_fora} ({val_b} vs {val_a})", val_a, val_b
    else:
        return 0, f"⚖️ Elencos de valor similar ({val_a} = {val_b})", val_a, val_b

def simular_ultimos_jogos():
    return random.randint(2, 5)

# ------------------------- Interface -------------------------
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
<p>Preencha os dados abaixo para começar a análise:</p>
</div>
""", unsafe_allow_html=True)

# ------------------------- Entrada -------------------------
col1, col2 = st.columns([5, 1])
with col1:
    time_casa = st.text_input("Time da Casa", "Brasil")
    time_fora = st.text_input("Time Visitante", "Argentina")
    odd_vitoria = st.number_input("Odd Vitória (Casa)", value=1.80, step=0.01)
    odd_empate = st.number_input("Odd Empate", value=3.20, step=0.01)
    odd_derrota = st.number_input("Odd Vitória (Visitante)", value=4.00, step=0.01)
with col2:
    banca = st.number_input("💼 Banca", value=100.0, step=10.0)

# ------------------------- Modo de Análise -------------------------
modo = st.radio("Modo de Análise", ["Checklist Manual", "Checklist Automático"])

respostas = []
fatores = []
if modo == "Checklist Automático":
    st.subheader("🤖 Checklist Automático")

    url_time_casa = "https://www.transfermarkt.com.br/brasil/startseite/verein/3435"
    url_time_fora = "https://www.transfermarkt.com.br/argentinien/startseite/verein/3437"

    respostas.append((+3, f"🏠 Jogo em casa → {time_casa}"))

    valor_a = buscar_valor_elenco(url_time_casa)
    valor_b = buscar_valor_elenco(url_time_fora)
    peso_valor, texto_valor, val_a, val_b = comparar_valores(valor_a, valor_b, time_casa, time_fora)
    respostas.append((peso_valor, texto_valor))

    vitorias_a = simular_ultimos_jogos()
    vitorias_b = simular_ultimos_jogos()
    if vitorias_a > vitorias_b:
        respostas.append((+4, f"📈 Forma recente → {time_casa} ({vitorias_a} vs {vitorias_b})"))
    elif vitorias_b > vitorias_a:
        respostas.append((-4, f"📉 Forma recente → {time_fora} ({vitorias_b} vs {vitorias_a})"))
    else:
        respostas.append((0, f"⚖️ Forma recente igual ({vitorias_a} vitórias cada)"))

    st.markdown("### 📊 Dados coletados automaticamente")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/en/0/05/Flag_of_Brazil.svg", width=80)
        st.metric("Vitórias recentes", f"{vitorias_a}/5")
        st.metric("Valor de mercado", val_a)
    with col2:
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1a/Flag_of_Argentina.svg", width=80)
        st.metric("Vitórias recentes", f"{vitorias_b}/5")
        st.metric("Valor de mercado", val_b)

else:
    st.subheader("✅ Checklist Manual")
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
    if 'etapa' not in st.session_state:
        st.session_state.etapa = 0
        st.session_state.respostas = []

    etapa = st.session_state.etapa
    respostas = st.session_state.respostas

    if etapa < len(fatores):
        pergunta, peso = fatores[etapa]
        st.markdown(f"**{etapa + 1}/{len(fatores)}** - {pergunta}")
        escolha = st.radio("Quem leva vantagem?", ["Nenhum", time_casa, time_fora], key=pergunta)
        if st.button("Próxima"):
            if escolha == time_casa:
                respostas.append((peso, f"⬆️ {pergunta} → {time_casa} (+{peso}%)"))
            elif escolha == time_fora:
                respostas.append((-peso, f"⬇️ {pergunta} → {time_fora} (+{peso}%)"))
            else:
                respostas.append((0, f"⚖️ {pergunta} → Nenhuma vantagem (0%)"))
            st.session_state.etapa += 1
            st.session_state.respostas = respostas
        st.progress(etapa / len(fatores))

# ------------------------- Resultado final -------------------------
if respostas and (modo == "Checklist Automático" or st.session_state.etapa >= len(fatores)):
    st.markdown("### 📈 Resultado da Análise")
    for _, desc in respostas:
        st.markdown(f"- {desc}")

    total_peso = sum([r[0] for r in respostas])
    vitoria = min(90, max(10, 50 + total_peso))
    empate = 100 - vitoria - 20
    derrota = 100 - vitoria - empate

    df_prob = pd.DataFrame({
        "Resultado": [
            f"Vitória {time_casa} 🏠",
            "Empate 🤝",
            f"Vitória {time_fora} 🛫"
        ],
        "Probabilidade (%)": [vitoria, empate, derrota],
        "Odd Justa": [calcular_odds(vitoria), calcular_odds(empate), calcular_odds(derrota)],
        "Odd Mercado": [odd_vitoria, odd_empate, odd_derrota]
    })
    st.dataframe(df_prob, use_container_width=True)

    fig = px.pie(df_prob, names='Resultado', values='Probabilidade (%)', title='Distribuição de Probabilidades')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚙️ Stake Kelly")
    ev = (vitoria / 100) * odd_vitoria - 1
    kelly = kelly_formula(vitoria / 100, odd_vitoria - 1)
    stake = banca * kelly

    col1, col2, col3 = st.columns(3)
    col1.metric("Valor Esperado", f"{ev:.2f}")
    col2.metric("Stake Kelly (%)", f"{kelly * 100:.1f}%")
    col3.metric("Stake (R$)", f"R$ {stake:.2f}")
