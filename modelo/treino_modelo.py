import pandas as pd
import joblib
import base64
from firebase_config import db
from utils.telegram_alert import enviar_telegram
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime

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
    print(f"✅ Acurácia: {acc:.2%}")

    if usar_csv:
        modelo_serializado = joblib.dumps(modelo)
        modelo_base64 = base64.b64encode(modelo_serializado).decode('utf-8')
        db.collection("modelos_treinados").add(
            {
                "timestamp": datetime.utcnow(),
                "modelo": modelo_base64,
                "acc": acc,
            },
            retry=None,
        )
        print("📤 Modelo enviado para Firestore.")
    else:
        joblib.dump(modelo, "modelo_treinado.pkl")
        enviar_telegram(f"🧠 Modelo re-treinado!\n🎯 Acurácia: *{acc*100:.2f}%* com {len(df)} registos.")
        print("✅ Modelo guardado localmente.")

    return acc

def executar_treino(usar_csv=False):
    df = carregar_dados(usar_csv)
    if df.empty:
        print("⚠️ Sem dados para treino.")
        return None
    return treinar(df, usar_csv)

if __name__ == "__main__":
    # Para correr em modo CSV (offline): executar_treino(usar_csv=True)
    executar_treino(usar_csv=False)
