# 📈 NIFTY Trader Pro

> **NIFTY Stock Tracker & Algo Trading Platform** — Zerodha Kite Connect + Perplexity AI Research + Option Strategy Builder

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Zerodha Kite](https://img.shields.io/badge/Zerodha-Kite%20Connect-387ED1?logo=zerodha&logoColor=white)](https://kite.trade)
[![Perplexity AI](https://img.shields.io/badge/Perplexity-AI%20Research-20B2AA)](https://docs.perplexity.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A full-stack **algorithmic trading dashboard** built with Streamlit, powered by **Zerodha Kite Connect** for live market data and order execution, **Perplexity AI** for real-time stock research, and a built-in **Options Strategy Builder** for NIFTY/BANKNIFTY derivatives.

---

## 🚀 Features

### 📊 Live Market Dashboard
- Real-time NIFTY 50 index tracking with live quotes via Kite Connect WebSocket
- Candlestick + volume charts using Plotly with multiple timeframes (1m, 5m, 15m, 1D)
- Portfolio P&L tracker with unrealized/realized breakdowns
- Watchlist management with alert triggers

### 🤖 Perplexity AI Research Engine
- One-click AI-powered fundamental + technical research for any NSE/BSE stock
- News sentiment analysis with source citations
- Earnings summaries, analyst ratings, and sector comparisons
- Inline research panel — no tab switching needed

### 🎯 Options Strategy Builder
- Build multi-leg options strategies: Bull Call Spread, Bear Put Spread, Iron Condor, Straddle, Strangle
- Real-time Greeks (Delta, Gamma, Theta, Vega) calculation using `scipy`
- P&L payoff diagram at expiry with interactive strike selection
- Option Chain viewer with OI buildup and PCR (Put-Call Ratio)

### ⚡ Algo Trading Engine
- Schedule-based strategy execution using `schedule` library
- Pre-built strategies: Moving Average Crossover, RSI Overbought/Oversold, Supertrend
- Paper trading mode with simulated order fills
- Order book with execution history, slippage tracking

### 🔐 Secure Auth
- Kite Connect OAuth 2.0 login flow
- TOTP-based auto-login support via `pyotp` (optional)
- Session token management with `.env` based secrets

---

## 🧱 Project Structure

```
nifty-trader-pro/
│
├── pages/                    # Streamlit multi-page app
│   ├── __init__.py
│   ├── 01_Dashboard.py       # Live market overview
│   ├── 02_Research.py        # Perplexity AI stock research
│   ├── 03_Options.py         # Options strategy builder
│   ├── 04_AlgoTrading.py     # Strategy builder & scheduler
│   └── 05_Portfolio.py       # Holdings & P&L tracker
│
├── utils/                    # Shared utility modules
│   ├── __init__.py
│   ├── kite_client.py        # Kite Connect session wrapper
│   ├── market_data.py        # OHLCV data fetcher + indicators
│   ├── options_engine.py     # Greeks calculator, payoff logic
│   ├── perplexity_client.py  # Perplexity AI API wrapper
│   └── strategy_engine.py   # Algo strategy logic
│
├── .env.example              # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / UI** | Streamlit 1.35 |
| **Broker API** | Zerodha Kite Connect v5 |
| **AI Research** | Perplexity AI (Sonar API) |
| **Charting** | Plotly 5.22 |
| **Technical Indicators** | `ta` library (RSI, MACD, Bollinger, Supertrend) |
| **Options Math** | `scipy` (Black-Scholes, Greeks) |
| **Data Processing** | Pandas 2.2, NumPy 1.26 |
| **Scheduling** | `schedule` 1.2 |
| **Auth / TOTP** | `pyotp` 2.9 |
| **Config** | `python-dotenv` |

---

## 🛠️ Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Ank576/nifty-trader-pro.git
cd nifty-trader-pro
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Zerodha Kite Connect
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here

# Perplexity AI
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Optional: TOTP for auto-login (from Zerodha app authenticator)
KITE_TOTP_SECRET=your_totp_secret_here
```

> 🔑 **Get your API keys:**
> - **Kite Connect**: [kite.trade/developers](https://kite.trade/developers) → Create an app
> - **Perplexity AI**: [docs.perplexity.ai](https://docs.perplexity.ai) → API Keys section

### 5. Run the Application

```bash
streamlit run pages/01_Dashboard.py
```

Or launch the full multi-page app:

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` by default.

---

## 🔑 Zerodha Kite Connect — Login Flow

1. Click **"Login with Zerodha"** on the sidebar
2. You'll be redirected to Kite's OAuth page
3. After login, Kite redirects back with a `request_token` in the URL
4. The app exchanges this token for an `access_token` and stores it in the session
5. If `KITE_TOTP_SECRET` is set, auto-login is triggered without manual browser redirect

> ⚠️ **Note:** Kite Connect API access requires a subscription (₹2000/month). Paper trading mode works without it.

---

## 📐 Options Strategy Builder — Usage

1. Navigate to **Options** page
2. Select underlying: `NIFTY`, `BANKNIFTY`, or any F&O stock
3. Choose expiry date from the live option chain
4. Pick a strategy template (or build custom legs):
   - **Bull Call Spread**: Buy lower strike call + Sell higher strike call
   - **Iron Condor**: Sell OTM call + Buy further OTM call + Sell OTM put + Buy further OTM put
   - **Straddle**: Buy ATM call + Buy ATM put
5. View the **P&L payoff chart** at expiry and current Greeks
6. Click **Place Order** to send legs to Kite (live) or simulate (paper mode)

---

## 🤖 Perplexity AI Research — Usage

1. Navigate to **Research** page
2. Enter any NSE ticker (e.g., `RELIANCE`, `INFY`, `COALINDIA`)
3. Select research type:
   - **Quick Summary**: 2-minute fundamental snapshot
   - **Deep Dive**: Full analysis with news, earnings, sector context
   - **Options View**: IV rank, put/call sentiment, upcoming events
4. Results stream inline with source citations

---

## 📋 Algo Strategy Configuration

Strategies are defined in `utils/strategy_engine.py`. Example — Moving Average Crossover:

```python
strategy = {
    "name": "MA Crossover",
    "symbol": "NIFTY 50",
    "fast_period": 9,
    "slow_period": 21,
    "quantity": 50,          # 1 lot NIFTY
    "sl_pct": 0.5,           # 0.5% stop loss
    "target_pct": 1.0,       # 1% target
    "trade_mode": "paper"    # "paper" or "live"
}
```

Schedule execution in `pages/04_AlgoTrading.py`:

```python
schedule.every(5).minutes.do(run_strategy, strategy)
```

---

## 🛡️ Disclaimer

> **This project is for educational and research purposes only.**
> Trading in equities, futures, and options involves significant financial risk. Past performance is not indicative of future results. The author is not a SEBI-registered investment advisor. Do not use this tool to make real financial decisions without consulting a qualified advisor.
> Never trade with money you cannot afford to lose.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'feat: add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

[MIT](LICENSE) © [Ankit Saxena](https://github.com/Ank576)

---

<p align="center">Built with ❤️ using Streamlit + Zerodha Kite Connect + Perplexity AI</p>
