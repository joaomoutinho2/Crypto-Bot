import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_config import iniciar_firebase
from bot.bot_entrada import correr_analise as entrada
from bot.bot_feedback import verificar_posicoes as feedback

print("✅ Bot em modo contínuo iniciado sem agendamento.")

# Inicializar Firebase
iniciar_firebase()

while True:
    try:
        print("⏳ A correr bot de entrada...")
        entrada()
    except Exception as e:
        print(f"❌ Erro em entrada: {e}")

    try:
        print("🔁 A correr bot de feedback...")
        feedback()
    except Exception as e:
        print(f"❌ Erro em feedback: {e}")

    time.sleep(10)  # Espera de 10 segundos entre iterações
