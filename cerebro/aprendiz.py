import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from firebase_config import db

def carregar_dados_posicoes():
    docs = db.collection("posicoes").where("em_aberto", "==", False).stream()
    registos = []
    for doc in docs:
        d = doc.to_dict()
        if "lucro" in d and all(k in d for k in ["rsi", "macd_diff", "preco_entrada"]):
            registos.append({
                "rsi": d["rsi"],
                "macd_diff": d["macd_diff"],
                "lucro": 1 if d["lucro"] > 0 else 0
            })
    return pd.DataFrame(registos)

def treinar_modelo(df):
    X = df.drop("lucro", axis=1)
    y = df["lucro"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)

    print("✅ Modelo treinado com sucesso.")
    print("🔎 Accuracy:", accuracy_score(y_test, y_pred))
    print("📋 Relatório:")
    print(classification_report(y_test, y_pred))

    joblib.dump(modelo, "modelo_treinado.pkl")
    print("💾 Modelo guardado como modelo_treinado.pkl")

if __name__ == "__main__":
    df = carregar_dados_posicoes()
    if df.empty:
        print("⚠️ Sem dados suficientes para treinar o modelo.")
    else:
        treinar_modelo(df)
