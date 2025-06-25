import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from modelo.avaliador_modelo import prever_subida

def correr_analise():
    """Percorre os principais mercados avaliando possíveis entradas.

    Para cada par USDT da KuCoin são obtidos os dados de mercado e
    calculados os indicadores técnicos. Em seguida o modelo de Machine
    Learning e o GPT decidem se a posição deve ser aberta. Quando todos
    os critérios positivos se alinham, a função registra a entrada e
    atualiza o saldo virtual.
    """
    exchange = ccxt.kucoin()
    simbolos = [s for s in exchange.load_markets().keys() if "/USDT" in s]
    saldo_virtual = carregar_saldo()

    for simbolo in simbolos[:30]:
        try:
            df = obter_df_ativo(simbolo)  # Use a função que calcula os indicadores técnicos

            # Verificar indicadores técnicos
            rsi = df['rsi'].iloc[-1]
            macd_hist = df['macd_diff'].iloc[-1]
            preco = df['close'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            volume = df['volume'].iloc[-1]
            volume_ma = df['volume_ma'].iloc[-1]

            condicoes_tecnicas = [
                rsi < 30,
                macd_hist > 0,
                preco < bb_lower,
                volume > volume_ma,
            ]

            # Após verificar os sinais técnicos
            if all(condicoes_tecnicas) and prever_subida(df):
                print(f"[ENTRADA] Confirmado por modelo ML via Firebase ✅")

                # Avaliar entrada com base em ML e GPT
                try:
                    resultado = avaliar_entrada(df, simbolo)

                    if isinstance(resultado, dict):
                        resultado_ml = int(resultado.get("ml", 0))
                        decisao_gpt = resultado.get("gpt", "nao").lower()
                    else:
                        resultado_ml = 0
                        decisao_gpt = "nao"

                except Exception as e:
                    print(f"❌ Erro em análise de {simbolo}: {e}")
                    continue

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
            else:
                print(f"[IGNORADO] Rejeitado pelo modelo ML")

        except Exception as e:
            print(f"❌ Erro ao analisar {simbolo}: {e}")
