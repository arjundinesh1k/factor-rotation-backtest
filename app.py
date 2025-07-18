import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    # === Download historical data for SPY ===
    df = yf.download("SPY", start="2010-01-01", end="2024-01-01", progress=False)
    df['Cumulative Return'] = (1 + df['Adj Close'].pct_change()).cumprod()

    # === Plotly chart ===
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Cumulative Return'],
        mode='lines',
        name='SPY',
        line=dict(color='deepskyblue', width=2)
    ))

    fig.update_layout(
        title="SPY Cumulative Returns (2010–2024)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        template="plotly_dark",
        height=600
    )

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # === HTML Template with external CSS ===
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Factor Rotation Backtest Engine</title>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
    </head>
    <body>
        <header>
            <h1>Factor Rotation Backtest Engine</h1>
            <p class="description">Benchmark: SPY | Backtest Range: 2010–2024</p>
        </header>
        <section>
            {{ chart_html|safe }}
        </section>
        <footer>
            <p>Built by Arjun Dinesh — MIT Bound Quant Research Engine</p>
        </footer>
    </body>
    </html>
    """

    return render_template_string(html_template, chart_html=chart_html)

if __name__ == '__main__':
    app.run(debug=True)
