import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import joblib
import base64
from firebase_admin import storage
from firebase_config import db
from utils.telegram_alert import enviar_telegram
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime, timezone

def carregar_dados(usar_csv=False):
    if usar_csv:
        df = pd.read_csv("dados_treinamento.csv")
        df = df.rename(columns={
            'RSI': 'rsi',
            'MACD': 'macd',
            'MACD_signal': 'macd_signal',
            'MACD_histograma': 'macd_diff'
        })
        df["target"] = df["target"].astype(int)
        return df
    else:
        docs = (
            db.collection("posicoes")
            .where("em_aberto", "==", False)
            .stream(retry=None)
        )
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

def treinar(df, usar_csv=False):
    if usar_csv:
        features = [
            'rsi', 'macd_diff', 'bb_lower', 'bb_upper', 'bb_middle',
            'volume', 'volume_ma', 'close'
        ]
        target_col = 'target'
    else:
        features = ['rsi', 'macd_diff']
        target_col = 'lucro'

    X = df[features]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    acc = accuracy_score(y_test, modelo.predict(X_test))
    n_amostras = len(df)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")

    if usar_csv:
        modelo_serializado = joblib.dumps(modelo)
        modelo_base64 = base64.b64encode(modelo_serializado).decode('utf-8')
        db.collection("modelos_treinados").add(
            {
                "timestamp": datetime.utcnow(),
                "modelo": modelo_base64,
                "acc": acc,
            },
            retry=None
        )
    else:
        joblib.dump(modelo, "modelo_treinado.pkl")

    # Upload para Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f"modelos/modelo_treinado_{datetime.now(timezone.utc).isoformat()}.pkl")
    blob.upload_from_filename("modelo_treinado.pkl")
    url_download = blob.generate_signed_url(expiration=3600 * 24 * 7)  # válido por 7 dias

    db.collection("modelos_treinados").add({
        "timestamp": datetime.now(timezone.utc),
        "url_download": url_download,
        "acc": acc
    }, retry=None)

    enviar_telegram(
        f"""🧠 *Modelo re-treinado com sucesso!*\n
🎯 *Acurácia:* {acc*100:.2f}%\n
📊 *Registos:* {n_amostras}\n
🕒 *Hora:* {agora}"""
    )

    # Guardar histórico no Firestore
    db.collection("registo_treinos").add(
        {
            "timestamp": datetime.now(timezone.utc),
            "modelo": "RandomForest",
            "acc": acc,
            "n_amostras": n_amostras
        },
        retry=None
    )

    return acc

def executar_treino(usar_csv=False):
    df = carregar_dados(usar_csv)
    if df.empty:
        enviar_telegram("⚠️ Sem dados disponíveis para treinar o modelo.")
        return None
    return treinar(df, usar_csv)

if __name__ == "__main__":
    executar_treino(usar_csv=False)
