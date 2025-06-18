from analise_tecnica.indicadores import calcular_indicadores
from analise_fundamental.avaliador_chatgpt import avaliar_com_chatgpt
from analise_fundamental.noticias_scraper import obter_contexto
from dados.gestor_posicoes import registar_entrada
from utils.telegram_alert import enviar_telegram
from utils.gestor_risco import calcular_montante, definir_limites_saida
from dados.gestor_saldo import carregar_saldo, guardar_saldo

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
    try:
        df = calcular_indicadores(df)

        # Verifica existência e validade dos indicadores
        if df.empty or 'rsi' not in df.columns or 'macd_diff' not in df.columns:
            return "Erro: indicadores não disponíveis"

        df = df.dropna(subset=['rsi', 'macd_diff'])
        if df.empty:
            return "Erro: indicadores vazios"

        rsi_val = df['rsi'].iloc[-1]
        macd_val = df['macd_diff'].iloc[-1]
        contexto = obter_contexto(simbolo)

        if modelo:
            dados = pd.DataFrame([{"rsi": rsi_val, "macd_diff": macd_val}])
            previsao = modelo.predict(dados)[0]
        else:
            previsao = 1

        if previsao == 1 and rsi_val < 30 and macd_val > 0:
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

    except Exception as e:
        return f"Erro em avaliação de {simbolo}: {e}"
