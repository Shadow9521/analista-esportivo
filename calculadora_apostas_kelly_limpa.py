
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Calculadora de Apostas Inteligente", layout="centered")
st.title("🎯 Calculadora de Apostas com Fórmula de Kelly")

# Informações principais
st.header("📌 Dados da Aposta")

col1, col2 = st.columns(2)
with col1:
    time_analisado = st.selectbox("Analisar qual time?", ["Time da Casa", "Time Visitante"])
    odd_oferecida = st.number_input("Odd oferecida pela casa", min_value=1.01, step=0.01)
with col2:
    banca = st.number_input("Sua banca atual (R$)", min_value=10.0, step=10.0)
    mercado = st.selectbox("Mercado da aposta", ["Resultado Final", "Mais de 2.5 Gols", "Mais de 8.5 Escanteios", "Cartões"])

# Checklist direcionado
st.header("✅ Checklist de Confiança do " + time_analisado)

checklist = {
    "Está em boa fase nos últimos jogos?": 4,
    "Joga em casa (caso aplicável)?": 3,
    "Adversário com desfalques importantes?": 3,
    "Elenco completo e motivado?": 3,
    "Odd parece acima do justo?": 4,
    "Média de desempenho superior no mercado analisado?": 3,
    "Tática e postura favorecem esse mercado?": 2,
    "Pressão ou necessidade de vencer?": 3
}

cols = st.columns(2)
pontos = 0
peso_total = sum(checklist.values())
for i, (pergunta, peso) in enumerate(checklist.items()):
    if cols[i % 2].checkbox(pergunta):
        pontos += peso

confianca = (pontos / peso_total) * 100
prob_real = max(5, min(95, round(confianca)))  # Proteção para extremos
odd_justa = round(100 / prob_real, 2)
valor_esperado = (prob_real / 100) * odd_oferecida - 1
kelly = max(((prob_real / 100) * (odd_oferecida - 1) - (1 - prob_real / 100)) / (odd_oferecida - 1), 0)
stake_kelly = banca * kelly

# Resultados
st.header("📈 Resultado da Análise")

col1, col2, col3 = st.columns(3)
col1.metric("Probabilidade Real", f"{prob_real}%")
col2.metric("Odd Justa", f"{odd_justa}")
col3.metric("Valor Esperado", f"{valor_esperado:.2f}")

col4, col5 = st.columns(2)
col4.metric("Stake Kelly", f"R$ {stake_kelly:.2f}")
col5.metric("Recomendação", "Apostar" if valor_esperado > 0 else "Evitar")

# Gráfico de pizza
st.subheader("🎯 Distribuição de Confiança")
fig = px.pie(values=[prob_real, 100 - prob_real], names=["Sucesso", "Fracasso"], hole=0.4)
st.plotly_chart(fig, use_container_width=True)

# Observações
st.text_area("📝 Observações pessoais sobre o jogo")
