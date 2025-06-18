import pandas as pd
import joblib
import base64
from firebase_admin import firestore
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime

# === Carrega dados
df = pd.read_csv("dados_treinamento.csv")
df = df.rename(columns={
    'RSI': 'rsi',
    'MACD': 'macd',
    'MACD_signal': 'macd_signal',
    'MACD_histograma': 'macd_diff'
})
features = [
    'rsi', 'macd_diff',
    'bb_lower', 'bb_upper', 'bb_middle',
    'volume', 'volume_ma', 'close'
]
X = df[features]
y = df['target']

# === Divide treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# === Treina modelo
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# === Avalia
acc = accuracy_score(y_test, modelo.predict(X_test))
print(f"✅ Acurácia: {acc:.2%}")

# === Serializa e codifica
modelo_serializado = joblib.dumps(modelo)
modelo_base64 = base64.b64encode(modelo_serializado).decode('utf-8')

# === Envia para Firestore
db = firestore.client()
db.collection("modelos_treinados").add({
    "timestamp": firestore.SERVER_TIMESTAMP,
    "modelo": modelo_base64,
    "acc": acc
})

print("✅ Modelo treinado e guardado no Firestore!")
