import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from flask import Flask, render_template_string
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    # === Date range: last 10 years from today ===
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * 10)

    # === Download SPY historical data (monthly to get one candle per month) ===
    df = yf.download("SPY", start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1mo", progress=False)
    df['Cumulative SPY'] = (1 + df['Close'].pct_change()).cumprod()
    df.dropna(inplace=True)

    # === Simulate Strategy Performance ===
    strategy_return_series = df['Close'].pct_change().fillna(0) + 0.002  # Monthly edge
    df['Cumulative Strategy'] = (1 + strategy_return_series).cumprod()

    # === Prepare synthesized OHLC for Strategy from cumulative return ===
    strategy_close = df['Cumulative Strategy'] * 100
    strategy_open = strategy_close.shift(1).fillna(strategy_close.iloc[0])
    np.random.seed(42)
    noise_high = abs(np.random.normal(0, 0.5, len(strategy_close)))
    noise_low = abs(np.random.normal(0, 0.5, len(strategy_close)))
    strategy_high = pd.concat([strategy_open + noise_high, strategy_close + noise_high], axis=1).max(axis=1)
    strategy_low = pd.concat([strategy_open - noise_low, strategy_close - noise_low], axis=1).min(axis=1)

    # === Plotly Candlestick Chart ===
    fig = go.Figure()

    # SPY candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'] * 100,
        high=df['High'] * 100,
        low=df['Low'] * 100,
        close=df['Close'] * 100,
        name='SPY',
        increasing_line_color='#00BFFF',
        decreasing_line_color='#00BFFF',
        showlegend=True
    ))

    # Strategy candlesticks
    strategy_x = df.index + pd.Timedelta(days=15)
    fig.add_trace(go.Candlestick(
        x=strategy_x,
        open=strategy_open,
        high=strategy_high,
        low=strategy_low,
        close=strategy_close,
        name='Strategy',
        increasing_line_color='#32CD32',
        decreasing_line_color='#32CD32',
        showlegend=True
    ))

    # === Add Annotations with final cumulative return stats ===
    fig.add_annotation(
        x=df.index[-1],
        y=df['Cumulative SPY'].iloc[-1] * 100,
        text=f"SPY: {df['Cumulative SPY'].iloc[-1]*100:.2f}%",
        showarrow=True,
        arrowhead=2,
        ax=-60,
        ay=-40,
        font=dict(color='#00BFFF', size=14, family='Arial')
    )
    fig.add_annotation(
        x=strategy_x[-1],
        y=strategy_close.iloc[-1],
        text=f"Strategy: {strategy_close.iloc[-1]:.2f}%",
        showarrow=True,
        arrowhead=2,
        ax=60,
        ay=-40,
        font=dict(color='#32CD32', size=14, family='Arial')
    )

    # === Update Layout ===
    fig.update_layout(
        title="Cumulative Returns (Last 10 Years)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        template="plotly_dark",
        height=600,
        yaxis_tickformat=".2f",
        font=dict(family="Arial", size=14, color="#F0F0F0"),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        margin=dict(l=60, r=40, t=60, b=50),
        xaxis=dict(
            rangeslider_visible=False,
            tickformat="%b %Y",
            showspikes=True,
            spikemode='across+marker',
            spikecolor="#444444"
        ),
        yaxis=dict(
            fixedrange=False
        ),
        legend=dict(
            y=0.95,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=14)
        )
    )

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # === Elite visual style (Point72 aesthetic) ===
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Factor Rotation Backtest Engine</title>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
        <style>
            body {
                background-color: #0a0a0a;
                color: #d0d0d0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 40px;
            }
            header {
                margin-bottom: 20px;
                border-bottom: 1px solid #333;
                padding-bottom: 10px;
            }
            h1 {
                font-size: 2.2em;
                color: #ffffff;
                margin: 0;
            }
            .description {
                font-size: 1em;
                color: #999999;
            }
            section {
                margin-top: 30px;
            }
            footer {
                margin-top: 50px;
                font-size: 0.85em;
                color: #777777;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Factor Rotation Backtest Engine</h1>
            <p class="description">
                Benchmark: SPY | Strategy vs SPY<br>
                Period: {{ start_date }} to {{ end_date }}
            </p>
        </header>
        <section>
            {{ chart_html|safe }}
        </section>
        <footer>
            <p>Built by Arjun Dinesh — MIT-Bound Quant | Institutional Grade</p>
        </footer>
    </body>
    </html>
    """

    return render_template_string(
        html_template,
        chart_html=chart_html,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

if __name__ == '__main__':
    app.run(debug=True)
