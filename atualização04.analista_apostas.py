import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# Configuração inicial
st.set_page_config(page_title="Analista Esportivo Inteligente", layout="wide")
st.title("⚽ Analista Esportivo Inteligente")

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

# Entrada manual dos times e odds
st.subheader("📋 Dados do Jogo")
col1, col2 = st.columns([3, 1])
with col1:
    col_a, col_b = st.columns(2)
    with col_a:
        time_casa = st.text_input("Time da Casa", "Brasil")
    with col_b:
        time_fora = st.text_input("Time Visitante", "Argentina")
    col_c, col_d, col_e = st.columns(3)
    with col_c:
        odd_vitoria = st.number_input("Odd Vitória", value=1.80, step=0.01)
    with col_d:
        odd_empate = st.number_input("Odd Empate", value=3.20, step=0.01)
    with col_e:
        odd_derrota = st.number_input("Odd Derrota", value=4.00, step=0.01)
with col2:
    banca = st.number_input("💰 Saldo da Banca (R$)", value=100.0, step=10.0)

st.subheader(f"✅ CHECKLIST DE ANÁLISE DO JOGO: {time_casa} x {time_fora}")

# Perguntas reformuladas com saldo de vantagem
fatores = [
    ("Qual time teve desempenho superior nos últimos 5 jogos?", 5),
    ("Qual time tem média de gols marcados superior?", 4),
    ("Qual time sofre menos gols por jogo?", 4),
    ("Qual time mantém padrão tático e técnico?", 3),
    ("Qual time costuma dominar a posse de bola?", 3),
    ("Qual time teve mais dias de descanso?", 3),
    ("Qual time foi menos afetado por viagens recentes?", 2),
    ("Quem joga em casa com bom retrospecto?", 3),
    ("Qual time está em melhor condição física (sem desfalques importantes)?", 4),
    ("Qual time enfrenta mais desfalques importantes?", -4),
    ("Qual time precisa mais da vitória (objetivo na tabela)?", 3),
    ("Qual time tem histórico recente favorável neste confronto?", 2),
    ("Qual time está sob mais pressão externa (torcida/imprensa)?", -2),
    ("Qual time demonstra maior confiança (entrevistas/mídia)?", 2),
    ("Qual time está mais motivado ou com algo em jogo?", 2)
]

st.markdown("### 🧠 Selecione o time que leva vantagem em cada critério:")
probabilidade_base = 50
contribuicoes = []
saldo_time_casa = 0
saldo_time_fora = 0

for i, (pergunta, peso) in enumerate(fatores):
    with st.expander(f"{i+1}. {pergunta}"):
        escolha = st.radio("Quem leva vantagem?", ["Nenhum", time_casa, time_fora], key=pergunta)
        if escolha == time_casa:
            probabilidade_base += peso
            saldo_time_casa += peso
            contribuicoes.append(f"⬆️ {pergunta} → {time_casa} (+{peso}%)")
        elif escolha == time_fora:
            probabilidade_base -= peso
            saldo_time_fora += peso
            contribuicoes.append(f"⬇️ {pergunta} → {time_fora} (+{peso}%)")
        else:
            contribuicoes.append(f"⚖️ {pergunta} → Nenhuma vantagem (0%)")

# Cálculo de probabilidades
vitoria = min(90, max(10, probabilidade_base))
empate = 100 - vitoria - 20
derrota = 100 - vitoria - empate

st.markdown("### 🧮 Construção da Probabilidade Estimada")
for c in contribuicoes:
    st.markdown(f"- {c}")

# Saldo total
st.markdown(f"**📊 Saldo de Vantagem:** {time_casa}: {saldo_time_casa}% | {time_fora}: {saldo_time_fora}%**")
st.markdown(f"**🎯 Probabilidade final estimada de vitória do {time_casa}: {vitoria}%**")

# Odds justas com nomes dos times
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

# Cálculo de valor esperado e Kelly para vitória
st.subheader("⚙️ Valor Esperado e Stake Kelly (Vitória)")
valor_esperado = (vitoria / 100) * odd_vitoria - 1
kelly = kelly_formula(vitoria / 100, odd_vitoria - 1)
stake_kelly = banca * kelly

col1, col2, col3 = st.columns(3)
col1.metric(label="Valor Esperado (EV)", value=f"{valor_esperado:.2f}")
col2.metric(label="Stake Kelly (%)", value=f"{kelly * 100:.1f}%")
col3.metric(label="Stake R$", value=f"R$ {stake_kelly:.2f}")

# Recomendação
if valor_esperado > 0:
    st.success("✅ Aposta com valor positivo. Pode valer a pena apostar.")
elif valor_esperado == 0:
    st.info("⚠️ Aposta neutra. Sem valor esperado.")
else:
    st.warning("❌ Aposta com valor negativo. Evite apostar.")

# Comparação visual
st.subheader("📊 Comparação Visual: Odd Justa vs Mercado (Vitória)")
comparativo = pd.DataFrame({
    "Tipo": ["Odd Justa", "Odd Mercado"],
    "Valor": [odds_justas["Vitória"], odd_vitoria]
})
fig_bar = px.bar(comparativo, x="Tipo", y="Valor", color="Tipo", title="Comparativo de Odds")
st.plotly_chart(fig_bar, use_container_width=True)

# Exportação
st.subheader("📥 Exportar Dados")
excel_data = export_df_to_excel(df_prob)
st.download_button(label="📄 Baixar Tabela em Excel", data=excel_data, file_name="analise_apostas.xlsx")

# Notas
st.subheader("📝 Anotações do Analista")
comentarios = st.text_area("Comentários, observações ou insights sobre este jogo:", height=150)
