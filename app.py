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
import logging
from functools import lru_cache
from html import escape

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
    idx = df.resample('ME').first().index
    # Ensure tz-naive
    if hasattr(idx, 'tz') and idx.tz is not None:
        idx = idx.tz_localize(None)
    return idx

def get_fallback_data():
    import pandas as pd
    import numpy as np
    from datetime import datetime
    # Generate monthly dates for the last 10 years
    end = pd.Timestamp(datetime.today().replace(day=1)) + pd.offsets.MonthEnd(0)
    start = end - pd.DateOffset(years=10) + pd.offsets.MonthEnd(0)
    dates = pd.date_range(start, end, freq='M')
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "SPY"]
    # No fixed seed: fallback data changes on every reload for demo realism
    data = {}
    for ticker in tickers:
        # Start price between 50 and 500
        price = np.random.uniform(50, 500)
        n = len(dates)
        # Simulate market cycles: combine trend, cycles, and noise
        t = np.arange(n)
        # Market cycle: 5-year and 2-year sine waves
        cycle = 0.04 * np.sin(2 * np.pi * t / 60) + 0.02 * np.sin(2 * np.pi * t / 24)
        # Random crisis: 1-2 per decade, sharp drawdown and recovery
        crisis = np.zeros(n)
        for _ in range(np.random.randint(1, 3)):
            c_start = np.random.randint(0, n-12)
            c_depth = np.random.uniform(-0.25, -0.15)  # 15-25% drop
            c_length = np.random.randint(3, 8)  # 3-8 months
            crisis[c_start:c_start+c_length] += np.linspace(0, c_depth, c_length)
            # Recovery
            if c_start + c_length < n:
                rec_length = np.random.randint(6, 18)
                crisis[c_start+c_length:c_start+c_length+rec_length] += np.linspace(-c_depth, 0, rec_length)
        # SPY: lower mean, lower volatility
        if ticker == "SPY":
            drift = 0.006
            vol = 0.035
        else:
            drift = 0.013  # higher mean for stocks
            vol = 0.09     # higher volatility
        # Monthly returns: drift + cycles + crisis + noise
        rets = drift + cycle + crisis + np.random.normal(0, vol, n)
        prices = [price]
        for r in rets:
            prices.append(prices[-1] * np.exp(r))
        data[ticker] = prices[1:]
    df = pd.DataFrame(data, index=dates)
    # Ensure index is tz-naive
    if hasattr(df.index, 'tz') and df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df

# Caching yahooquery data fetch
@lru_cache(maxsize=8)
def fetch_data_cached(tickers, start, end):
    from yahooquery import Ticker
    import pandas as pd
    data = pd.DataFrame()
    missing_tickers = []
    used_fallback = False
    for ticker in tickers:
        try:
            t = Ticker(ticker)
            # Yahooquery returns a multi-index DataFrame for history
            hist = t.history(start=start, end=end)
            if hist.empty:
                missing_tickers.append(ticker)
                continue
            # If multi-index, get the 'adjclose' column
            if isinstance(hist.index, pd.MultiIndex):
                # Some tickers may have multiple levels, get the right one
                if 'adjclose' in hist.columns:
                    tdata = hist['adjclose'].reset_index(level=0, drop=True)
                    tdata.name = ticker
                    data = pd.concat([data, tdata], axis=1)
                else:
                    missing_tickers.append(ticker)
            else:
                if 'adjclose' in hist.columns:
                    tdata = hist['adjclose']
                    tdata.name = ticker
                    data = pd.concat([data, tdata], axis=1)
                else:
                    missing_tickers.append(ticker)
        except Exception:
            missing_tickers.append(ticker)
    # Fill missing data
    data = data.ffill().bfill()
    # If all data is missing, use fallback
    if data.empty or data.isnull().all().all():
        data = get_fallback_data()
        used_fallback = True
        missing_tickers = [t for t in tickers if t not in data.columns]
    # Ensure index is tz-naive
    if hasattr(data.index, 'tz') and data.index.tz is not None:
        data.index = data.index.tz_localize(None)
    return data, missing_tickers, used_fallback

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
    return f"{pct:.2f}%"

# Helper for Yahoo Finance style growth display
def format_growth_yahoo(start: float, end: float, label: str) -> str:
    pct = ((end / start) - 1) * 100
    pct_str = f"{pct:.2f}%"
    up = pct >= 0
    arrow = "▲" if up else "▼"
    color = "#26a69a" if up else "#e45756"
    return (
        f"<span style='font-size:1.25em;font-weight:700;color:{color};margin-right:0.7em;'>"
        f"{arrow} {escape(pct_str)}"
        f"</span>"
        f"<span style='font-size:1.1em;font-weight:400;color:#f3f4f6;'>"
        f"{escape(label)}"
        f"</span>"
    )

def format_date(dt: pd.Timestamp) -> str:
    return dt.strftime("%Y/%m/%d")

# Utility to force tz-naive index

def force_tz_naive_index(df):
    # Parse all as UTC, so all are tz-aware and comparable
    idx = pd.to_datetime([str(x) for x in df.index], format='mixed', errors='coerce', utc=True)
    # Convert to tz-naive (local time, drops tz info)
    idx = idx.tz_convert(None)
    # Drop any NaT (unparseable) values and corresponding rows
    mask = ~pd.isna(idx)
    df = df[mask]
    df.index = idx[mask]
    return df

def generate_plot() -> tuple[str, List[str]]:
    warnings = []
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "SPY"]
    start = "2015-01-01"
    end = None
    data, missing_tickers, used_fallback = fetch_data_cached(tuple(tickers), start, end)

    if used_fallback:
        warnings.append("Live data unavailable. Showing fallback sample data.")
    if missing_tickers:
        warnings.append(f"Missing data for: {', '.join(missing_tickers)}")

    # If data is empty or all NaN, forcibly generate fallback data
    if data.empty or data.isnull().all().all():
        data = get_fallback_data()
        warnings.append("All data missing. Forcibly showing fallback sample data.")

    data = force_tz_naive_index(data)
    data = data.sort_index()

    strat_cum = run_strategy(data)
    spy_cum = get_spy_cumulative(data)

    # Only drop rows where both are missing
    df = pd.DataFrame({"Strategy": strat_cum, "SPY": spy_cum})
    before = df.shape[0]
    df = df.dropna(how='all')
    after = df.shape[0]
    if after < before:
        warnings.append(f"Dropped {before-after} rows with all missing values.")

    # If df is empty after all, forcibly generate fallback data and plot again
    if df.empty:
        data = get_fallback_data()
        warnings.append("No data available after processing. Forcibly showing fallback sample data.")
        data = force_tz_naive_index(data)
        data = data.sort_index()
        strat_cum = run_strategy(data)
        spy_cum = get_spy_cumulative(data)
        df = pd.DataFrame({"Strategy": strat_cum, "SPY": spy_cum})
        df = df / df.iloc[0] * 100
    else:
        df = df / df.iloc[0] * 100

    df = force_tz_naive_index(df)
    df = df.sort_index()

    rebalance_dates = get_month_starts(df)
    # Ensure rebalance_dates is tz-naive
    if hasattr(rebalance_dates, 'tz') and rebalance_dates.tz is not None:
        rebalance_dates = rebalance_dates.tz_localize(None)
    rebalance_dates = [d for d in rebalance_dates if d <= df.index[-1]]
    # Ensure all dates in rebalance_dates are tz-naive
    rebalance_dates = [d.tz_localize(None) if hasattr(d, 'tz') and d.tz is not None else d for d in rebalance_dates]
    actual_rebalance_dates = df.index.intersection(rebalance_dates)
    # Ensure actual_rebalance_dates is tz-naive
    if hasattr(actual_rebalance_dates, 'tz') and actual_rebalance_dates.tz is not None:
        actual_rebalance_dates = actual_rebalance_dates.tz_localize(None)
    df.index = pd.to_datetime([str(x) for x in df.index]).tz_localize(None)
    df = df.sort_index()

    # Minimal, cold, elite line colors
    strat_color = '#3a4a5a'  # deep blue-gray
    spy_color = '#6bb7c7'    # muted icy teal
    grid_color = '#2a2d34'
    # Calculate percent growth for plotting and summary
    strat_pct = 100 * (df['Strategy'] / df['Strategy'].iloc[0] - 1)
    spy_pct = 100 * (df['SPY'] / df['SPY'].iloc[0] - 1)
    # Use the last value for summary
    strat_growth = f"{strat_pct.iloc[-1]:.2f}%"
    spy_growth = f"{spy_pct.iloc[-1]:.2f}%"
    # Define start_date and end_date for the date range
    start_date = format_date(df.index[0])
    end_date = format_date(df.index[-1])
    # Minimalist, institutional subtitle and growth stats
    date_range = f"{start_date} – {end_date}"
    growth_stats = f"Strategy Growth: {strat_growth}   |   SPY Growth: {spy_growth}"
    subtitle_html = (
        f"<div style='text-align:left;padding-left:2px;margin-bottom:0.2em;'>"
        f"<span style='font-size:1.05em;font-weight:400;color:#b0b3b8;font-family:IBM Plex Sans,Inter,Segoe UI,Roboto,Arial,sans-serif;letter-spacing:0.5px;'>{date_range}</span><br>"
        f"<span style='font-size:1.18em;font-weight:500;color:#d3d7de;font-family:IBM Plex Sans,Inter,Segoe UI,Roboto,Arial,sans-serif;letter-spacing:0.2px;'>{growth_stats}</span>"
        f"</div>"
    )
    # Main lines
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=strat_pct, mode='lines', name='Strategy',
        line=dict(width=4, color=strat_color),
        hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br><b>Strategy</b>: %{y:.2f}%<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=spy_pct, mode='lines', name='SPY',
        line=dict(width=4, color=spy_color, dash='dot'),
        hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br><b>SPY</b>: %{y:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        title=None,
        xaxis_title="Date",
        yaxis_title="Growth (%)",
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="left",
            x=0.0,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=14, color="#b0b3b8", family="IBM Plex Sans,Inter,Segoe UI,Roboto,Arial,sans-serif")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="IBM Plex Sans,Inter,Segoe UI,Roboto,Arial,sans-serif", color="#e3e6eb", size=17),
        xaxis=dict(showgrid=True, gridcolor=grid_color, tickfont=dict(size=15), zeroline=False, showline=True, linecolor="#444", mirror=True),
        yaxis=dict(
            showgrid=True, gridcolor=grid_color, tickfont=dict(size=15), zeroline=False, showline=True, linecolor="#444", mirror=True,
            tickformat=".2f"
        ),
        margin=dict(l=30, r=30, t=30, b=30),
        width=1100,
        height=480,
    )
    plot_html = pio.to_html(fig, full_html=False)
    plot_div = f'<div class="dashboard-container" style="padding-top:0.5em;padding-left:0.5em;">{subtitle_html}{plot_html}</div>'
    PLOT_CACHE.write_text(plot_div)
    return plot_div, warnings

def parallel_backtests(prices: pd.DataFrame, strategies: List) -> List[pd.Series]:
    with Pool() as pool:
        results = pool.map(lambda strat: strat(prices), strategies)
    return results

@app.route("/")
def index():
    try:
        result = generate_plot()
        if isinstance(result, tuple):
            plot_div, warnings = result
        else:
            plot_div, warnings = result, []
        return render_template("index.html", plot_div=plot_div, warnings=warnings)
    except Exception as e:
        logging.exception("Error in index route")
        return render_template("index.html", error=str(e), warnings=[])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
# For even more speed, you can implement bottlenecks in Cython or pybind11 (C++), or Rust via PyO3.
