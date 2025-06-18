# 📁 programa_investimento/
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
programa_investimento/
├── analise_tecnica/       # RSI, MACD, Bollinger, etc.
├── analise_fundamental/   # GPT-4o, scraper de contexto
├── cerebro/               # Tomada de decisão e aprendizagem
│   └── modelo/            # Treino e avaliação de ML
├── dados/                 # Firestore + modelos + saldo
├── bot/                   # Entrada de sinais e feedback de lucro
├── painel/                # Streamlit com saldo e decisões
├── utils/                 # Helpers e formatação
├── scripts/               # Ferramentas e agendadores
├── firebase_config.py     # Inicia Firebase
├── main.py                # Ponto de entrada do bot
├── requirements.txt       # Bibliotecas
└── .env                   # Credenciais sensíveis
```

## 🔧 Como Correr Localmente
1. Clona o projeto:
```bash
git clone https://github.com/teu_repositorio/programa_investimento.git
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
python cerebro/modelo/treino_modelo.py
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

6. (Opcional) Para executar em modo contínuo:
```bash
python scripts/loop_bot.py
```

7. Para ver o painel:
```bash
streamlit run painel/painel.py
```

## ☁️ Uso no Render
- Cria dois serviços:
  - `bot_entrada` com `main.py`
  - `bot_feedback` com `bot/bot_feedback.py` (cron: cada hora ou 2h)
- Coloca as variáveis de ambiente `.env` no Render

## 📈 Funcionalidades Futuras
- Scraping real de notícias (CoinTelegraph, Twitter, etc.)
- Uso ativo do modelo RandomForest na decisão
- Feedback do utilizador via Telegram ou painel

---
Desenvolvido com ❤️ por [o teu nome/organização].
