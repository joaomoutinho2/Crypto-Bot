from analise_tecnica.indicadores import calcular_indicadores

def avaliar_saida(df):
    df = calcular_indicadores(df)
    rsi = df["rsi"].iloc[-1]
    macd = df["macd_diff"].iloc[-1]

    if rsi > 70 and macd < 0:
        return {"acao": "sair", "motivo": "RSI elevado e MACD negativo"}
    return {"acao": "manter"}
