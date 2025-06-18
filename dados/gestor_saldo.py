from datetime import datetime
from firebase_config import db

COL_SALDO = "saldo"
ID_DOCUMENTO = "principal"

def carregar_saldo():
    doc = db.collection("saldo_virtual").document("principal").get()
    data = doc.to_dict()
    if not data:
        # Inicializa com saldo padrão
        valor_inicial = 1000.0
        db.collection("saldo_virtual").document("principal").set({"valor": valor_inicial})
        return valor_inicial
    return data.get("valor", 1000.0)


def guardar_saldo(novo_valor):
    # Atualiza saldo atual
    db.collection("saldo_virtual").document("principal").set({
        "valor": novo_valor
    })

    # Guarda histórico
    db.collection("historico_saldo").add({
        "saldo": novo_valor,
        "data": datetime.utcnow()
    })
