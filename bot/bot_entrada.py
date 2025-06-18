import ccxt
import pandas as pd
from datetime import datetime

from cerebro.decisor_final import avaliar_entrada
from firebase_config import db
from utils.gestor_risco import calcular_montante, definir_limites_saida
from utils.telegram_alert import enviar_telegram
from utils.dados_market import obter_df_ativo
from dados.gestor_posicoes import registar_entrada
from dados.gestor_saldo import carregar_saldo, guardar_saldo

def correr_analise():
    exchange = ccxt.kucoin()
    simbolos = [s for s in exchange.load_markets().keys() if "/USDT" in s]
    saldo_virtual = carregar_saldo()

    for simbolo in simbolos[:30]:
        try:
            df = obter_df_ativo(simbolo)  # Use a função que calcula os indicadores técnicos

            try:
                resultado = avaliar_entrada(df, simbolo)

                # Verificação extra de indicadores válidos
                if df[['rsi', 'macd_diff']].iloc[-1].isnull().any():
                    raise ValueError("Indicadores insuficientes (NaN detectado)")

                if isinstance(resultado, str) and "ML:" in resultado and "GPT:" in resultado:
                    resultado_ml = 1 if "ML: 1" in resultado else 0
                    decisao_gpt = resultado.split("GPT:")[1].strip().lower()
                else:
                    resultado_ml = 0
                    decisao_gpt = "nao"

            except Exception as e:
                print(f"❌ Erro em análise de {simbolo}: {e}")
                continue

            preco = df['close'].iloc[-1]
            contexto = {"timeframe": "1m", "limite": 100}

            montante = calcular_montante(df, resultado_ml, decisao_gpt, saldo_virtual)

            if montante > 0:
                stop_loss, take_profit = definir_limites_saida(df, preco)

                registar_entrada(simbolo, preco, contexto, decisao_gpt, montante, stop_loss, take_profit)

                mensagem = (
                    f"📈 *Nova entrada registada em* `{simbolo}`\n"
                    f"💰 Montante: *{montante:.2f} USDT*\n"
                    f"🟢 Preço entrada: `{preco:.4f}`\n"
                    f"🔻 Stop-Loss: `{stop_loss:.4f}`\n"
                    f"🔺 Take-Profit: `{take_profit:.4f}`\n"
                    f"🤖 ML: {'Sim' if resultado_ml == 1 else 'Não'} | GPT: {decisao_gpt.capitalize()}\n"
                    f"🧠 Contexto:\n`{contexto}`"
                )
                enviar_telegram(mensagem)

                saldo_virtual -= montante
                guardar_saldo(saldo_virtual)

        except Exception as e:
            print(f"❌ Erro ao analisar {simbolo}: {e}")
