import pandas as pd

def calcular_montante(df, resultado_ml, decisao_gpt, saldo_virtual):
    """
    Calcula o montante a investir com base em sinais técnicos, ML, GPT e saldo disponível.
    """
    # Parâmetros
    confianca_base = 0.03  # 3%
    confianca_maxima = 0.25  # 25%
    confianca = confianca_base

    # RSI e MACD
    rsi = df["rsi"].iloc[-1]
    macd = df["macd"].iloc[-1]
    macd_signal = df["macd_signal"].iloc[-1]
    volume_atual = df["volume"].iloc[-1]
    volume_passado = df["volume"].iloc[-10]

    if rsi < 25:
        confianca += 0.03
    if macd > macd_signal:
        confianca += 0.05
    if volume_atual > volume_passado:
        confianca += 0.02
    if resultado_ml == 1:
        confianca += 0.05
    if decisao_gpt.lower() == "sim":
        confianca += 0.05

    # Clamp
    confianca = min(confianca, confianca_maxima)

    montante = saldo_virtual * confianca
    montante = round(min(montante, saldo_virtual), 2)

    return montante

def calcular_atr(df, periodo=14):
    """
    Calcula o ATR (Average True Range) para um DataFrame com colunas: high, low, close.
    """
    high = df['high']
    low = df['low']
    close = df['close']

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=periodo).mean()
    return atr

def definir_limites_saida(df, preco_entrada):
    """
    Define stop-loss e take-profit com base na volatilidade (ATR).
    """
    atr = calcular_atr(df).iloc[-1]

    if pd.isna(atr) or atr == 0:
        # Fallback: usar % fixos conservadores
        stop_loss = preco_entrada * 0.95  # -5%
        take_profit = preco_entrada * 1.10  # +10%
    else:
        stop_loss = round(preco_entrada - 2 * atr, 5)
        take_profit = round(preco_entrada + 3 * atr, 5)

    return stop_loss, take_profit
