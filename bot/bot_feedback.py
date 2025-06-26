import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ccxt
import pandas as pd
from firebase_config import db
from dados.gestor_posicoes import carregar_posicoes_abertas, fechar_posicao
from utils.dados_market import obter_df_ativo  
from dados.gestor_saldo import carregar_saldo, guardar_saldo
from utils.telegram_alert import enviar_telegram
from datetime import datetime

exchange = ccxt.kucoin()

def carregar_parametros():
    doc = db.collection("parametros_bot").document("estrategias").get()
    if doc.exists:
        return doc.to_dict()
    return {}

def usar_trailing_stop(preco_atual, preco_maximo, trailing_percent):
    return preco_atual <= preco_maximo * (1 - trailing_percent)

def usar_saida_tecnica(df):
    try:
        rsi = df['rsi'].iloc[-1]
        macd = df['macd_diff'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        volume = df['volume'].iloc[-1]
        volume_ma = df['volume_ma'].iloc[-1]
        return rsi > 70 and macd < 0 and df['close'].iloc[-1] > bb_upper and volume > volume_ma
    except:
        return False

def usar_nova_tecnica(df):
    try:
        rsi = df['rsi'].iloc[-1]
        return rsi < 20
    except:
        return False

def usar_cruzamento_medias(df):
    try:
        ma_curta = df['close'].rolling(window=5).mean()
        ma_longa = df['close'].rolling(window=20).mean()
        return ma_curta.iloc[-2] > ma_longa.iloc[-2] and ma_curta.iloc[-1] < ma_longa.iloc[-1]
    except:
        return False

def usar_candle_rejeicao(df):
    try:
        open = df['open'].iloc[-1]
        close = df['close'].iloc[-1]
        high = df['high'].iloc[-1]
        low = df['low'].iloc[-1]
        corpo = abs(close - open)
        sombra_total = (high - low)
        return corpo / sombra_total < 0.2
    except:
        return False

def usar_volume_spike(df):
    try:
        vol = df['volume'].iloc[-1]
        vol_ma = df['volume'].rolling(window=20).mean().iloc[-1]
        return vol > 2 * vol_ma
    except:
        return False

def verificar_posicoes():
    params = carregar_parametros()
    trailing_percent = params.get("trailing_percent", 0.03)

    posicoes = carregar_posicoes_abertas()

    for data in posicoes:
        simbolo = data["simbolo"]
        preco_entrada = data["preco_entrada"]
        montante = data["montante"]
        stop_loss = data["stop_loss"]
        take_profit = data["take_profit"]
        preco_maximo = data.get("preco_maximo_alcancado", preco_entrada)
        doc_id = data["id"]

        try:
            df = obter_df_ativo(simbolo)
            preco_atual = df["close"].iloc[-1]

            motivo = None
            if preco_atual <= stop_loss:
                motivo = "📉 Stop-loss atingido"
            elif preco_atual >= take_profit:
                motivo = "📈 Take-profit atingido"
            elif preco_atual > preco_maximo:
                preco_maximo = preco_atual
                db.collection("posicoes").document(doc_id).update(
                    {"preco_maximo_alcancado": preco_maximo}, retry=None
                )
            elif params.get("usar_trailing_stop", True) and usar_trailing_stop(preco_atual, preco_maximo, trailing_percent):
                motivo = f"Trailing Stop ativado (abaixo de {trailing_percent*100:.1f}% do pico de {preco_maximo:.2f})"
            elif params.get("usar_saida_tecnica", True) and usar_saida_tecnica(df):
                motivo = "Saída técnica: RSI>70, MACD<0, acima da BB e volume alto"
            elif params.get("usar_nova_tecnica", True) and usar_nova_tecnica(df):
                motivo = "Nova técnica: RSI < 20"
            elif params.get("usar_cruzamento_medias", True) and usar_cruzamento_medias(df):
                motivo = "📉 Cruzamento de médias: Curta cruzou abaixo da Longa"
            elif params.get("usar_candle_rejeicao", True) and usar_candle_rejeicao(df):
                motivo = "🚫 Candle de rejeição detectado"
            elif params.get("usar_volume_spike", True) and usar_volume_spike(df):
                motivo = "📊 Volume spike: volume acima do normal"

            if motivo:
                lucro_percentual = (preco_atual - preco_entrada) / preco_entrada * 100
                lucro_valor = montante * (lucro_percentual / 100)

                fechar_posicao(doc_id, preco_atual)
                saldo_atual = carregar_saldo()
                saldo_novo = saldo_atual + lucro_valor
                guardar_saldo(saldo_novo)

                mensagem = (
                    f"{motivo}\n"
                    f"📉 *Saída de* `{simbolo}`\n"
                    f"💰 Entrada: `{preco_entrada:.4f}` → Saída: `{preco_atual:.4f}`\n"
                    f"💼 Lucro: *{lucro_valor:.2f} USDT* ({lucro_percentual:.2f}%)\n"
                    f"🏦 Saldo atualizado: `{saldo_novo:.2f} USDT`"
                )
                enviar_telegram(mensagem)

                db.collection("historico_vendas").add(
                    {
                        "simbolo": simbolo,
                        "preco_entrada": preco_entrada,
                        "preco_saida": preco_atual,
                        "lucro_prejuizo": lucro_valor,
                        "motivo": motivo,
                        "timestamp": datetime.utcnow(),
                    }, retry=None
                )

        except Exception as e:
            print(f"❌ Erro ao verificar posição {simbolo}: {e}")

if __name__ == "__main__":
    verificar_posicoes()