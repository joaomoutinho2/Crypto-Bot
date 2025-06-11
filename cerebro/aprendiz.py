from firebase_admin import firestore

def analisar_erros():
    db = firestore.client()
    docs = db.collection("previsoes").where("avaliado", "==", True).stream()
    acertos, erros = 0, 0
    lições = []

    for doc in docs:
        d = doc.to_dict()
        if d.get("lucro", 0) > 0:
            acertos += 1
        else:
            erros += 1
            lições.append({
                "simbolo": d.get("simbolo"),
                "rsi": d.get("rsi"),
                "macd_diff": d.get("macd_diff"),
                "decisao": d.get("decisao"),
                "contexto": d.get("contexto")
            })

    resumo = {
        "acertos": acertos,
        "erros": erros,
        "lições": lições[-5:]  # últimas 5 lições aprendidas
    }

    db.collection("aprendizagem").document("resumo").set(resumo)
    print(f"📚 Aprendizagem atualizada: {acertos} acertos / {erros} erros")