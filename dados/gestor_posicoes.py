from datetime import datetime
from firebase_config import db
from dados.gestor_saldo import carregar_saldo, guardar_saldo

def registar_entrada(simbolo, preco_entrada, contexto, decisao, montante, stop_loss, take_profit):
    doc_ref = db.collection("posicoes").document()
    doc_ref.set(
        {
            "simbolo": simbolo,
            "preco_entrada": preco_entrada,
            "contexto": contexto,
            "decisao": decisao,
            "timestamp_entrada": datetime.utcnow(),
            "em_aberto": True,
            "montante": montante,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
        }, retry=None
    )

def carregar_posicoes_abertas():
    docs = db.collection("posicoes").where("em_aberto", "==", True).stream(retry=None)
    return [doc.to_dict() | {"id": doc.id} for doc in docs]

def fechar_posicao(doc_id, preco_saida):
    doc_ref = db.collection("posicoes").document(doc_id)
    doc = doc_ref.get(retry=None)

    if doc.exists:
        data = doc.to_dict()
        preco_entrada = data.get("preco_entrada", 0)
        montante = data.get("montante", 0)

        lucro_percentual = (preco_saida - preco_entrada) / preco_entrada
        lucro_valor = montante * lucro_percentual

        doc_ref.update(
            {
                "preco_saida": preco_saida,
                "timestamp_saida": datetime.utcnow(),
                "lucro_percentual": round(lucro_percentual * 100, 2),
                "lucro_valor": round(lucro_valor, 2),
                "em_aberto": False,
            }, retry=None
        )

        # Atualizar saldo
        saldo = carregar_saldo()
        novo_saldo = saldo + montante + lucro_valor
        guardar_saldo(round(novo_saldo, 2))
