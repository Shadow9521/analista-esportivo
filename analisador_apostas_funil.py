
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configuração inicial
st.set_page_config(page_title="Analisador de Apostas - Funil Inteligente", layout="wide")

st.title("🎯 Analisador de Apostas Esportivas")

# Função para calcular odds justas
def calcular_odds(prob):
    return round(100 / prob, 2) if prob > 0 else float("inf")

# Função de Kelly
def kelly_formula(p, b):
    return max(((p * (b + 1) - 1) / b), 0)

# Etapas em abas
aba = st.sidebar.radio("🔍 Etapas da Análise", ["1. Dados do Jogo", "2. Análise de Confiança e Kelly"])

# Sessão de estado
if "analise" not in st.session_state:
    st.session_state.analise = {
        "time_casa": "",
        "time_fora": "",
        "mercado": "",
        "odd_casa": 1.80
    }

# Etapa 1: Preenchimento do Jogo e Odds
if aba == "1. Dados do Jogo":
    st.subheader("📋 Informações do Jogo")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.analise["time_casa"] = st.text_input("Nome do Time da Casa", "Time A")
        st.session_state.analise["time_fora"] = st.text_input("Nome do Time Visitante", "Time B")
    with col2:
        st.session_state.analise["mercado"] = st.selectbox("Mercado da Aposta", [
            "Resultado Final (1X2)",
            "Mais de 2.5 Gols",
            "Menos de 2.5 Gols",
            "Mais de 8.5 Escanteios",
            "Cartões (Time com mais cartões)"
        ])
        st.session_state.analise["odd_casa"] = st.number_input("Odd oferecida pela casa", min_value=1.01, step=0.01)

    st.info("✅ Agora vá para a segunda aba 'Análise de Confiança e Kelly' para continuar.")

# Etapa 2: Checklist, Odds Justas, Kelly
if aba == "2. Análise de Confiança e Kelly":
    info = st.session_state.analise
    st.subheader("🧠 Checklist de Confiança — " + info["time_casa"] + " vs " + info["time_fora"])
    checklist = {
        "Está em boa fase nos últimos jogos?": 5,
        "Joga em casa (ou com vantagem tática)?": 4,
        "Adversário tem desfalques relevantes?": 4,
        "Elenco completo e motivado?": 3,
        "Odd oferecida parece generosa para o mercado?": 5,
        "Desempenho histórico no mercado analisado é bom?": 4,
        "Necessita vencer por fator externo (classificação etc)?": 3,
        "Pressão positiva da torcida/mídia?": 2
    }

    pontos = 0
    total = sum(checklist.values())
    colunas = st.columns(2)
    for i, (pergunta, peso) in enumerate(checklist.items()):
        if colunas[i % 2].checkbox(pergunta):
            pontos += peso

    confianca = (pontos / total) * 100
    prob_real = round(min(90, max(5, confianca)), 2)
    odd_justa = calcular_odds(prob_real)
    odd_oferecida = info["odd_casa"]
    ev = (prob_real / 100) * odd_oferecida - 1
    kelly = kelly_formula(prob_real / 100, odd_oferecida - 1)

    st.markdown(f"### 📊 Probabilidades e Cálculos para o mercado: **{info['mercado']}**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Probabilidade Real", f"{prob_real:.1f}%")
    col2.metric("Odd Justa", f"{odd_justa:.2f}")
    col3.metric("Odd da Casa", f"{odd_oferecida:.2f}")

    st.markdown("### 💰 Valor Esperado e Gestão de Banca")
    col4, col5 = st.columns(2)
    col4.metric("Valor Esperado (EV)", f"{ev:.2f}")
    col5.metric("Stake Kelly (%)", f"{kelly * 100:.1f}%")

    if ev > 0:
        st.success("✅ Aposta com valor positivo. Boa oportunidade.")
    elif ev == 0:
        st.info("⚠️ Aposta neutra.")
    else:
        st.warning("❌ Aposta com valor negativo.")

    st.subheader("📈 Gráfico de Confiança")
    fig = px.pie(values=[prob_real, 100 - prob_real], names=["Sucesso", "Fracasso"],
                 title="Distribuição de Probabilidade Estimada", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    st.text_area("📝 Anotações ou observações sobre este jogo")

