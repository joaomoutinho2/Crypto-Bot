from firebase_admin import firestore

COL_SALDO = "saldo_virtual"
ID_DOCUMENTO = "principal"


def carregar_saldo():
    db = firestore.client()
    doc = db.collection(COL_SALDO).document(ID_DOCUMENTO).get()
    if doc.exists:
        return doc.to_dict().get("valor", 100.0)
    return 100.0


def guardar_saldo(valor):
    db = firestore.client()
    db.collection(COL_SALDO).document(ID_DOCUMENTO).set({"valor": valor})