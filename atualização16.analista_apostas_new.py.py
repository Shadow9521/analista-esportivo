
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

# 🔻 Cabeçalho com imagem de fundo
background_image_base64 = get_base64_image("ChatGPTima.png")
st.markdown(
    f"""
    <style>
    .custom-header {{
        background-image: url(data:image/png;base64,{background_image_base64});
        background-size: cover;
        background-position: center;
        padding: 30px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }}
    .custom-header h1 {{
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }}
    .custom-header p {{
        font-size: 1.2em;
        margin: 0;
    }}
    </style>

    <div class="custom-header">
        <h1>⚽ Analista Esportivo Inteligente</h1>
        <p>Preencha os dados abaixo para começar a análise:</p>
    </div>
    """,
    unsafe_allow_html=True
)

# 🔻 Entrada manual dos times e odds
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

if 'etapa' not in st.session_state:
    st.session_state.etapa = 0
if 'respostas' not in st.session_state:
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
else:
    probabilidade_base = 50 + sum([r[0] for r in respostas])
    vitoria = min(90, max(10, probabilidade_base))
    empate = 100 - vitoria - 20
    derrota = 100 - vitoria - empate

    st.markdown("### 🧮 Construção da Probabilidade Estimada")
    for _, c in respostas:
        st.markdown(f"- {c}")

    saldo_time_casa = sum([r[0] for r, c in zip(respostas, fatores) if '⬆️' in c])
    saldo_time_fora = sum([-r[0] for r, c in zip(respostas, fatores) if '⬇️' in c])

    st.markdown(f"**📊 Saldo de Vantagem:** {time_casa}: {saldo_time_casa}% | {time_fora}: {saldo_time_fora}%**")
    st.markdown(f"**🎯 Probabilidade final estimada de vitória do {time_casa}: {vitoria}%**")

    odds_justas = {
        "Vitória": calcular_odds(vitoria),
        "Empate": calcular_odds(empate),
        "Derrota": calcular_odds(derrota)
    }

    st.subheader("📊 Probabilidades e Odds Justas")
    df_prob = pd.DataFrame({
        "Resultado": [
            f"Vitória {time_casa} 🏠",
            "Empate 🤝",
            f"Vitória {time_fora} 🛫"
        ],
        "Probabilidade (%)": [vitoria, empate, derrota],
        "Odd Justa": [odds_justas["Vitória"], odds_justas["Empate"], odds_justas["Derrota"]],
        "Odd Mercado": [odd_vitoria, odd_empate, odd_derrota]
    })
    st.dataframe(df_prob, use_container_width=True)

    fig = px.pie(df_prob, names='Resultado', values='Probabilidade (%)', title='Distribuição de Probabilidades')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚙️ Valor Esperado e Stake Kelly (Vitória)")
    valor_esperado = (vitoria / 100) * odd_vitoria - 1
    kelly = kelly_formula(vitoria / 100, odd_vitoria - 1)
    stake_kelly = banca * kelly

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Valor Esperado (EV)", value=f"{valor_esperado:.2f}")
    col2.metric(label="Stake Kelly (%)", value=f"{kelly * 100:.1f}%")
    col3.metric(label="Stake R$", value=f"R$ {stake_kelly:.2f}")

    if valor_esperado > 0:
        st.success("✅ Aposta com valor positivo. Pode valer a pena apostar.")
    elif valor_esperado == 0:
        st.info("⚠️ Aposta neutra. Sem valor esperado.")
    else:
        st.warning("❌ Aposta com valor negativo. Evite apostar.")

    st.subheader("📥 Exportar Dados")
    excel_data = export_df_to_excel(df_prob)
    st.download_button(label="📄 Baixar Tabela em Excel", data=excel_data, file_name="analise_apostas.xlsx")

    st.subheader("📝 Anotações do Analista")
    comentarios = st.text_area("Comentários, observações ou insights sobre este jogo:", height=150)

    st.markdown("---")
    col_restart, col_express = st.columns(2)
    with col_restart:
        if st.button("🔁 Reiniciar Checklist"):
            st.session_state.etapa = 0
            st.session_state.respostas = []
            st.experimental_rerun()
    with col_express:
        if st.button("⚡ Modo Rápido (5 perguntas)"):
            fatores = fatores[:5]
            st.session_state.etapa = 0
            st.session_state.respostas = []
            st.experimental_rerun()
