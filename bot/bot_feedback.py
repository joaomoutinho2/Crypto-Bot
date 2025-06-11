import ccxt
from firebase_admin import firestore
from dados.saldo_virtual import carregar_saldo, guardar_saldo
from datetime import datetime

exchange = ccxt.kucoin()

def avaliar_resultados():
    db = firestore.client()
    saldo = carregar_saldo()

    docs = db.collection("previsoes").order_by("timestamp").stream()
    for doc in docs:
        dados = doc.to_dict()
        if dados.get("avaliado"):
            continue
        simbolo = dados['simbolo']
        decisao = dados['decisao']
        timestamp = dados['timestamp']
        if decisao != 'sim':
            continue

        try:
            df = exchange.fetch_ohlcv(simbolo, timeframe='1m', limit=2)
            preco_atual = df[-1][4]
            preco_entrada = df[-2][4]
            lucro = preco_atual / preco_entrada - 1
            saldo *= (1 + lucro)

            db.collection("previsoes").document(doc.id).update({
                "avaliado": True,
                "lucro": lucro,
                "preco_entrada": preco_entrada,
                "preco_saida": preco_atual,
                "rsi": dados.get("rsi"),
                "macd_diff": dados.get("macd_diff")
            })
        except:
            continue

    guardar_saldo(saldo)