from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from datetime import datetime, timedelta

app = Flask(__name__)

# Top 8 tech stocks + SPY
TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'SPY'
]

START_DATE = (datetime.today() - timedelta(days=365*10)).strftime('%Y-%m-%d')
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Helper to get monthly rebalancing dates
def get_month_starts(df):
    return df.resample('M').first().index

def fetch_prices():
    data = yf.download(TICKERS, start=START_DATE, end=END_DATE, progress=False)
    # Handle both single and multi-index columns
    if isinstance(data.columns, pd.MultiIndex):
        if 'Adj Close' in data.columns.get_level_values(0):
            adj_close = data.xs('Adj Close', axis=1, level=0)
        else:
            # fallback: try 'Close'
            adj_close = data.xs('Close', axis=1, level=0)
    else:
        # Single ticker case
        if 'Adj Close' in data.columns:
            adj_close = data['Adj Close'].to_frame()
        else:
            adj_close = data['Close'].to_frame()
    adj_close = adj_close.dropna(how='all')
    return adj_close

def calculate_momentum(prices):
    # Calculate 3M, 6M, 12M returns
    returns_3m = prices.pct_change(63)  # ~21 trading days/month
    returns_6m = prices.pct_change(126)
    returns_12m = prices.pct_change(252)
    momentum = returns_3m + returns_6m + returns_12m
    return momentum

def run_strategy(prices):
    # Only use stocks, not SPY, for selection
    stock_tickers = [t for t in TICKERS if t != 'SPY']
    momentum = calculate_momentum(prices[stock_tickers])
    month_starts = get_month_starts(prices)
    portfolio = pd.Series(index=prices.index, dtype=float)
    current_holdings = []
    for i in range(1, len(month_starts)):
        date = month_starts[i]
        prev_date = month_starts[i-1]
        # Select top 3 by momentum at rebalance date
        if date in momentum.index:
            top3 = momentum.loc[date].sort_values(ascending=False).head(3).index.tolist()
            current_holdings = top3
        # Equally weight the selected stocks
        if current_holdings:
            period_returns = prices[current_holdings].loc[prev_date:date].pct_change().mean(axis=1)
            portfolio.loc[prev_date:date] = period_returns
    # Fill any missing values with 0 (no return)
    portfolio = portfolio.fillna(0)
    # Calculate cumulative return
    cumulative = (1 + portfolio).cumprod()
    return cumulative

def get_spy_cumulative(prices):
    spy = prices['SPY'].pct_change().fillna(0)
    return (1 + spy).cumprod()

@app.route("/")
def index():
    prices = fetch_prices()
    strat_cum = run_strategy(prices)
    spy_cum = get_spy_cumulative(prices)
    # Align for plotting
    df = pd.DataFrame({"Strategy": strat_cum, "SPY": spy_cum}).dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Strategy'], mode='lines', name='Momentum Strategy'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SPY'], mode='lines', name='SPY'))
    fig.update_layout(title="Momentum Factor Rotation vs SPY (10Y)", xaxis_title="Date", yaxis_title="Cumulative Return", template="plotly_white")
    plot_div = pio.to_html(fig, full_html=False)
    return render_template("index.html", plot_div=plot_div)

if __name__ == "__main__":
    app.run(debug=True)
