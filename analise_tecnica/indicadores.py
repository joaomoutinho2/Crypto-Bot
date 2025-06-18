def calcular_indicadores(df):
    from ta.momentum import RSIIndicator
    from ta.trend import EMAIndicator, MACD
    from ta.volatility import BollingerBands

    if len(df) < 50:
        raise ValueError("O DataFrame precisa de pelo menos 50 valores para calcular indicadores.")

    df = df.copy()  # evita SettingWithCopyWarning

    df['rsi'] = RSIIndicator(df['close']).rsi()
    df['ema_diff'] = EMAIndicator(df['close'], 12).ema_indicator() - EMAIndicator(df['close'], 26).ema_indicator()

    macd = MACD(df['close'])
    df['macd_diff'] = macd.macd_diff()

    bb = BollingerBands(df['close'])
    df['bb_pos'] = (df['close'] - bb.bollinger_lband()) / (bb.bollinger_hband() - bb.bollinger_lband())

    if 'macd_diff' not in df.columns or df['macd_diff'].isnull().all():
        raise ValueError("Erro: `macd_diff` não foi calculado corretamente.")

    return df
