# 🧠 Factor Rotation Backtest Engine

A single-file, portable Python application that backtests a dynamic **factor rotation strategy** across U.S. equity markets. Built using **Dash**, **Plotly**, and **YFinance**, this engine evaluates monthly factor performance (Value, Momentum, Low Volatility) and reallocates to the top-performing factor's top stocks with optional trading cost adjustments.

---

## 🚀 Features

- 📊 **Factor Momentum Model** — Rotates across Value, Momentum, and Low Volatility ETFs based on 1-month trailing returns
- 🔄 **Top Stock Mapping** — Selects 3 leading stocks per factor using predefined mappings
- 💵 **Cost-Adjusted Returns** — Models realistic slippage, bid/ask spread, and turnover-based cost drag
- 📉 **Performance Metrics** — Auto-computes CAGR, Sharpe, Calmar, Drawdown, and Benchmark (SPY) comparison
- 🌐 **Interactive Dashboard** — Fully browser-based Plotly + Dash interface with toggle for cost inclusion
- 📦 **One-Script Simplicity** — Easy to deploy, understand, and share; no complicated project structure

---

## 🧪 Sample Use Case

A retail quant or student can:
1. Run the engine monthly to determine leading factors
2. Evaluate the suggested stock picks for the month
3. Study the impact of trading costs on strategy efficiency

---

## 🛠️ Technologies

- Python 3.11+
- Dash
- Plotly
- Pandas / NumPy
- YFinance
- PyNgrok (for local web exposure)

---

## 📈 Example Output

- Strategy vs. SPY performance chart
- Drawdown curves (optional)
- Monthly factor allocations
- Stock suggestions for the current month

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
python app.py
