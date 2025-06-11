import ccxt
import pandas as pd
from cerebro.decisor_final import avaliar_entrada
from firebase_config import iniciar_firebase

def correr_analise():
    iniciar_firebase()
    exchange = ccxt.kucoin()
    simbolos = [s for s in exchange.load_markets().keys() if "/USDT" in s]
    for simbolo in simbolos[:5]:
        try:
            df = exchange.fetch_ohlcv(simbolo, timeframe='1m', limit=100)
            df = pd.DataFrame(df, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            resultado = avaliar_entrada(df, simbolo)
            print(f"{simbolo}: {resultado}")
        except Exception as e:
            print(f"Erro ao analisar {simbolo}: {e}")