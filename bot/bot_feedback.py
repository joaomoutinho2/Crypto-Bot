import ccxt
import pandas as pd
from firebase_config import iniciar_firebase
from dados.gestor_posicoes import carregar_posicoes_abertas, fechar_posicao
from estrategia.avaliar_saida import avaliar_saida
from utils.telegram_alert import enviar_telegram

db = iniciar_firebase()
exchange = ccxt.kucoin()

def correr_feedback():
    posicoes = carregar_posicoes_abertas()

    for pos in posicoes:
        simbolo = pos["simbolo"]
        try:
            df = exchange.fetch_ohlcv(simbolo, timeframe="1m", limit=100)
            df = pd.DataFrame(df, columns=["timestamp", "open", "high", "low", "close", "volume"])

            resultado = avaliar_saida(df)
            if resultado["acao"] == "sair":
                preco_saida = df["close"].iloc[-1]
                lucro = fechar_posicao(pos["id"], preco_saida)

                mensagem = f"📉 *Saída recomendada* em `{simbolo}`\n\n🧠 Motivo: {resultado['motivo']}\n📈 Preço atual: `{preco_saida}`\n💰 Lucro: `{lucro*100:.2f}%`"
                enviar_telegram(mensagem)

        except Exception as e:
            print(f"Erro ao verificar {simbolo}: {e}")

if __name__ == "__main__":
    correr_feedback()
