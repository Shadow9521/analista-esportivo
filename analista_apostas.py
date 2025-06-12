import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
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
col1, col2, col3 = st.columns(3)
with col1:
    time_casa = st.text_input("Time da Casa", "Brasil")
with col2:
    time_fora = st.text_input("Time Visitante", "Argentina")
with col3:
    banca = st.number_input("Saldo da Banca (R$)", value=100.0, step=10.0)

st.subheader("💸 Odds do Mercado")
col4, col5, col6 = st.columns(3)
with col4:
    odd_vitoria = st.number_input("Odd Vitória", value=1.80, step=0.01)
with col5:
    odd_empate = st.number_input("Odd Empate", value=3.20, step=0.01)
with col6:
    odd_derrota = st.number_input("Odd Derrota", value=4.00, step=0.01)

st.subheader(f"Análise do Jogo: {time_casa} x {time_fora}")

# Novo checklist binário com direção
st.subheader("🧠 Checklist Estratégico")

fatores = [
    ("Forma recente favorece", ["Nenhum", time_casa, time_fora], 5),
    ("Desfalques prejudicam", ["Nenhum", time_casa, time_fora], 4),
    ("Mando de campo influencia", ["Nenhum", time_casa, time_fora], 3),
    ("Motivação maior", ["Igual", time_casa, time_fora], 3),
    ("Pressão externa maior", ["Nenhuma", time_casa, time_fora], -2),
    ("Histórico de confronto favorece", ["Nenhum", time_casa, time_fora], 2),
    ("Desempenho ofensivo superior", ["Igual", time_casa, time_fora], 3),
    ("Sistema defensivo superior", ["Igual", time_casa, time_fora], 3),
    ("Adversário poupando titulares", ["Não", "Sim"], 2),
    ("Time completo e confiante", ["Nenhum", time_casa, time_fora], 2)
]

contribuicoes = []
probabilidade_base = 50

for fator, opcoes, peso in fatores:
    selecao = st.selectbox(f"{fator}:", opcoes, key=fator)
    if selecao == time_casa:
        probabilidade_base += peso
        contribuicoes.append(f"+{peso}% {fator} a favor do {time_casa}")
    elif selecao == time_fora:
        probabilidade_base -= peso
        contribuicoes.append(f"-{peso}% {fator} a favor do {time_fora}")

# Clampeia a probabilidade
vitoria = min(90, max(10, probabilidade_base))
empate = 100 - vitoria - 20
derrota = 100 - vitoria - empate

st.markdown("### 🧮 Construção da Probabilidade Estimada")
for item in contribuicoes:
    st.markdown(f"- {item}")
st.markdown(f"**→ Probabilidade final estimada: {vitoria}%**")

# Odds justas
odds_justas = {
    "Vitória": calcular_odds(vitoria),
    "Empate": calcular_odds(empate),
    "Derrota": calcular_odds(derrota)
}

st.subheader("📊 Probabilidades e Odds Justas")
df_prob = pd.DataFrame({
    "Resultado": ["Vitória", "Empate", "Derrota"],
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
