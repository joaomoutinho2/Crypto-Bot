import pandas as pd
import ta

# Carregar o histórico de preços
df = pd.read_csv("BTCUSDT_1min.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# === CALCULAR INDICADORES ===

# RSI
df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

# MACD
macd = ta.trend.MACD(df['close'])
df['MACD'] = macd.macd()
df['MACD_signal'] = macd.macd_signal()
df['MACD_histograma'] = macd.macd_diff()

# Bandas de Bollinger
bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
df['bb_upper'] = bb.bollinger_hband()
df['bb_lower'] = bb.bollinger_lband()
df['bb_middle'] = bb.bollinger_mavg()

# Volume médio
df['volume_ma'] = df['volume'].rolling(window=20).mean()

# Remover linhas com NaN (início das médias móveis)
df.dropna(inplace=True)

# Salvar com indicadores
df.to_csv("BTCUSDT_1min_com_indicadores.csv", index=False)

print("✅ Indicadores calculados e ficheiro guardado como BTCUSDT_1min_com_indicadores.csv")
