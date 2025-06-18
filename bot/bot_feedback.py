import ccxt
import pandas as pd
from firebase_config import db
from dados.gestor_posicoes import carregar_posicoes_abertas, fechar_posicao
from utils.dados_market import obter_df_ativo  
from dados.gestor_saldo import carregar_saldo
from utils.telegram_alert import enviar_telegram

exchange = ccxt.kucoin()

def verificar_posicoes():
    posicoes = carregar_posicoes_abertas()

    for data in posicoes:
        simbolo = data["simbolo"]
        preco_entrada = data["preco_entrada"]
        montante = data["montante"]
        stop_loss = data["stop_loss"]
        take_profit = data["take_profit"]
        doc_id = data["id"]

        try:
            df = obter_df_ativo(simbolo)
            preco_atual = df["close"].iloc[-1]

            # Decisão de saída
            if preco_atual <= stop_loss:
                motivo = "📉 Stop-loss atingido"
            elif preco_atual >= take_profit:
                motivo = "📈 Take-profit atingido"
            else:
                continue  # mantém a posição

            # Fechar posição
            fechar_posicao(doc_id, preco_atual)

            lucro_percentual = (preco_atual - preco_entrada) / preco_entrada * 100
            lucro_valor = montante * (lucro_percentual / 100)
            saldo_atual = carregar_saldo()

            mensagem = (
                f"{motivo}\n"
                f"📉 *Saída de* `{simbolo}`\n"
                f"💰 Preço de saída: `{preco_atual:.4f}`\n"
                f"💼 Lucro: *{lucro_valor:.2f} USDT* ({lucro_percentual:.2f}%)\n"
                f"🏦 Saldo atualizado: `{saldo_atual:.2f} USDT`"
            )
            enviar_telegram(mensagem)

        except Exception as e:
            print(f"❌ Erro ao verificar posição {simbolo}: {e}")


if __name__ == "__main__":
    verificar_posicoes()
