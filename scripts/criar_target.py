import pandas as pd

# Carregar o CSV com indicadores
df = pd.read_csv("BTCUSDT_1min_com_indicadores.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

# === CRIAR TARGET ===

# Calcular o retorno futuro em 5 minutos
df['retorno_futuro'] = df['close'].shift(-5) / df['close'] - 1

# Criar o target binário:
# 1 → se subir mais de 0.5%
# 0 → se subir menos ou cair
df['target'] = (df['retorno_futuro'] > 0.005).astype(int)

# Remover linhas com NaN (últimas 5 linhas não têm futuro conhecido)
df.dropna(inplace=True)

# Guardar ficheiro final
df.to_csv("dados_treinamento.csv", index=False)

print("✅ Target criado e ficheiro guardado como dados_treinamento.csv")
