
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

# Checklist com pesos
checklist = {
    "Forma recente (últimos 5 jogos) favorável": 5,
    "Time joga em casa": 4,
    "Desfalques do adversário": 4,
    "Time completo e sem lesões": 3,
    "Motivação elevada (decisivo, clássico etc.)": 5,
    "Histórico favorável contra o adversário": 3,
    "Desempenho como mandante/visitante": 4,
    "Técnico mantém padrão tático e escalação": 3,
    "Situação na tabela exige vitória": 4,
    "Odd está acima da justa (valor)": 5,
    "Clima e gramado favorecem o time": 2,
    "Torcida pressionando adversário": 1,
    "Viagem longa/recentemente desgastante do adversário": 2,
    "Adversário já classificado ou rebaixado": 2,
    "Ausência de jogadores decisivos no adversário": 4,
    "Time poupando titulares para outro jogo": 3,
    "Confiança do time está alta (entrevista, mídia etc.)": 2,
    "Pressão sobre o adversário": 3,
    "Desempenho ofensivo superior": 4,
    "Sistema defensivo sólido": 4
}

st.subheader("🧠 Checklist de Confiança (20 Itens de Alta Relevância)")
cols = st.columns(4)
respostas = []
for i, (pergunta, peso) in enumerate(checklist.items()):
    col = cols[i % 4]
    marcado = col.checkbox(pergunta)
    respostas.append(peso if marcado else 0)

pontuacao_total = sum(checklist.values())
pontuacao_usuario = sum(respostas)
confianca_percentual = (pontuacao_usuario / pontuacao_total) * 100

st.markdown(f"**Pontuação de Confiança Total:** {pontuacao_usuario} / {pontuacao_total}")
st.progress(confianca_percentual / 100)

# Estimativas
vitoria = min(70, max(10, confianca_percentual))
empate = 100 - vitoria - 20
derrota = 100 - vitoria - empate

odds_justas = {
    "Vitória": calcular_odds(vitoria),
    "Empate": calcular_odds(empate),
    "Derrota": calcular_odds(derrota)
}

# Exibição
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
