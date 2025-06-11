import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

def iniciar_firebase():
    if firebase_admin._apps:
        return firestore.client()

    cred_json = os.getenv("FIREBASE_JSON")
    if not cred_json:
        raise Exception("FIREBASE_JSON não encontrado nas variáveis de ambiente.")

    cred = credentials.Certificate(json.loads(cred_json))
    firebase_admin.initialize_app(cred)
    return firestore.client()