from firebase_config import iniciar_firebase

iniciar_firebase()

from bot.bot_entrada import correr_analise as entrada
from bot.bot_feedback import verificar_posicoes as feedback
import schedule
import time


def tarefa_entrada():
    print("⏳ A correr bot de entrada...")
    entrada()

def tarefa_feedback():
    print("🔁 A correr bot de feedback...")
    feedback()

# Agendamentos
schedule.every(10).minutes.do(tarefa_entrada)
schedule.every(5).minutes.do(tarefa_feedback)

print("✅ Bot em modo contínuo iniciado.")
while True:
    schedule.run_pending()
    time.sleep(1)
