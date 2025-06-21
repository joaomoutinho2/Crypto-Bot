import ccxt
import pandas as pd
import ta

def obter_df_ativo(simbolo):
    """
    Vai buscar os dados de mercado da KuCoin para o símbolo dado
    e calcula todos os indicadores técnicos necessários para o bot.
    """
    exchange = ccxt.kucoin()
    ohlcv = exchange.fetch_ohlcv(simbolo, timeframe='1m', limit=100)

    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # Indicadores técnicos
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    macd = ta.trend.MACD(close=df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()

    # Bandas de Bollinger
    bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_middle'] = bb.bollinger_mavg()

    # Média móvel do volume
    df['volume_ma'] = df['volume'].rolling(window=20).mean()

    # Limpar NaNs iniciais
    df = df.dropna()

    return df
