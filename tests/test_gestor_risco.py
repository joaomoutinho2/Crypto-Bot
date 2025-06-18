import pandas as pd
import math

from utils.gestor_risco import calcular_montante, calcular_atr, definir_limites_saida


def test_calcular_atr():
    data = {
        'high': [10, 12, 11, 13, 14],
        'low': [8, 9, 10, 11, 12],
        'close': [9, 11, 10.5, 12, 13]
    }
    df = pd.DataFrame(data)
    periodo = 3

    # Expected ATR calculated manually
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - df['close'].shift(1)).abs()
    tr3 = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    expected = tr.rolling(window=periodo).mean()

    result = calcular_atr(df, periodo)
    pd.testing.assert_series_equal(result, expected)


def test_definir_limites_saida():
    data = {
        'high': [10, 12, 11, 13, 14],
        'low': [8, 9, 10, 11, 12],
        'close': [9, 11, 10.5, 12, 13]
    }
    df = pd.DataFrame(data)
    preco_entrada = 15
    atr = calcular_atr(df).iloc[-1]
    stop_loss, take_profit = definir_limites_saida(df, preco_entrada)

    if not math.isnan(atr) and atr != 0:
        expected_sl = round(preco_entrada - 2 * atr, 5)
        expected_tp = round(preco_entrada + 3 * atr, 5)
    else:
        expected_sl = preco_entrada * 0.95
        expected_tp = preco_entrada * 1.10

    assert stop_loss == expected_sl
    assert take_profit == expected_tp


def test_calcular_montante():
    rows = 11
    df = pd.DataFrame({
        'rsi': [20]*rows,
        'macd': [1.5]*rows,
        'macd_signal': [1.0]*rows,
        'volume': list(range(100, 100 + rows))
    })
    resultado_ml = 1
    decisao_gpt = 'sim'
    saldo = 1000
    montante = calcular_montante(df, resultado_ml, decisao_gpt, saldo)

    expected_conf = 0.03 + 0.03 + 0.05 + 0.02 + 0.05 + 0.05
    expected_montante = round(min(saldo * expected_conf, saldo), 2)

    assert montante == expected_montante
