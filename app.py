from flask import Flask, render_template
import plotly.graph_objs as go
import plotly.io as pio
from utils import run_factor_rotation_backtest
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    df = run_factor_rotation_backtest()
    df['strategy_pct'] = (df['strategy_cum_returns'] - 1) * 100
    df['spy_pct'] = (df['spy_cum_returns'] - 1) * 100

    latest_row = df.iloc[-1]
    latest_date = f"{df.index[-1].month}/{df.index[-1].year}"
    latest_strategy = f"{latest_row['strategy_pct']:.0f}%"
    latest_spy = f"{latest_row['spy_pct']:.0f}%"

    fig = go.Figure()

    # Strategy shadow glow (thin, electric blue)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['strategy_pct'],
        mode='lines',
        line=dict(
            color='rgba(0,120,215,0.16)',
            width=5,
            shape='spline',
            smoothing=1.3
        ),
        hoverinfo='skip',
        showlegend=False
    ))

    # Strategy main line - electric blue, refined thin line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['strategy_pct'],
        mode='lines',
        name='Factor Strategy',
        line=dict(
            color='rgba(0,102,204,1)',
            width=2.5,
            shape='spline',
            smoothing=1.3
        ),
        hovertemplate='%{x|%b %Y}<br><b>Strategy:</b> %{y:.2f}%<extra></extra>'
    ))

    # SPY shadow glow (thin, teal)
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['spy_pct'],
        mode='lines',
        line=dict(
            color='rgba(64,192,186,0.13)',
            width=4,
            shape='spline',
            smoothing=1.2
        ),
        hoverinfo='skip',
        showlegend=False
    ))

    # SPY main line - cool teal, thin
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['spy_pct'],
        mode='lines',
        name='S&P 500 (SPY)',
        line=dict(
            color='rgba(64,192,186,0.92)',
            width=2.2,
            shape='spline',
            smoothing=1.2
        ),
        hovertemplate='%{x|%b %Y}<br><b>SPY:</b> %{y:.2f}%<extra></extra>'
    ))

    # Layout with deep dark bg, crisp font, accent gridlines, subtle shadows
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(
            family='Segoe UI, Open Sans, Roboto, sans-serif',
            size=15,
            color='#CED6E0'
        ),
        title=dict(
            text='Factor Strategy vs S&P 500: Cumulative Return (%)',
            font=dict(
                family='Segoe UI Semibold, Open Sans, sans-serif',
                size=24,
                color='#D1E8FF'
            ),
            x=0.015,
            xanchor='left',
            yanchor='top'
        ),
        hovermode='x unified',
        hoverdistance=2,
        spikedistance=2,
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor='rgba(100,150,200,0.1)',
            zeroline=False,
            showline=True,
            linecolor='#555555',
            ticks='outside',
            tickcolor='#9ABCD9',
            tickfont=dict(size=13, color='#B3C7E6'),
            showspikes=True,
            spikecolor='rgba(180,200,255,0.25)',
            spikethickness=2,
            spikedash='dot',
            spikemode='across',
            zerolinecolor='#444444'
        ),
        yaxis=dict(
            title='Cumulative Return (%)',
            showgrid=True,
            gridcolor='rgba(100,150,200,0.1)',
            zeroline=False,
            showline=True,
            linecolor='#555555',
            ticks='outside',
            tickcolor='#9ABCD9',
            tickfont=dict(size=13, color='#B3C7E6'),
            showspikes=True,
            spikecolor='rgba(180,200,255,0.25)',
            spikethickness=2,
            spikedash='dot',
            spikemode='across',
            zerolinecolor='#444444'
        ),
        legend=dict(
            bgcolor='rgba(18,18,18,0.96)',
            bordercolor='#2E3A59',
            borderwidth=1,
            font=dict(size=14, color='#A9B9D3'),
            x=0.01,
            y=0.99,
            traceorder='normal',
            orientation='h'
        ),
        margin=dict(l=70, r=40, t=85, b=60),
        height=520,
        autosize=True
    )

    plot_div = pio.to_html(fig, full_html=False)

    project_description = (
    "This Factor Rotation Backtest Engine is a sophisticated institutional-grade quantitative dashboard "
    "designed to rigorously analyze and compare the cumulative returns of a custom multi-factor investment "
    "strategy against the S&P 500 benchmark (SPY). Built for precision and clarity, the platform empowers "
    "quantitative researchers and portfolio managers to visualize strategy performance through a clean, responsive "
    "interface featuring state-of-the-art data visualization techniques. It enables actionable insights into factor-driven "
    "investment decisions by leveraging historical data and smooth trend representation, supported by robust backend analytics. "
    "This tool exemplifies the fusion of quantitative finance rigor with elegant, user-centric design, tailored for professional "
    "use in hedge funds, asset management, and advanced research environments."
)

    return render_template(
        'index.html',
        plot_div=plot_div,
        latest_date=latest_date,
        latest_strategy=latest_strategy,
        latest_spy=latest_spy,
        project_description=project_description
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# Developed by Arjun Dinesh | 2025 | MIT-Bound | Quantitative Research & Portfolio Systems
