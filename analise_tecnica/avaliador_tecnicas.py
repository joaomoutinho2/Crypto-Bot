import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from firebase_config import db
from collections import defaultdict

def avaliar_tecnicas():
    docs = db.collection("historico_vendas").stream()
    dados = []

    for doc in docs:
        d = doc.to_dict()
        if "motivo" in d and "lucro_prejuizo" in d:
            dados.append({
                "estrategia": d["motivo"],
                "lucro": d["lucro_prejuizo"]
            })

    if not dados:
        print("❌ Nenhuma venda encontrada com motivo registrado.")
        return

    df = pd.DataFrame(dados)
    resumo = df.groupby("estrategia").agg(
        total_vezes=("lucro", "count"),
        total_lucro=("lucro", "sum"),
        media_lucro=("lucro", "mean"),
        taxa_sucesso=("lucro", lambda x: (x > 0).sum() / len(x))
    ).reset_index()

    print("\n📊 Avaliação de Estratégias:")
    print(resumo)

    # Enviar para o Firestore
    estatisticas = {}
    for _, row in resumo.iterrows():
        estatisticas[row["estrategia"]] = {
            "total_vezes": int(row["total_vezes"]),
            "total_lucro": float(row["total_lucro"]),
            "media_lucro": float(row["media_lucro"]),
            "taxa_sucesso": float(row["taxa_sucesso"])
        }

    db.collection("estatisticas_tecnicas").document("resumo").set(estatisticas)
    print("\n✅ Estatísticas guardadas em 'estatisticas_tecnicas/resumo'.")

if __name__ == "__main__":
    avaliar_tecnicas()
