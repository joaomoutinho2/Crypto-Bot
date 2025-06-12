import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from firebase_config import iniciar_firebase
from firebase_admin import firestore
from utils.telegram_alert import enviar_telegram

def carregar_dados():
    db = firestore.client()
    docs = db.collection("posicoes").where("em_aberto", "==", False).stream()
    dados = []
    for doc in docs:
        d = doc.to_dict()
        if "lucro" in d and all(k in d for k in ["rsi", "macd_diff"]):
            dados.append({
                "rsi": d["rsi"],
                "macd_diff": d["macd_diff"],
                "lucro": 1 if d["lucro"] > 0 else 0
            })
    return pd.DataFrame(dados)

def treinar(df):
    X = df.drop("lucro", axis=1)
    y = df["lucro"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    joblib.dump(modelo, "modelo_treinado.pkl")

    enviar_telegram(f"🧠 Modelo re-treinado!\n🎯 Acurácia: *{acc*100:.2f}%* com {len(df)} registos.")
    print("✅ Modelo treinado e guardado.")
    return acc

if __name__ == "__main__":
    iniciar_firebase()
    df = carregar_dados()
    if df.empty:
        print("⚠️ Sem dados para treino.")
    else:
        treinar(df)
