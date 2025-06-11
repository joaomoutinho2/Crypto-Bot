from firebase_admin import firestore
from datetime import datetime

def guardar_previsao(simbolo, decisao, contexto):
    db = firestore.client()
    doc = {
        "simbolo": simbolo,
        "decisao": decisao,
        "contexto": contexto,
        "timestamp": datetime.utcnow()
    }
    db.collection("previsoes").add(doc)