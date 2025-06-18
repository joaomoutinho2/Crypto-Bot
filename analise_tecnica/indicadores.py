import pandas as pd
import ta


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula indicadores técnicos e normaliza nomes das colunas."""
    df = df.copy()
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
    macd = ta.trend.MACD(close=df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    bb = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_middle"] = bb.bollinger_mavg()

    df["volume_ma"] = df["volume"].rolling(window=20).mean()

    return df.dropna()
