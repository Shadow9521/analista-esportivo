
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analista Esportivo - Planilha Inteligente", layout="wide")
st.title("📊 Analista Esportivo - Preenchimento Manual")

# Seleção de mercado
mercado = st.selectbox("📌 Qual mercado deseja analisar?", [
    "Resultado Final (1X2)",
    "Mais de 2.5 Gols",
    "Mais de 8.5 Escanteios",
    "Cartões (Time com mais cartões)"
])

# Informações básicas
st.subheader("📋 Informações do Jogo")
col1, col2 = st.columns(2)
with col1:
    time1 = st.text_input("Nome do Time 1", value="Time A")
    desempenho_time1 = st.number_input("Vitórias nos últimos 5 jogos (Time 1)", 0, 5, 3)
with col2:
    time2 = st.text_input("Nome do Time 2", value="Time B")
    desempenho_time2 = st.number_input("Vitórias nos últimos 5 jogos (Time 2)", 0, 5, 2)

# Odd de mercado
st.subheader("💸 Odd oferecida pela casa")
odd_casa = st.number_input("Odd da aposta que deseja analisar", min_value=1.01, step=0.01)

# Checklist com pesos
st.subheader("✅ Checklist de Confiança (Preencha com base no cenário atual)")
checklist = {
    "Time analisado está em boa fase?": 4,
    "Joga em casa?": 3,
    "O adversário tem desfalques?": 3,
    "Odd oferecida parece generosa?": 4,
    "Motivação (precisa da vitória, clássico, etc.)": 3,
    "Técnico e elenco estão estáveis?": 2,
    "Boa média de gols ou escanteios (conforme o mercado)?": 3,
    "Leitura tática favorece o time analisado?": 2
}

cols = st.columns(4)
pontuacao = 0
peso_total = sum(checklist.values())
for i, (pergunta, peso) in enumerate(checklist.items()):
    if cols[i % 4].checkbox(pergunta):
        pontuacao += peso

confianca_percentual = (pontuacao / peso_total) * 100
st.markdown(f"**Confiança calculada:** {confianca_percentual:.1f}%")
st.progress(confianca_percentual / 100)

# Cálculo de probabilidade real e odd justa
prob_real = min(80, max(5, round(confianca_percentual)))  # Limitada para simulação
odd_justa = round(100 / prob_real, 2)
valor_esperado = (prob_real / 100) * odd_casa - 1

st.subheader("📈 Resultado da Análise")
col1, col2, col3 = st.columns(3)
col1.metric("Probabilidade Real", f"{prob_real:.1f}%")
col2.metric("Odd Justa", f"{odd_justa:.2f}")
col3.metric("Valor Esperado (EV)", f"{valor_esperado:.2f}")

# Recomendação baseada no valor esperado
if valor_esperado > 0:
    st.success("✅ Aposta com valor positivo. Boa oportunidade!")
elif valor_esperado == 0:
    st.info("⚠️ Aposta neutra. Analise com cuidado.")
else:
    st.warning("❌ Valor negativo. Evite esta aposta.")

# Gráfico ilustrativo
st.subheader("📊 Visualização da Probabilidade")
fig = px.pie(values=[prob_real, 100 - prob_real], names=["Sucesso", "Fracasso"],
             title="Distribuição de Probabilidade Real")
st.plotly_chart(fig, use_container_width=True)

# Campo para observações
st.text_area("📝 Observações pessoais do analista", placeholder="Digite aqui suas anotações...")
