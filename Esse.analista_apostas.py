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

# Fatores Objetivos
st.markdown("### 1. 📊 Fatores Objetivos")
objetivos = [
    ("📈 Posição na Tabela:", f"{time_casa} é 3º | {time_fora} é 14º", time_casa, 6),
    ("🏆 Últimos 5 jogos:", f"{time_casa} 4V-1D | {time_fora} 1V-4D", time_casa, 5),
    ("📅 Calendário / Fadiga:", f"{time_casa} jogou há 7 dias | {time_fora} há 3", time_casa, 4),
    ("🩼 Desfalques:", f"{time_casa} completo | {time_fora} sem 2 zagueiros", time_casa, 5),
    ("🏠 Mando de Campo:", f"Jogo em casa favorece {time_casa}", time_casa, 3)
]

# Fatores Subjetivos
st.markdown("### 2. 🤔 Fatores Subjetivos (peso menor)")
subjetivos = [
    ("🧠 Motivação:", f"{time_casa} luta por Champions | {time_fora} contra rebaixamento", "Ambos", 2),
    ("📣 Pressão externa:", f"{time_casa} com apoio | {time_fora} sob vaias", time_casa, 2),
    ("🧑‍🏫 Técnico:", f"{time_casa} com treinador estável | {time_fora} trocou há 2 rodadas", time_casa, 2),
    ("🔥 Confiança:", f"{time_casa} em alta | {time_fora} pressionado", time_casa, 2)
]

# Lógica de construção
contribuicoes = []
probabilidade_base = 50

for titulo, descricao, favorecido, peso in objetivos + subjetivos:
    st.markdown(f"**{titulo}** {descricao}")
    if favorecido == time_casa:
        probabilidade_base += peso
        contribuicoes.append(f"✅ {titulo} +{peso}% a favor do {time_casa}")
    elif favorecido == time_fora:
        probabilidade_base -= peso
        contribuicoes.append(f"❌ {titulo} -{peso}% (vantagem do {time_fora})")
    elif favorecido == "Ambos":
        contribuicoes.append(f"⚠️ {titulo} Motivação para ambos os lados (sem alteração)")

vitoria = min(90, max(10, probabilidade_base))
empate = 100 - vitoria - 20
derrota = 100 - vitoria - empate

st.markdown("### 🧮 Construção da Probabilidade Estimada")
for c in contribuicoes:
    st.markdown(f"- {c}")
st.markdown(f"**🎯 Probabilidade final estimada de vitória do {time_casa}: {vitoria}%**")

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
