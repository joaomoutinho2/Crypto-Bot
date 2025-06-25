from firebase_admin import firestore
from utils.dados_market import obter_df_ativo as get_historico_1min
from utils.telegram_alert import enviar_telegram
from datetime import datetime

db = firestore.client()

def avaliar_saida():
    colecao_posicoes = db.collection("posicoes").where("em_aberto", "==", True)
    documentos = colecao_posicoes.stream(retry=None)

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
            db.collection("posicoes").document(doc.id).update(
                {"preco_maximo_alcancado": preco_atual}, retry=None
            )
            preco_maximo = preco_atual

        motivo_saida = None

        # 🟢 Trailing Stop: preço caiu 3% abaixo do máximo atingido
        trailing_percent = 0.03
        if preco_atual <= preco_maximo * (1 - trailing_percent):
            motivo_saida = f"Trailing Stop ativado (3% abaixo do pico de {preco_maximo:.2f})"

        # 🔁 Condição técnica de saída
        else:
            rsi = df['rsi'].iloc[-1]
            macd = df['macd_diff'].iloc[-1]
            preco = df['close'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            volume = df['volume'].iloc[-1]
            volume_ma = df['volume_ma'].iloc[-1]

            if rsi > 70 and macd < 0 and preco > bb_upper and volume > volume_ma:
                motivo_saida = "Saída técnica: RSI>70, MACD<0, acima da BB e volume alto"

        # Se houver motivo, sair da posição
        if motivo_saida:
            print(f"[SAÍDA] {simbolo}: {motivo_saida} | Entrada: {preco_entrada:.2f} | Atual: {preco_atual:.2f}")

            lucro_valor = preco_atual - preco_entrada
            lucro_percent = (lucro_valor / preco_entrada) * 100

            # Registar no histórico de vendas
            db.collection("historico_vendas").add(
                {
                    "simbolo": simbolo,
                    "preco_entrada": preco_entrada,
                    "preco_saida": preco_atual,
                    "lucro_prejuizo": lucro_valor,
                    "motivo": motivo_saida,
                    "timestamp": datetime.utcnow(),
                }, retry=None
            )

            # Eliminar posição
            db.collection("posicoes").document(doc.id).delete(retry=None)

            # Enviar alerta para o Telegram
            mensagem = (
                f"⚠️ *{motivo_saida}*\n"
                f"📉 *Saída de* `{simbolo}`\n"
                f"💰 Entrada: `{preco_entrada:.4f}` → Saída: `{preco_atual:.4f}`\n"
                f"📊 Resultado: *{lucro_valor:.2f} USDT* ({lucro_percent:.2f}%)"
            )
            enviar_telegram(mensagem)
