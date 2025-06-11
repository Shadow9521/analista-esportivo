import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime
from io import BytesIO

# Configuração inicial
st.set_page_config(page_title="Analista Esportivo Inteligente", layout="wide")
st.title("⚽ Analista Esportivo Inteligente")

# Função para calcular odds justas a partir das probabilidades
def calcular_odds(prob):
    return round(1 / (prob / 100), 2) if prob > 0 else float('inf')

# Função de Kelly
def kelly_formula(p, b):
    return max(((p * (b + 1) - 1) / b), 0)

# Função para exportar dados para Excel
def export_df_to_excel(df):
    output = BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Analise')
    except ImportError:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Analise')
    return output.getvalue()

# Pesos do checklist (valores entre 1 e 5)
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

# Interface lateral
st.sidebar.header("Configurações do Jogo")
jogos = ["Brasil x Argentina", "Alemanha x França", "Espanha x Itália"]
jogo_selecionado = st.sidebar.selectbox("Selecione o Jogo", jogos)
banca = st.sidebar.number_input("Saldo da Banca (R$)", value=100.0, step=10.0)
stake_recomendada = banca * 0.05
st.sidebar.markdown(f"**Stake recomendada:** R$ {stake_recomendada:.2f}")

st.subheader(f"Análise do Jogo: {jogo_selecionado}")

# Dicionário para armazenar análises separadas
if "analises" not in st.session_state:
    st.session_state.analises = {}

if jogo_selecionado not in st.session_state.analises:
    st.session_state.analises[jogo_selecionado] = {
        "respostas": [False] * len(checklist),
        "historico": [],
        "odd_oferecida": 1.80,
        "comentarios": ""
    }

# Atualiza dados atuais da sessão
analise = st.session_state.analises[jogo_selecionado]

# Tabela de estatísticas simuladas
dados = {
    "Time": jogo_selecionado.split(" x "),
    "Últimos 5 Jogos (Vitórias)": [4, 3],
    "Odds": [1.80, 2.20]
}
df = pd.DataFrame(dados)
st.dataframe(df, use_container_width=True)

# Checklist com pesos
st.subheader("🧠 Checklist de Confiança (20 Itens de Alta Relevância)")
cols = st.columns(4)
respostas = []
for i, (pergunta, peso) in enumerate(checklist.items()):
    col = cols[i % 4]
    marcado = col.checkbox(pergunta, value=analise["respostas"][i])
    respostas.append(peso if marcado else 0)
    analise["respostas"][i] = marcado

pontuacao_total = sum(checklist.values())
pontuacao_usuario = sum(respostas)
confianca_percentual = (pontuacao_usuario / pontuacao_total) * 100

st.markdown(f"**Pontuação de Confiança Total:** {pontuacao_usuario} / {pontuacao_total}  ")
st.progress(confianca_percentual / 100)

# Histórico de confiança
analise["historico"].append({"Data": datetime.datetime.now(), "Confiança (%)": confianca_percentual})
df_hist = pd.DataFrame(analise["historico"])
with st.expander("📈 Evolução Histórica da Confiança"):
    st.line_chart(df_hist.set_index("Data"))

# Estimativa de probabilidades baseada na confiança
vitoria = min(70, max(10, confianca_percentual))
empate = 100 - vitoria - 20
derrota = 100 - vitoria - empate

# Odds justas com base na probabilidade
odds_vitoria = calcular_odds(vitoria)
odds_empate = calcular_odds(empate)
odds_derrota = calcular_odds(derrota)

# Exibição das probabilidades e odds estimadas
st.subheader("📊 Probabilidades e Odds Justas")
df_prob = pd.DataFrame({
    "Resultado": ["Vitória", "Empate", "Derrota"],
    "Probabilidade (%)": [vitoria, empate, derrota],
    "Odd Justa": [odds_vitoria, odds_empate, odds_derrota]
})
st.dataframe(df_prob, use_container_width=True)

# Gráfico de pizza com plotly
fig = px.pie(df_prob, names='Resultado', values='Probabilidade (%)', title='Distribuição de Probabilidades')
st.plotly_chart(fig, use_container_width=True)

# Cálculo de valor esperado e Kelly
st.subheader("⚙️ Cálculo de Valor Esperado e Kelly")
analise["odd_oferecida"] = st.number_input("Odd Oferecida pela Casa para Vitória", value=analise["odd_oferecida"], step=0.01)
valor_esperado = (vitoria / 100) * analise["odd_oferecida"] - 1
kelly = kelly_formula(vitoria / 100, analise["odd_oferecida"] - 1)

col1, col2 = st.columns(2)
col1.metric(label="Valor Esperado (EV)", value=f"{valor_esperado:.2f}")
col2.metric(label="Stake Kelly (%)", value=f"{kelly * 100:.1f}%")

# Recomendação
if valor_esperado > 0:
    st.success("✅ Aposta com valor positivo. Pode valer a pena apostar.")
elif valor_esperado == 0:
    st.info("⚠️ Aposta neutra. Sem valor esperado.")
else:
    st.warning("❌ Aposta com valor negativo. Evite apostar.")

# Comparação visual de odds
st.subheader("📊 Comparação Visual: Odd Justa x Odd da Casa")
comparativo = pd.DataFrame({
    "Tipo": ["Odd Justa", "Odd da Casa"],
    "Valor": [odds_vitoria, analise["odd_oferecida"]]
})
fig_bar = px.bar(comparativo, x="Tipo", y="Valor", color="Tipo", title="Comparação de Odds")
st.plotly_chart(fig_bar, use_container_width=True)

# Exportação dos dados
st.subheader("📥 Exportar Análise")
excel_data = export_df_to_excel(df_prob)
st.download_button(label="📄 Baixar Dados em Excel", data=excel_data, file_name="analise_apostas.xlsx")

# Agenda de Jogos
st.subheader("🗓️ Agenda de Jogos (Exemplo)")
jogos_proximos = pd.DataFrame({
    "Data": ["12/06/2025", "13/06/2025", "14/06/2025"],
    "Jogo": ["Brasil x Uruguai", "França x Itália", "Alemanha x Espanha"],
    "Campeonato": ["Eliminatórias", "Eurocopa", "Eurocopa"]
})
st.dataframe(jogos_proximos, use_container_width=True)

# Notas do Analista
st.subheader("📝 Anotações do Analista")
analise["comentarios"] = st.text_area("Comentários, observações ou insights sobre este jogo:",
                                       value=analise["comentarios"], height=150)
