from firebase_admin import firestore
from funcoes import get_historico_1min
from datetime import datetime

db = firestore.client()

def avaliar_saida():
    colecao_posicoes = db.collection("posicoes")
    documentos = colecao_posicoes.stream()

    for doc in documentos:
        posicao = doc.to_dict()
        simbolo = posicao["simbolo"]
        preco_entrada = posicao["preco_entrada"]
        preco_maximo = posicao.get("preco_maximo_alcancado", preco_entrada)

        try:
            df = get_historico_1min(simbolo)
            preco_atual = df['close'].iloc[-1]
        except Exception as e:
            print(f"[ERRO] Falha ao obter preço de {simbolo}: {e}")
            continue

        # Atualizar o pico se o preço atual for o maior até agora
        if preco_atual > preco_maximo:
            db.collection("posicoes").document(doc.id).update({
                "preco_maximo_alcancado": preco_atual
            })
            preco_maximo = preco_atual

        motivo_saida = None

        # 🟢 Trailing Stop: preço caiu 3% abaixo do máximo atingido
        trailing_percent = 0.03
        if preco_atual <= preco_maximo * (1 - trailing_percent):
            motivo_saida = f"Trailing Stop ativado (3% abaixo do pico de {preco_maximo:.2f})"

        # 🔁 Condição técnica de saída
        else:
            rsi = df['RSI'].iloc[-1]
            macd = df['MACD_histograma'].iloc[-1]
            preco = df['close'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            volume = df['volume'].iloc[-1]
            volume_ma = df['volume_ma'].iloc[-1]

            if rsi > 70 and macd < 0 and preco > bb_upper and volume > volume_ma:
                motivo_saida = "Saída técnica: RSI>70, MACD<0, acima da BB e volume alto"

        # Se houver motivo, sair da posição
        if motivo_saida:
            print(f"[SAÍDA] {simbolo}: {motivo_saida} | Entrada: {preco_entrada:.2f} | Atual: {preco_atual:.2f}")

            db.collection("historico_vendas").add({
                "simbolo": simbolo,
                "preco_entrada": preco_entrada,
                "preco_saida": preco_atual,
                "lucro_prejuizo": preco_atual - preco_entrada,
                "motivo": motivo_saida,
                "timestamp": datetime.utcnow()
            })

            db.collection("posicoes").document(doc.id).delete()
