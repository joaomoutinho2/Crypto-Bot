import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from firebase_config import iniciar_firebase
import pandas as pd

iniciar_firebase()

import firebase_admin
from firebase_admin import firestore
from dados.saldo_virtual import carregar_saldo

def mostrar_dashboard():
    st.title("📈 Painel de Inteligência de Investimento")
    st.metric("💰 Saldo Virtual", f"${carregar_saldo():.2f}")

    st.write("Entradas e decisões da IA:")
    db = firestore.client()
    docs = db.collection("previsoes").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
    lista = []
    for doc in docs:
        d = doc.to_dict()
        lista.append({
            "Moeda": d.get("simbolo"),
            "Decisão": d.get("decisao"),
            "Contexto": d.get("contexto"),
            "Entrada": d.get("preco_entrada"),
            "Saída": d.get("preco_saida"),
            "Lucro": f"{d.get('lucro', 0)*100:.2f}%" if "lucro" in d else None,
            "Data": d.get("timestamp")
        })
    st.dataframe(pd.DataFrame(lista))

if __name__ == "__main__":
    mostrar_dashboard()