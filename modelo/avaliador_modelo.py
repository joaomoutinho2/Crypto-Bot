import pandas as pd
import joblib
import base64
from firebase_admin import firestore

# === Função principal: prever se a próxima subida é provável ===
def prever_subida(df_indicadores):
    """Carrega o modelo mais recente do Firestore e faz a inferência.

    Esta é a função oficial de inferência utilizada pelo bot em tempo real.
    Recebe um DataFrame com os indicadores técnicos mais recentes e retorna
    ``True`` caso o modelo preveja que o próximo candle será de subida.
    """
    db = firestore.client()
    colecao = db.collection("modelos_treinados")
    docs = (
        colecao.order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )

    modelo = None
    for doc in docs:
        dados = doc.to_dict()
        modelo_b64 = dados.get("modelo")
        if modelo_b64:
            modelo_bytes = base64.b64decode(modelo_b64)
            modelo = joblib.loads(modelo_bytes)
            break

    if modelo is None:
        print("❌ Nenhum modelo disponível no Firestore.")
        return False

    # Garantir que os dados estão no mesmo formato do treino
    features = [
        'rsi', 'macd_diff',
        'bb_lower', 'bb_upper', 'bb_middle',
        'volume', 'volume_ma', 'close'
    ]

    try:
        entrada = df_indicadores[features].iloc[-1:]
    except Exception as e:
        print(f"❌ Erro ao preparar dados para previsão: {e}")
        return False

    # Faz a previsão
    pred = modelo.predict(entrada)[0]
    return pred == 1
