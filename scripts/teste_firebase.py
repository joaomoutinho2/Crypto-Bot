import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

def iniciar_firebase():
    if firebase_admin._apps:
        return firebase_admin.get_app()
    cred_dict = json.loads(os.getenv("FIREBASE_JSON"))
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(cred_dict)
    return firebase_admin.initialize_app(cred)

iniciar_firebase()
print("✅ Firebase inicializado com sucesso.")
