import random

def obter_contexto(moeda):
    exemplos = [
        f"Investidores estão otimistas em relação ao {moeda} esta semana.",
        f"Volume de negociação do {moeda} aumentou 25% nas últimas 24h.",
        f"Análise indica possível reversão positiva no {moeda}.",
        f"Mercado de cripto enfrenta incertezas, mesmo para o {moeda}.",
        f"Nenhuma notícia relevante sobre {moeda} foi encontrada."
    ]
    return random.choice(exemplos)