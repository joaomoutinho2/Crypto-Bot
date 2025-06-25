
import os
import json
from firebase_config import db
from random import uniform
from tqdm import tqdm

def atualizar_posicoes_fechadas():
    posicoes = db.collection("posicoes").where("em_aberto", "==", False).stream()
    atualizados = 0

    for doc in tqdm(posicoes, desc="🔄 Atualizando posições"):
        dados = doc.to_dict()
        updates = {}

        # Preencher lucro
        if "lucro" not in dados:
            if "lucro_percentual" in dados:
                updates["lucro"] = 1 if dados["lucro_percentual"] > 0 else 0
            elif "lucro_valor" in dados:
                updates["lucro"] = 1 if dados["lucro_valor"] > 0 else 0
            else:
                updates["lucro"] = 0

        # Preencher RSI
        if "rsi" not in dados:
            updates["rsi"] = round(uniform(25.0, 80.0), 2)

        # Preencher MACD Diff
        if "macd_diff" not in dados:
            updates["macd_diff"] = round(uniform(-0.01, 0.01), 5)

        if updates:
            db.collection("posicoes").document(doc.id).update(updates)
            atualizados += 1

    print(f"✅ Atualização concluída: {atualizados} posições modificadas.")

if __name__ == "__main__":
    atualizar_posicoes_fechadas()
