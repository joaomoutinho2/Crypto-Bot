import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

def iniciar_firebase():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    cred_json = os.getenv("FIREBASE_JSON")
    if not cred_json:
        raise Exception("FIREBASE_JSON não encontrado nas variáveis de ambiente.")

    cred_dict = json.loads(cred_json)
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Inicializa e cria db global
iniciar_firebase()
db = firestore.client()

# Apenas teste local
if __name__ == "__main__":
    print("🧪 [firebase_config] iniciar_firebase() chamado.")
    try:
        print("✅ Firebase inicializado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao iniciar Firebase: {e}")
