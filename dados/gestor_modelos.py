from firebase_config import db
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import joblib
import base64
import io
from google.cloud import firestore

def treinar_modelo():
    docs = db.collection("previsoes").where("avaliado", "==", True).stream(retry=None)
    dados = []
    for doc in docs:
        d = doc.to_dict()
        if all(k in d for k in ["rsi", "macd_diff", "lucro"]):
            dados.append({
                "rsi": d["rsi"],
                "macd_diff": d["macd_diff"],
                "target": 1 if d["lucro"] > 0 else 0
            })

    df = pd.DataFrame(dados)
    if df.empty:
        print("⚠️ Nenhum dado suficiente para treinar o modelo.")
        return

    X = df[["rsi", "macd_diff"]]
    y = df["target"]

    modelo = RandomForestClassifier(n_estimators=100)
    modelo.fit(X, y)

    buffer = io.BytesIO()
    joblib.dump(modelo, buffer)
    modelo_bytes = base64.b64encode(buffer.getvalue()).decode()

    db.collection("modelos_treinados").add(
        {
            "timestamp": firestore.SERVER_TIMESTAMP,
            "modelo_serializado": modelo_bytes,
            "acuracia_aparente": modelo.score(X, y),
        },
        retry=None,
    )

    print("✅ Modelo treinado e guardado com sucesso.")
