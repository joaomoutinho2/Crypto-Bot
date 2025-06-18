
import streamlit as st
import pandas as pd
import altair as alt
from firebase_config import db
from dados.gestor_saldo import carregar_saldo
from google.cloud import firestore

st.title("💹 Painel de Controlo do Crypto-Bot")

# Saldo
saldo = carregar_saldo()
st.metric("Saldo Virtual", f"{saldo:.2f} USDT")

# Carregar posições
docs = db.collection("posicoes").order_by("timestamp_entrada", direction=firestore.Query.DESCENDING).stream()

dados = []
for doc in docs:
    d = doc.to_dict()
    dados.append({
        "Moeda": d.get("simbolo"),
        "Entrada": d.get("preco_entrada"),
        "Saída": d.get("preco_saida", None),
        "Montante": d.get("montante", None),
        "Lucro (USDT)": d.get("lucro_valor", None),
        "Lucro (%)": d.get("lucro_percentual", None),
        "Aberta?": d.get("em_aberto", True),
        "GPT": d.get("decisao"),
        "Data": d.get("timestamp_entrada"),
    })

df = pd.DataFrame(dados)

# Separar por estado
df_abertas = df[df["Aberta?"] == True]
df_fechadas = df[df["Aberta?"] == False]

st.subheader("📊 Posições em Aberto")
st.dataframe(df_abertas.style.format({
    "Entrada": "{:.4f}",
    "Montante": "{:.2f}"
}))

st.subheader("✅ Posições Fechadas")
st.dataframe(df_fechadas.style.format({
    "Entrada": "{:.4f}",
    "Saída": "{:.4f}",
    "Montante": "{:.2f}",
    "Lucro (USDT)": "{:.2f}",
    "Lucro (%)": "{:.2f}"
}))

# Gráfico de saldo ao longo do tempo
docs_saldo = db.collection("historico_saldo").order_by("data").stream()
dados_grafico = []

for doc in docs_saldo:
    d = doc.to_dict()
    dados_grafico.append({
        "Data": d.get("data"),
        "Saldo (USDT)": d.get("saldo")
    })

if dados_grafico:
    df_saldo = pd.DataFrame(dados_grafico)
    st.subheader("📈 Evolução do Saldo Virtual")
    chart = alt.Chart(df_saldo).mark_line().encode(
        x="Data:T",
        y="Saldo (USDT):Q"
    ).properties(width=700, height=300)
    st.altair_chart(chart, use_container_width=True)
