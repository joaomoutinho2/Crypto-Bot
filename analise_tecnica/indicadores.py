def calcular_indicadores(df):
    from ta.momentum import RSIIndicator
    from ta.trend import EMAIndicator, MACD
    from ta.volatility import BollingerBands

    df['rsi'] = RSIIndicator(df['close']).rsi()
    df['ema_diff'] = EMAIndicator(df['close'], 12).ema_indicator() - EMAIndicator(df['close'], 26).ema_indicator()
    macd = MACD(df['close'])
    df['macd_diff'] = macd.macd_diff()
    bb = BollingerBands(df['close'])
    df['bb_pos'] = (df['close'] - bb.bollinger_lband()) / (bb.bollinger_hband() - bb.bollinger_lband())
    return df