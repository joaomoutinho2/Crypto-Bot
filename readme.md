# 📁 Crypto-Bot
# Estrutura organizada e funcional do projeto inteligente com IA, Firebase e KuCoin

# === README.md ===
# 🤖 Programa de Investimento Inteligente com IA + Firebase + KuCoin

## 🚀 Visão Geral
Este bot toma decisões de investimento em criptomoedas de forma totalmente automática. Ele:
- Analisa pares USDT da KuCoin
- Usa indicadores técnicos (RSI, MACD, etc.)
- Valida sinais com IA (GPT-4o)
- Aprende com os erros
- Mostra tudo num painel via Streamlit

## 🗂️ Estrutura do Projeto
```
Crypto-Bot/
├── analise_tecnica/       # RSI, MACD, Bollinger, etc.
├── analise_fundamental/   # GPT-4o, scraper de contexto
├── cerebro/               # Tomada de decisão e aprendizagem
├── dados/                 # Firestore + modelos + saldo
├── bot/                   # Entrada de sinais e feedback de lucro
├── painel/                # Streamlit com saldo e decisões
├── utils/                 # Helpers e formatação
├── firebase_config.py     # Inicia Firebase
├── main.py                # Ponto de entrada do bot
├── requirements.txt       # Bibliotecas
└── .env                   # Credenciais sensíveis
```

Cada pasta possui uma responsabilidade clara:
- **analise_tecnica** – implementação dos indicadores de mercado.
- **analise_fundamental** – obtém contexto externo e usa o GPT.
- **cerebro** – módulo de decisão e aprendizagem do bot.
- **dados** – persistência no Firestore e modelos de ML.
- **bot** – scripts que executam entradas e feedback de lucro.
- **painel** – dashboard Streamlit para acompanhamento em tempo real.
- **utils** – funções auxiliares e formatação em geral.

## 🔧 Como Correr Localmente
1. Clona o projeto:
```bash
git clone https://github.com/seu_usuario/Crypto-Bot.git
cd Crypto-Bot
```

2. Cria o `.env`:
```
OPENAI_API_KEY=...
FIREBASE_JSON={...}  # JSON compactado como string
```

3. Instala as dependências:
```bash
pip install -r requirements.txt
```

### Gerar ou obter o modelo
O bot carrega o modelo RandomForest mais recente do Firebase. Caso ainda não
exista um modelo disponível, podes treinar e enviar um novo executando:
```bash
python modelo/treino_modelo.py
```
O arquivo `modelo_rf.pkl` será criado localmente (e está ignorado pelo Git) e
enviado para o Firestore, de onde o bot o irá buscar automaticamente.

4. (Opcional) Gere indicadores técnicos com o dataset `BTCUSDT_1min.csv`:
```bash
python analise_tecnica/indicadores.py
```

5. Corre o bot principal:
```bash
python main.py
```

6. Para ver o painel:
```bash
streamlit run painel/painel.py
```

Ao rodar `main.py`, o bot analisa cerca de 30 mercados e registra as entradas
que satisfazem os filtros. Com `streamlit run painel/painel.py` é possível
acompanhar em tempo real as posições abertas, fechamentos e saldo virtual.

## 🔌 Tecnologias e Credenciais
O projeto utiliza alguns serviços externos:
- **OpenAI API** para análise textual;
- **Firebase Firestore** para persistir estado e modelos;
- **KuCoin via CCXT** para obter dados de mercado.

Para executar é necessário definir `OPENAI_API_KEY` e `FIREBASE_JSON` no
arquivo `.env`. O JSON do Firebase pode ser gerado seguindo a documentação
[Creating a service account](https://firebase.google.com/docs/admin/setup).
As coleções `saldo_virtual`, `historico_saldo` e `posicoes` são criadas
automaticamente na primeira execução.

## ☁️ Uso no Render
- Cria dois serviços:
  - `bot_entrada` com `main.py`
  - `bot_feedback` com `bot/bot_feedback.py` (cron: cada hora ou 2h)
- Coloca as variáveis de ambiente `.env` no Render

## 📈 Funcionalidades Futuras
- Scraping real de notícias (CoinTelegraph, Twitter, etc.)
- Uso ativo do modelo RandomForest na decisão (parcialmente implementado)
- Feedback do utilizador via Telegram ou painel

---
Desenvolvido com ❤️ por [Seu nome ou organização].
