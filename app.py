import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from dash import Dash, dcc, html, Input, Output, State
import plotly.graph_objects as go
from dash import ctx
import os

# ------------------- CONFIG -------------------
slippage_estimate = 0.0005
bid_ask_spread = 0.0003
cost_multiplier = 1

APP_TITLE = "📊 Factor Rotation Backtest Engine"
APP_DESCRIPTION = "A smart rotation engine analyzing factor ETF momentum with intuitive visuals."

TOGGLE_COSTS_LABEL = "Include Transaction Costs"
SHOW_ETF_LABEL = "Show Raw ETF Performance"
DOWNLOAD_LABEL = "📥 Download CSV"

GRAPH_TITLE = "📈 Factor Rotation Strategy vs SPY"
ETF_GRAPH_TITLE = "📊 Raw ETF Performance Since 2015"
BENCHMARK_LABEL = "SPY"
STRATEGY_LABEL = "Strategy"
# ----------------------------------------------

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
    benchmark_aligned = benchmark_returns.loc[strategy_returns.index]
    cumulative_benchmark = (1 + benchmark_aligned).cumprod()

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
- Benchmark Return ({BENCHMARK_LABEL}): {benchmark_return:.2%}  
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
    fig.add_trace(go.Scatter(
        x=cumulative_strategy.index,
        y=np.round(cumulative_strategy * 100, 2),
        name=STRATEGY_LABEL,
        line=dict(color="#1f77b4", width=3, shape="spline")
    ))
    fig.add_trace(go.Scatter(
        x=cumulative_benchmark.index,
        y=np.round(cumulative_benchmark * 100, 2),
        name=BENCHMARK_LABEL,
        line=dict(color="#2ca02c", width=2, dash="dot")
    ))

    fig.update_layout(
        title=GRAPH_TITLE,
        template="plotly_dark",
        yaxis_title="Cumulative Return (%)",
        height=600,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font=dict(color="white", family="Helvetica Neue, sans-serif")
    )

    return fig, analysis_md

# Dash App Setup
app = Dash(__name__, assets_folder="assets")
app.title = APP_TITLE

app.layout = html.Div([
    html.H1(APP_TITLE, className="title"),
    html.P(APP_DESCRIPTION, className="description"),

    html.Div([
        dcc.Checklist(
            id="cost-toggle",
            options=[{"label": TOGGLE_COSTS_LABEL, "value": "with_costs"}],
            value=["with_costs"],
            className="checklist"
        ),
        dcc.Checklist(
            id="show-etfs",
            options=[{"label": SHOW_ETF_LABEL, "value": "show"}],
            value=[],
            className="checklist"
        )
    ], className="controls"),

    html.Div([
        html.Button(DOWNLOAD_LABEL, id="download-btn", className="download-btn"),
        dcc.Download(id="download-dataframe-csv")
    ], className="download-section"),

    dcc.Graph(id="strategy-graph"),
    html.Div(id="analysis-text", className="analysis-box")
])

@app.callback(
    Output("strategy-graph", "figure"),
    Output("analysis-text", "children"),
    Output("download-dataframe-csv", "data"),
    Input("cost-toggle", "value"),
    Input("show-etfs", "value"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def update_graph(include_costs, show_etfs, download_clicks):
    use_costs = "with_costs" in include_costs
    strategy, best_factors = run_backtest(use_costs)
    fig, analysis_md = compute_metrics(strategy, best_factors)

    if "show" in show_etfs:
        etf_fig = go.Figure()
        for etf in factor_etfs:
            perf = (1 + etf_returns[etf].dropna()).cumprod()
            etf_fig.add_trace(go.Scatter(x=perf.index, y=np.round(perf * 100, 2), name=etf))
        etf_fig.update_layout(
            title=ETF_GRAPH_TITLE,
            template="plotly_dark",
            yaxis_title="Cumulative Return (%)",
            height=600,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            plot_bgcolor="#111111",
            paper_bgcolor="#111111",
            font=dict(color="white", family="Helvetica Neue, sans-serif")
        )
        if ctx.triggered_id == "download-btn":
            df = pd.DataFrame({"Date": strategy.index, "Strategy Return": strategy.values})
            return etf_fig, dcc.Markdown(analysis_md), dcc.send_data_frame(df.to_csv, "strategy_returns.csv")
        return etf_fig, dcc.Markdown(analysis_md), None

    if ctx.triggered_id == "download-btn":
        df = pd.DataFrame({"Date": strategy.index, "Strategy Return": strategy.values})
        return fig, dcc.Markdown(analysis_md), dcc.send_data_frame(df.to_csv, "strategy_returns.csv")

    return fig, dcc.Markdown(analysis_md), None

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port)
