# For production, use Gunicorn: web: gunicorn --bind 0.0.0.0:$PORT app:app
from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime, timedelta
import time
import os
from typing import List, Optional
import joblib
from multiprocessing import Pool
from pathlib import Path

app = Flask(__name__)

# Top 8 tech stocks + SPY
TICKERS: List[str] = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'SPY'
]

START_DATE: str = (datetime.today() - timedelta(days=365*10)).strftime('%Y-%m-%d')
END_DATE: str = datetime.today().strftime('%Y-%m-%d')
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
PRICES_CACHE = CACHE_DIR / "prices.joblib"
PLOT_CACHE = CACHE_DIR / "plot.html"

# Helper to get monthly rebalancing dates
def get_month_starts(df: pd.DataFrame) -> pd.DatetimeIndex:
    return df.resample('ME').first().index  # Use 'ME' instead of 'M'

def fetch_prices(force_refresh: bool = False) -> pd.DataFrame:
    if PRICES_CACHE.exists() and not force_refresh:
        return joblib.load(PRICES_CACHE)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            data = yf.download(
                TICKERS,
                start=START_DATE,
                end=END_DATE,
                progress=False,
                auto_adjust=True
            )
            break
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                raise e
    if isinstance(data.columns, pd.MultiIndex):
        if 'Adj Close' in data.columns.get_level_values(0):
            adj_close = data.xs('Adj Close', axis=1, level=0)
        else:
            adj_close = data.xs('Close', axis=1, level=0)
        adj_close = adj_close[[t for t in TICKERS if t in adj_close.columns]]
    else:
        if 'Adj Close' in data.columns:
            adj_close = data['Adj Close'].to_frame()
        else:
            adj_close = data['Close'].to_frame()
    adj_close = adj_close.dropna(how='all')
    joblib.dump(adj_close, PRICES_CACHE)
    return adj_close

def calculate_momentum(prices: pd.DataFrame) -> pd.DataFrame:
    returns_3m = prices.pct_change(63)
    returns_6m = prices.pct_change(126)
    returns_12m = prices.pct_change(252)
    momentum = returns_3m + returns_6m + returns_12m
    return momentum

def run_strategy(prices: pd.DataFrame) -> pd.Series:
    stock_tickers = [t for t in TICKERS if t != 'SPY' and t in prices.columns]
    momentum = calculate_momentum(prices[stock_tickers])
    month_starts = get_month_starts(prices)
    portfolio = pd.Series(index=prices.index, dtype=float)
    current_holdings: List[str] = []
    for i in range(1, len(month_starts)):
        date = month_starts[i]
        prev_date = month_starts[i-1]
        if date in momentum.index:
            top3 = momentum.loc[date].sort_values(ascending=False).head(3).index.tolist()
            current_holdings = top3
        if current_holdings:
            period_returns = prices[current_holdings].loc[prev_date:date].pct_change().mean(axis=1)
            portfolio.loc[prev_date:date] = period_returns
    portfolio = portfolio.fillna(0)
    cumulative = (1 + portfolio).cumprod()
    return cumulative

def get_spy_cumulative(prices: pd.DataFrame) -> pd.Series:
    if 'SPY' not in prices.columns:
        return pd.Series(index=prices.index, data=np.nan)
    spy = prices['SPY'].pct_change().fillna(0)
    return (1 + spy).cumprod()

def format_growth(start: float, end: float) -> str:
    pct = ((end / start) - 1) * 100
    return f"{pct:.1f}%"

def format_date(dt: pd.Timestamp) -> str:
    return dt.strftime("%Y/%m/%d")

def generate_plot(force_refresh: bool = False) -> str:
    if PLOT_CACHE.exists() and not force_refresh:
        return PLOT_CACHE.read_text()
    prices = fetch_prices()
    strat_cum = run_strategy(prices)
    spy_cum = get_spy_cumulative(prices)
    df = pd.DataFrame({"Strategy": strat_cum, "SPY": spy_cum}).dropna()
    # Calculate growth
    strat_growth = format_growth(df['Strategy'].iloc[0], df['Strategy'].iloc[-1])
    spy_growth = format_growth(df['SPY'].iloc[0], df['SPY'].iloc[-1])
    # Format dates
    start_date = format_date(df.index[0])
    end_date = format_date(df.index[-1])
    # Professional, colorblind-friendly colors
    strat_color = '#1f77b4'  # blue
    spy_color = '#ff7f0e'    # orange
    # Main lines
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Strategy'], mode='lines', name='Momentum Strategy',
        line=dict(width=3, color=strat_color)
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df['SPY'], mode='lines', name='SPY',
        line=dict(width=3, color=spy_color, dash='dot')
    ))
    # Add markers for monthly rebalances
    rebalance_dates = get_month_starts(df)
    fig.add_trace(go.Scatter(
        x=rebalance_dates, y=df.loc[rebalance_dates, 'Strategy'],
        mode='markers', name='Rebalance',
        marker=dict(size=7, color='#e45756', symbol='diamond'),
        showlegend=True
    ))
    subtitle = (
        f"<span style='font-size:1.1em;font-weight:400;'>"
        f"Backtest: {start_date} to {end_date} | "
        f"Strategy Growth: <b>{strat_growth}</b> | SPY Growth: <b>{spy_growth}</b>"
        f"</span>"
    )
    fig.update_layout(
        title=dict(
            text=f"Factor Rotation Backtest Engine<br>{subtitle}",
            x=0.5
        ),
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0
        ),
        plot_bgcolor="#18181b",
        paper_bgcolor="#18181b",
        font=dict(family="Inter, Segoe UI, Arial", color="#f3f4f6"),
        xaxis=dict(showgrid=True, gridcolor="#23272f"),
        yaxis=dict(showgrid=True, gridcolor="#23272f"),
        margin=dict(l=40, r=40, t=90, b=40)
    )
    plot_div = f'<div class="dashboard-container">{pio.to_html(fig, full_html=False)}</div>'
    PLOT_CACHE.write_text(plot_div)
    return plot_div

def parallel_backtests(prices: pd.DataFrame, strategies: List) -> List[pd.Series]:
    with Pool() as pool:
        results = pool.map(lambda strat: strat(prices), strategies)
    return results

@app.route("/")
def index():
    plot_div = generate_plot()
    return render_template("index.html", plot_div=plot_div)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
# For even more speed, you can implement bottlenecks in Cython or pybind11 (C++), or Rust via PyO3.
