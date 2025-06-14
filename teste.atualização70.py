# === PARTE 1: Setup, Estilo, Entrada de Dados ===
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

st.set_page_config(page_title="Analista Esportivo Inteligente", layout="wide")
background_image_base64 = get_base64_image("ChatGPTima.png")

# Estilo visual
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{background_image_base64}");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }}
    .block-container {{
        background-color: rgba(0, 0, 0, 0.75);
        padding: 2rem;
        border-radius: 15px;
    }}
    input, textarea {{ background-color: #111; color: white; }}
    .stMarkdown, .stTextInput, .stNumberInput, .stRadio, .stButton, .stDownloadButton {{
        color: white !important;
    }}
    .stRadio > div {{
        background-color: #222;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
    }}
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("""
    <div style="padding: 30px; border-radius: 10px; color: white; margin-bottom: 30px;">
        <h1>⚽ Analista Esportivo Inteligente</h1>
        <p>Preencha os dados abaixo para começar a análise:</p>
    </div>
""", unsafe_allow_html=True)

# Inicialização de estados
if 'respostas' not in st.session_state:
    st.session_state.respostas = []
if 'fase' not in st.session_state:
    st.session_state.fase = 1
if 'etapa' not in st.session_state:
    st.session_state.etapa = 0
if 'avancar' not in st.session_state:
    st.session_state.avancar = False
if 'fatores' not in st.session_state:
    st.session_state.fatores = [
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

fatores = st.session_state.fatores
respostas = st.session_state.respostas
etapa = st.session_state.etapa

# Entrada de dados
col_titulo, col_banca = st.columns([5, 1])
with col_titulo:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        time_casa = st.text_input("Time da Casa", "Brasil")
    with col_b:
        st.text_input("Empate", "Empate", disabled=True)
    with col_c:
        time_fora = st.text_input("Time Visitante", "Argentina")

    col_d, col_e, col_f = st.columns(3)
    with col_d:
        odd_vitoria = max(st.number_input("Odd Vitória (Casa)", value=1.80, step=0.01), 1.01)
    with col_e:
        odd_empate = max(st.number_input("Odd Empate", value=3.20, step=0.01), 1.01)
    with col_f:
        odd_derrota = max(st.number_input("Odd Vitória (Visitante)", value=4.00, step=0.01), 1.01)

with col_banca:
    st.markdown("#### 💼 Banca")
    banca = st.number_input("", value=100.0, step=10.0, label_visibility="collapsed")
    st.markdown("<small>Saldo da Banca (R$)</small>", unsafe_allow_html=True)

# === PARTE 2: Checklist com pesos e cálculo de odds justas ===

if st.session_state.fase == 1:
    st.subheader(f"✅ CHECKLIST DE ANÁLISE DO JOGO: {time_casa} x {time_fora}")
    
    fator, peso = fatores[etapa]
    st.markdown(f"**{etapa + 1}/{len(fatores)} - {fator} (Peso {peso})**")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        resposta = st.radio(
            "Escolha a opção:",
            [f"{time_casa}", "Empate", f"{time_fora}"],
            index=1,
            horizontal=True
        )

    if st.button("Responder"):
        st.session_state.respostas.append((resposta, peso))
        if etapa + 1 >= len(fatores):
            st.session_state.fase = 2
        else:
            st.session_state.etapa += 1
        st.experimental_rerun()

    if etapa > 0:
        if st.button("🔙 Voltar pergunta"):
            st.session_state.etapa -= 1
            st.session_state.respostas.pop()
            st.experimental_rerun()

    st.progress((etapa + 1) / len(fatores))

# === PARTE 2B: Cálculo de probabilidades e odds ===
if st.session_state.fase == 2:
    total_peso = sum([peso for _, peso in respostas])
    soma_casa = sum([peso for resp, peso in respostas if resp == time_casa])
    soma_fora = sum([peso for resp, peso in respostas if resp == time_fora])

    prob_casa = round((soma_casa / total_peso) * 100, 2)
    prob_fora = round((soma_fora / total_peso) * 100, 2)
    prob_empate = max(0, round(100 - prob_casa - prob_fora, 2))

    odd_justa_casa = calcular_odds(prob_casa)
    odd_justa_empate = calcular_odds(prob_empate)
    odd_justa_fora = calcular_odds(prob_fora)

    st.subheader("📊 Resultado da Análise")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Prob. {time_casa}", f"{prob_casa}%")
        st.metric("Odd Justa", f"{odd_justa_casa}")
        lucro_casa = round((odd_vitoria - 1) * 100, 2)
        st.metric("Odd da Casa", f"{odd_vitoria}", delta=f"+{lucro_casa}%")
    with col2:
        st.metric("Prob. Empate", f"{prob_empate}%")
        st.metric("Odd Justa", f"{odd_justa_empate}")
        lucro_empate = round((odd_empate - 1) * 100, 2)
        st.metric("Odd da Casa", f"{odd_empate}", delta=f"+{lucro_empate}%")
    with col3:
        st.metric(f"Prob. {time_fora}", f"{prob_fora}%")
        st.metric("Odd Justa", f"{odd_justa_fora}")
        lucro_fora = round((odd_derrota - 1) * 100, 2)
        st.metric("Odd da Casa", f"{odd_derrota}", delta=f"+{lucro_fora}%")
    # === PARTE 3: Stake com Fórmula de Kelly ===

    st.subheader("📈 Sugestão de Aposta com Gestão de Banca (Fórmula de Kelly)")

    selecao = st.selectbox("Qual resultado deseja simular?", [time_casa, "Empate", time_fora])

    prob_selecionada = {
        time_casa: prob_casa,
        "Empate": prob_empate,
        time_fora: prob_fora
    }[selecao]

    odd_selecionada = {
        time_casa: max(odd_vitoria, 1.01),
        "Empate": max(odd_empate, 1.01),
        time_fora: max(odd_derrota, 1.01)
    }[selecao]

    valor_kelly = kelly(prob_selecionada / 100, odd_selecionada)

    if valor_kelly > 0:
        sugestao_valor = round(banca * valor_kelly, 2)
        st.success(f"Sugestão: Apostar R$ {sugestao_valor} ({round(valor_kelly*100,2)}% da banca)")
    else:
        st.warning("⚠️ Não há valor nesta aposta. Sugere-se **não apostar**.")

    # === GRÁFICO DE PIZZA (Distribuição de Probabilidades) ===

    st.subheader("📊 Distribuição de Probabilidades (Checklist)")

    fig_pizza = px.pie(
        names=[time_casa, "Empate", time_fora],
        values=[prob_casa, prob_empate, prob_fora],
        title="Probabilidades Reais Estimadas",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

    # === GRÁFICO DE BARRAS COMPARANDO ODDS ===

    st.subheader("📉 Comparação: Odds da Casa vs Odds Justas")

    df_comparacao = pd.DataFrame({
        "Resultado": [time_casa, "Empate", time_fora],
        "Odd Justa": [odd_justa_casa, odd_justa_empate, odd_justa_fora],
        "Odd da Casa": [odd_vitoria, odd_empate, odd_derrota]
    })

    fig_barras = px.bar(
        df_comparacao.melt(id_vars="Resultado", var_name="Tipo", value_name="Odds"),
        x="Resultado", y="Odds", color="Tipo", barmode="group",
        title="Comparação de Odds"
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # === EXPORTAÇÃO DOS DADOS ===

    st.subheader("💾 Exportar Análise")

    df_export = pd.DataFrame(respostas, columns=["Resposta", "Peso"])
    df_export.loc[len(df_export.index)] = ["Prob. " + time_casa, f"{prob_casa}%"]
    df_export.loc[len(df_export.index)] = ["Prob. Empate", f"{prob_empate}%"]
    df_export.loc[len(df_export.index)] = ["Prob. " + time_fora, f"{prob_fora}%"]
    df_export.loc[len(df_export.index)] = ["Odd Justa " + time_casa, odd_justa_casa]
    df_export.loc[len(df_export.index)] = ["Odd Justa Empate", odd_justa_empate]
    df_export.loc[len(df_export.index)] = ["Odd Justa " + time_fora, odd_justa_fora]

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Análise")
        writer.close()
        st.download_button(
            label="📥 Baixar Análise em Excel",
            data=buffer.getvalue(),
            file_name=f"analise_{time_casa}_vs_{time_fora}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
