import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import altair as alt
from firebase_config import db
from dados.gestor_saldo import carregar_saldo
from google.cloud import firestore

st.set_page_config(page_title="Crypto-Bot", layout="wide")
st.title("💹 Painel de Controlo do Crypto-Bot")

# ----------------------------
# SALDO VIRTUAL
# ----------------------------
saldo = carregar_saldo()
st.metric("💰 Saldo Virtual", f"{saldo:.2f} USDT")

# ----------------------------
# POSIÇÕES
# ----------------------------
docs = db.collection("posicoes").order_by("timestamp_entrada", direction=firestore.Query.DESCENDING).stream()
dados = []
for doc in docs:
    d = doc.to_dict()
    dados.append({
        "Moeda": d.get("simbolo", ""),
        "Entrada": d.get("preco_entrada", 0),
        "Saída": d.get("preco_saida", None),
        "Montante": d.get("montante", 0),
        "Lucro (USDT)": d.get("lucro_valor", None),
        "Lucro (%)": d.get("lucro_percentual", None),
        "Aberta?": d.get("em_aberto", True),
        "GPT": d.get("decisao", "-"),
        "Data": pd.to_datetime(d.get("timestamp_entrada")).strftime("%Y-%m-%d %H:%M")
    })
df = pd.DataFrame(dados)

st.subheader("📊 Posições em Aberto")
df_abertas = df[df["Aberta?"] == True]
st.dataframe(df_abertas.style.format({"Entrada": "{:.4f}", "Montante": "{:.2f}"}), use_container_width=True)

st.subheader("✅ Posições Fechadas")
df_fechadas = df[df["Aberta?"] == False]
st.dataframe(df_fechadas.style.format({
    "Entrada": "{:.4f}", "Saída": "{:.4f}", "Montante": "{:.2f}",
    "Lucro (USDT)": "{:.2f}", "Lucro (%)": "{:.2f}"
}), use_container_width=True)

# ----------------------------
# GRÁFICO DE SALDO
# ----------------------------
docs_saldo = db.collection("historico_saldo").order_by("data").stream()
dados_grafico = []
for doc in docs_saldo:
    d = doc.to_dict()
    dados_grafico.append({"Data": pd.to_datetime(d.get("data")), "Saldo (USDT)": d.get("saldo", 0)})
if dados_grafico:
    df_saldo = pd.DataFrame(dados_grafico)
    st.subheader("📈 Evolução do Saldo Virtual")
    chart = alt.Chart(df_saldo).mark_line(point=True).encode(
        x=alt.X("Data:T", title="Data"),
        y=alt.Y("Saldo (USDT):Q", title="Saldo em USDT")
    ).properties(width=800, height=350)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Nenhum dado de saldo encontrado ainda.")

# ----------------------------
# DECISÕES RECENTES DO MODELO
# ----------------------------
st.subheader("🧠 Decisões Recentes do Modelo")
docs_decisoes = db.collection("historico_previsoes").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
dados_decisoes = []
for doc in docs_decisoes:
    d = doc.to_dict()
    dados_decisoes.append({
        "Data": pd.to_datetime(d.get("timestamp")).strftime("%Y-%m-%d %H:%M"),
        "Moeda": d.get("simbolo"),
        "Resultado": d.get("resultado"),
        "Score": d.get("score")
    })
if dados_decisoes:
    df_dec = pd.DataFrame(dados_decisoes)
    st.table(df_dec)
else:
    st.info("Nenhuma decisão recente encontrada.")

# ----------------------------
# GRÁFICO: Lucro por Moeda
# ----------------------------
st.subheader("💸 Lucro Médio por Moeda")
df_lucro_moeda = df_fechadas.groupby("Moeda")["Lucro (USDT)"].mean().reset_index()
chart_lucro = alt.Chart(df_lucro_moeda).mark_bar().encode(
    x=alt.X("Moeda:N"),
    y=alt.Y("Lucro (USDT):Q"),
    color="Moeda:N"
).properties(width=800, height=300)
st.altair_chart(chart_lucro, use_container_width=True)

# ----------------------------
# HISTÓRICO DE TRANSAÇÕES (exportável)
# ----------------------------
st.subheader("📜 Exportar Histórico de Transações")
with st.expander("Ver tabela completa"):
    st.dataframe(df.style.format({"Entrada": "{:.4f}", "Montante": "{:.2f}"}), use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "historico_transacoes.csv", "text/csv")

# ----------------------------
# ESTRATÉGIAS
# ----------------------------
st.subheader("🎯 Estratégia Ativa")
estrategias = db.collection("estrategia").stream()
lista = []
for e in estrategias:
    d = e.to_dict()
    lista.append(d.get("nome"))
if lista:
    estrategia_ativa = st.selectbox("Selecionar Estratégia Ativa", lista)
    if st.button("💾 Guardar Estratégia"):
        db.collection("controlo").document("estrategia").set({"ativa": estrategia_ativa})
        st.success(f"Estratégia '{estrategia_ativa}' guardada com sucesso!")
else:
    st.info("Nenhuma estratégia definida.")

# ----------------------------
# ADMINISTRAÇÃO
# ----------------------------
st.subheader("⚙️ Administração")
with st.expander("Saldo Virtual"):
    novo_saldo = st.number_input("Alterar saldo virtual", value=saldo)
    if st.button("Atualizar Saldo"):
        db.collection("controlo").document("saldo_virtual").set({"saldo": novo_saldo})
        st.success("Saldo atualizado com sucesso!")

with st.expander("Treino do Modelo"):
    if st.button("🧠 Forçar novo treino"):
        db.collection("controlo").document("forcar_treino").set({"status": True})
        st.success("Treino solicitado com sucesso!")
