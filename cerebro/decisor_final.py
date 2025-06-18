from analise_tecnica.indicadores import calcular_indicadores
from analise_fundamental.avaliador_chatgpt import avaliar_com_chatgpt
from analise_fundamental.noticias_scraper import obter_contexto


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
    """Avalia se deve entrar na moeda retornando resultados estruturados."""
    try:
        df = calcular_indicadores(df)

        if df.empty or 'rsi' not in df.columns or 'macd_diff' not in df.columns:
            return {"erro": "indicadores não disponíveis"}

        df = df.dropna(subset=['rsi', 'macd_diff'])
        if df.empty:
            return {"erro": "indicadores vazios"}

        rsi_val = df['rsi'].iloc[-1]
        macd_val = df['macd_diff'].iloc[-1]
        contexto = obter_contexto(simbolo)

        if modelo:
            dados = pd.DataFrame([{"rsi": rsi_val, "macd_diff": macd_val}])
            previsao = int(modelo.predict(dados)[0])
        else:
            previsao = 1

        decisao = "nao"
        if previsao == 1 and rsi_val < 30 and macd_val > 0:
            decisao = avaliar_com_chatgpt(simbolo, contexto).lower()

        return {"ml": previsao, "gpt": decisao}

    except Exception as e:
        return {"erro": f"Erro em avaliação de {simbolo}: {e}"}
