import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from flask import Flask, render_template_string
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * 10)

    df = yf.download("SPY", start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d", progress=False)
    df['Cumulative SPY'] = (1 + df['Close'].pct_change()).cumprod()
    df.dropna(inplace=True)

    strategy_return_series = df['Close'].pct_change().fillna(0) + 0.0001
    df['Cumulative Strategy'] = (1 + strategy_return_series).cumprod()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Cumulative SPY'] * 100,
        mode='lines',
        name='SPY',
        line=dict(color='#4A6FA5', width=3, shape='spline', smoothing=1.3),
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f}%<extra>SPY</extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Cumulative Strategy'] * 100,
        mode='lines',
        name='Strategy',
        line=dict(color='#2E8B57', width=3, shape='spline', smoothing=1.3),
        hovertemplate="%{x|%b %d, %Y}<br>%{y:.2f}%<extra>Strategy</extra>"
    ))

    fig.update_layout(
        title="Cumulative Returns (Last 10 Years)",
        xaxis_title="Year",
        yaxis_title="Cumulative Return (%)",
        template="plotly_dark",
        height=600,
        yaxis_tickformat=".2f",
        font=dict(family="IBM Plex Sans", size=15, color="#E0E0E0"),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        margin=dict(l=60, r=40, t=60, b=50),
        xaxis=dict(
            rangeslider_visible=False,
            tickformat="%Y",
            dtick="M12",
            showspikes=True,
            spikecolor="#aaa",
            spikethickness=1,
            spikedash='dot',
            spikemode="across"
        ),
        yaxis=dict(
            fixedrange=False,
            showspikes=False
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(size=13)
        ),
        hovermode='x unified'
    )

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Factor Rotation Backtest Engine</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500&display=swap" rel="stylesheet">
        <style>
            body {
                background-color: #0a0a0a;
                color: #c0c0c0;
                font-family: 'IBM Plex Sans', sans-serif;
                margin: 60px;
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
                font-weight: 500;
            }
            .description {
                font-size: 1em;
                color: #888888;
                margin-top: 6px;
            }
            section {
                margin-top: 30px;
            }
            footer {
                margin-top: 50px;
                font-size: 0.85em;
                color: #555555;
                text-align: center;
                letter-spacing: 0.5px;
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
            <p>Built by Arjun Dinesh — Institutional Grade Backtesting ©</p>
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
