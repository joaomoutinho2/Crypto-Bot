from firebase_admin import firestore
from datetime import datetime

db = firestore.client()

def registar_entrada(simbolo, preco, contexto, decisao):
    doc = {
        "simbolo": simbolo,
        "preco_entrada": preco,
        "contexto": contexto,
        "decisao": decisao,
        "timestamp_entrada": datetime.utcnow(),
        "em_aberto": True
    }
    db.collection("posicoes").add(doc)

def carregar_posicoes_abertas():
    docs = db.collection("posicoes").where("em_aberto", "==", True).stream()
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def fechar_posicao(doc_id, preco_saida):
    doc_ref = db.collection("posicoes").document(doc_id)
    doc = doc_ref.get().to_dict()
    lucro = (preco_saida - doc["preco_entrada"]) / doc["preco_entrada"]

    doc_ref.update({
        "preco_saida": preco_saida,
        "timestamp_saida": datetime.utcnow(),
        "lucro": lucro,
        "em_aberto": False
    })
    return lucro
