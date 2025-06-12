from analise_tecnica.indicadores import calcular_indicadores
from analise_fundamental.avaliador_chatgpt import avaliar_com_chatgpt
from analise_fundamental.noticias_scraper import obter_contexto
from dados.gestor_posicoes import registar_entrada
from utils.telegram_alert import enviar_telegram

import joblib
import pandas as pd
import os

# 🔁 Carregar modelo treinado
MODELO_PATH = "modelo_treinado.pkl"
modelo = None
if os.path.exists(MODELO_PATH):
    modelo = joblib.load(MODELO_PATH)
else:
    print("⚠️ Modelo não encontrado. A decisão será feita sem ML.")

def avaliar_entrada(df, simbolo):
    df = calcular_indicadores(df)
    contexto = obter_contexto(simbolo)

    # Verificar se temos modelo e dados suficientes
    if modelo and "rsi" in df and "macd_diff" in df:
        dados = pd.DataFrame([{
            "rsi": df["rsi"].iloc[-1],
            "macd_diff": df["macd_diff"].iloc[-1]
        }])
        previsao = modelo.predict(dados)[0]
    else:
        previsao = 1  # assume positivo se não houver modelo

    if previsao == 1 and df['rsi'].iloc[-1] < 30 and df['macd_diff'].iloc[-1] > 0:
        decisao = avaliar_com_chatgpt(simbolo, contexto)

        if "sim" in decisao.lower():
            preco = df['close'].iloc[-1]

            registar_entrada(simbolo, preco, contexto, decisao)

            mensagem = (
                f"📈 *Entrada registada* em `{simbolo}`\n\n"
                f"📊 RSI < 30, MACD > 0\n"
                f"🤖 ML: *Sim* | GPT: *{decisao}*\n"
                f"💰 Preço de entrada: `{preco}`"
            )
            enviar_telegram(mensagem)

        return f"ML: {previsao}, GPT: {decisao}"

    return "Sem sinal forte"
