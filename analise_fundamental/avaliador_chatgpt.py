import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def avaliar_com_chatgpt(moeda, contexto):
    prompt = f"""
    A moeda {moeda} está com sinais técnicos de entrada.
    Contexto adicional:
    {contexto}

    Devo entrar agora nesta moeda?
    Responde apenas com: 'sim', 'não' ou 'incerto'. Depois explica brevemente.
    """
    resposta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta['choices'][0]['message']['content']