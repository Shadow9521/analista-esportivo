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

# Perguntas mais inteligentes com escolha entre os times
fatores = [
    ("O time teve desempenho superior nos últimos 5 jogos?", 5),
    ("O time tem média de gols marcados superior ao adversário?", 4),
    ("O time sofre menos gols por jogo que o adversário?", 4),
    ("O padrão tático é mantido (mesmo técnico e estilo)?", 3),
    ("O time costuma dominar a posse de bola?", 3),
    ("O time teve mais dias de descanso que o adversário?", 3),
    ("O adversário fez viagem longa ou cansativa recentemente?", 2),
    ("O time joga em casa com bom retrospecto como mandante?", 3),
    ("O time está completo (sem desfalques importantes)?", 3),
    ("O adversário tem jogadores suspensos ou lesionados?", 3),
    ("O time precisa vencer por objetivo na tabela (título, vaga, etc)?", 3),
    ("O time tem histórico recente de vitórias sobre este adversário?", 2),
    ("O adversário está sob pressão da torcida ou imprensa?", 2),
    ("O elenco demonstrou confiança em entrevistas ou mídia?", 2),
    ("O adversário já está classificado ou sem motivação?", 2)
]

st.markdown("### 🧠 Selecione quem é favorecido em cada critério:")
probabilidade_base = 50
contribuicoes = []

for i, (pergunta, peso) in enumerate(fatores):
    with st.expander(f"{i+1}. {pergunta}"):
        escolha = st.radio("Quem leva vantagem?", ["Nenhum", time_casa, time_fora], key=pergunta)
        if escolha == time_casa:
            probabilidade_base += peso
            contribuicoes.append(f"✅ {pergunta} → {time_casa} (+{peso}%)")
        elif escolha == time_fora:
            probabilidade_base -= peso
            contribuicoes.append(f"❌ {pergunta} → {time_fora} (-{peso}%)")
        else:
            contribuicoes.append(f"⚠️ {pergunta} → Nenhum dos dois (0%)")

# Cálculo de probabilidades
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
