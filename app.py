import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

# ------------------- SETTINGS -------------------
slippage_estimate = 0.0005
bid_ask_spread = 0.0003
cost_multiplier = 1
# ------------------------------------------------

factor_etfs = {
    "VLUE": "Value",
    "MTUM": "Momentum",
    "SPLV": "Low Volatility",
    "SPY": "Benchmark"
}

factor_top_stocks = {
    "Value": ["JPM", "BRK-B", "META"],
    "Momentum": ["NVDA", "JPM", "AMZN"],
    "Low Volatility": ["MSFT", "BRK-B", "JPM"]
}

start_date = "2015-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')

# Data download
etf_data = yf.download(list(factor_etfs.keys()), start=start_date, end=end_date, auto_adjust=True)['Close']
all_stocks = list({stock for stocks in factor_top_stocks.values() for stock in stocks})
stock_data = yf.download(all_stocks, start=start_date, end=end_date, auto_adjust=True)['Close']

# Monthly resample
etf_monthly = etf_data.resample("ME").last().ffill()
stock_monthly = stock_data.resample("ME").last().ffill()
etf_returns = etf_monthly.pct_change()
benchmark_returns = etf_returns["SPY"]

# Backtest logic
def run_backtest(include_costs=True):
    strategy_returns, best_factors, last_holdings = [], [], set()
    for i in range(1, len(etf_returns)):
        prev_month = etf_returns.iloc[i - 1].drop("SPY", errors='ignore')
        if prev_month.isnull().all():
            continue
        best_etf = prev_month.idxmax()
        best_factor = factor_etfs[best_etf]
        stocks = factor_top_stocks[best_factor]

        try:
            current_prices = stock_monthly[stocks].iloc[i]
            prev_prices = stock_monthly[stocks].iloc[i - 1]
            returns = (current_prices / prev_prices) - 1
            avg_return = returns.mean()

            turnover = len(set(stocks).symmetric_difference(last_holdings)) / len(stocks)
            last_holdings = set(stocks)

            if include_costs:
                cost = turnover * cost_multiplier * (slippage_estimate + bid_ask_spread)
                avg_return -= cost

            strategy_returns.append(avg_return)
            best_factors.append(best_factor)
        except:
            continue

    strategy_returns = pd.Series(strategy_returns, index=etf_returns.index[1:len(strategy_returns)+1])
    return strategy_returns, best_factors

# Analysis and visualization
def compute_metrics(strategy_returns, best_factors):
    cumulative_strategy = (1 + strategy_returns).cumprod()
    cumulative_benchmark = (1 + benchmark_returns.loc[cumulative_strategy.index]).cumprod()
    drawdowns = (cumulative_strategy / cumulative_strategy.cummax() - 1)
    total_return = cumulative_strategy.iloc[-1] - 1
    benchmark_return = cumulative_benchmark.iloc[-1] - 1
    cagr = cumulative_strategy.iloc[-1] ** (1 / (len(strategy_returns)/12)) - 1
    volatility = strategy_returns.std() * np.sqrt(12)
    sharpe = (strategy_returns - (0.01/12)).mean() / strategy_returns.std() * np.sqrt(12)
    max_dd = drawdowns.min()

    latest_month = strategy_returns.index[-1].strftime('%B %Y')
    latest_factor = best_factors[-1]
    latest_picks = ", ".join(factor_top_stocks[latest_factor])

    analysis_md = f"""
**Quantitative Analysis:**  
This strategy rotates monthly into the best-performing factor ETF based on prior momentum and allocates equally to its top stocks.

---

**Performance Summary:**  
- Total Return: {total_return:.2%}  
- Benchmark Return (SPY): {benchmark_return:.2%}  
- CAGR: {cagr:.2%}  
- Annual Volatility: {volatility:.2%}  
- Sharpe Ratio: {sharpe:.2f}  
- Max Drawdown: {max_dd:.2%}  

---

**{latest_month} Allocation:**  
- **Factor:** {latest_factor}  
- **Stocks:** {latest_picks}  

---

*Disclaimer:* Past performance does not guarantee future results. Use for educational purposes only.
"""

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cumulative_strategy.index, y=cumulative_strategy * 100,
                             name="Strategy", line=dict(color="#1f77b4", width=3)))
    fig.add_trace(go.Scatter(x=cumulative_benchmark.index, y=cumulative_benchmark * 100,
                             name="SPY", line=dict(color="#2ca02c", width=3)))

    fig.update_layout(
        title="📈 Factor Rotation Strategy vs SPY",
        template="plotly_dark",
        yaxis_title="Cumulative Return (%)",
        height=600,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return fig, analysis_md

# Dash App
app = Dash(__name__)
app.title = "Factor Rotation Engine"

app.layout = html.Div([
    html.H1("📊 Adaptive Factor Rotation Engine", className="title"),
    html.Div([
        dcc.Checklist(
            id="cost-toggle",
            options=[{"label": "Include Transaction Costs", "value": "with_costs"}],
            value=["with_costs"],
            labelStyle={"color": "white", "margin-right": "15px"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    dcc.Graph(id="strategy-graph"),
    html.Div(id="analysis-text", className="analysis-box")
])

@app.callback(
    Output("strategy-graph", "figure"),
    Output("analysis-text", "children"),
    Input("cost-toggle", "value")
)
def update_graph(include_costs):
    use_costs = "with_costs" in include_costs
    strategy, best_factors = run_backtest(use_costs)
    fig, analysis_md = compute_metrics(strategy, best_factors)
    return fig, dcc.Markdown(analysis_md)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)
