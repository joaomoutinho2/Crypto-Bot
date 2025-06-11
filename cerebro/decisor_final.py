from analise_tecnica.indicadores import calcular_indicadores
from analise_fundamental.avaliador_chatgpt import avaliar_com_chatgpt
from analise_fundamental.noticias_scraper import obter_contexto
from dados.gestor_dados import guardar_previsao

def avaliar_entrada(df, simbolo):
    df = calcular_indicadores(df)
    contexto = obter_contexto(simbolo)
    if df['rsi'].iloc[-1] < 30 and df['macd_diff'].iloc[-1] > 0:
        decisao = avaliar_com_chatgpt(simbolo, contexto)
        guardar_previsao(simbolo, decisao, contexto)
        return decisao
    return "Sem sinal forte"
