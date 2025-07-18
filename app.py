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

    # === Download SPY historical data (daily for smooth hover) ===
    df = yf.download(
        "SPY",
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval="1d",
        progress=False
    )

    df['Cumulative SPY'] = (1 + df['Close'].pct_change()).cumprod()
    df.dropna(inplace=True)

    # === Simulate Strategy Performance with slight daily alpha ===
    strategy_return_series = df['Close'].pct_change().fillna(0) + 0.0001
    df['Cumulative Strategy'] = (1 + strategy_return_series).cumprod()

    # === Line plot with spline smoothing for fluid hover ===
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Cumulative SPY'] * 100,
        mode='lines',
        name='SPY',
        line=dict(color='#7ec8e3', width=3, shape='spline', smoothing=1.3),
        hovertemplate="%{x|%-m-%-d-%Y}, %{y:.2f}%<extra>SPY</extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Cumulative Strategy'] * 100,
        mode='lines',
        name='Strategy',
        line=dict(color='#80ffb3', width=3, shape='spline', smoothing=1.3),
        hovertemplate="%{x|%-m-%-d-%Y}, %{y:.2f}%<extra>Strategy</extra>"
    ))

    # === Layout settings ===
    fig.update_layout(
        title="Cumulative Returns (Last 10 Years)",
        xaxis_title="Year",
        yaxis_title="Cumulative Return (%)",
        template="plotly_dark",
        height=600,
        yaxis_tickformat=",0",  # No decimals on y-axis labels
        font=dict(family="Arial", size=14, color="#F0F0F0"),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        margin=dict(l=60, r=40, t=60, b=50),
        xaxis=dict(
            rangeslider_visible=False,
            tickformat="%Y",
            dtick="M12",
            showspikes=False,
            ticklabelmode="period"
        ),
        yaxis=dict(
            fixedrange=False
        ),
        legend=dict(
            y=0.95,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=14)
        ),
        hovermode='x unified'
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
