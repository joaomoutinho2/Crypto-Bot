import pandas as pd
import ta
import matplotlib.pyplot as plt

# === PARÂMETROS ===
capital_inicial = 1000
sl_percent = 0.03  # Stop-loss
tp_percent = 0.06  # Take-profit
trailing_percent = 0.03

# === 1. Carregar CSV com dados históricos ===
df = pd.read_csv("BTCUSDT_1min.csv")  # ou outro par
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# === 2. Calcular indicadores ===
df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
macd = ta.trend.MACD(df['close'])
df['MACD_histograma'] = macd.macd_diff()
bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
df['bb_lower'] = bb.bollinger_lband()
df['bb_upper'] = bb.bollinger_hband()
df['volume_ma'] = df['volume'].rolling(window=20).mean()

# === 3. Loop simulado ===
capital = capital_inicial
posicao = None
entradas, saidas = [], []

for i in range(20, len(df)):  # começa após 20 para evitar NaN dos indicadores
    linha = df.iloc[i]
    
    if posicao is None:
        # Verifica condições de entrada
        if (
            linha['RSI'] < 30 and
            linha['MACD_histograma'] > 0 and
            linha['close'] < linha['bb_lower'] and
            linha['volume'] > linha['volume_ma']
        ):
            posicao = {
                'entrada': linha['close'],
                'pico': linha['close'],
                'timestamp': linha.name
            }
            entradas.append(linha.name)
    else:
        preco = linha['close']
        if preco > posicao['pico']:
            posicao['pico'] = preco

        stop = posicao['pico'] * (1 - trailing_percent)
        take = posicao['entrada'] * (1 + tp_percent)
        loss = posicao['entrada'] * (1 - sl_percent)

        if preco <= stop:
            capital += preco - posicao['entrada']
            saidas.append((linha.name, preco, "Trailing Stop"))
            posicao = None
        elif preco >= take:
            capital += preco - posicao['entrada']
            saidas.append((linha.name, preco, "Take Profit"))
            posicao = None
        elif preco <= loss:
            capital += preco - posicao['entrada']
            saidas.append((linha.name, preco, "Stop Loss"))
            posicao = None

# === 4. Resultados ===
print(f"Capital final: {capital:.2f} USDT")
print(f"Lucro líquido: {capital - capital_inicial:.2f}")
print(f"Trades realizados: {len(saidas)}")

# === 5. Gráfico do saldo (simples) ===
plt.title("Equity Curve (simulação)")
plt.plot([capital_inicial] + [capital_inicial + sum([s[1] - df.loc[e].close for e, s in zip(entradas, saidas)])])
plt.xlabel("Tempo (simplificado)")
plt.ylabel("Saldo USDT")
plt.grid()
plt.show()
