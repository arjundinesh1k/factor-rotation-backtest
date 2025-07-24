from flask import Flask, render_template
import pandas as pd
import numpy as np
from utils import run_factor_rotation_backtest

app = Flask(__name__)

@app.route('/')
def index():
    # Run the backtest to get the data
    df = run_factor_rotation_backtest()

    # Calculate overall growth for strategy and SPY
    overall_growth = (df['strategy_cum_returns'].iloc[-1] - 1) * 100
    spy_growth = (df['spy_cum_returns'].iloc[-1] - 1) * 100

    # Outperformance (simple difference in total growth)
    outperformance = overall_growth - spy_growth

    # Calculate daily returns for Sharpe Ratio and Max Drawdown
    strategy_daily_returns = df['strategy_cum_returns'].pct_change().dropna()
    spy_daily_returns = df['spy_cum_returns'].pct_change().dropna()

    # Calculate Sharpe Ratio
    # Assuming a risk-free rate of 0 for simplicity in this simulation
    risk_free_rate = 0.0
    # Annualized Sharpe Ratio = (Annualized Return - Risk-Free Rate) / Annualized Volatility
    # Calculate annualized return
    annualized_strategy_return = (1 + strategy_daily_returns).prod() ** (252 / len(strategy_daily_returns)) - 1
    # Calculate annualized volatility
    annualized_strategy_volatility = strategy_daily_returns.std() * np.sqrt(252)
    
    sharpe_ratio = (annualized_strategy_return - risk_free_rate) / annualized_strategy_volatility
    
    # Calculate Max Drawdown
    # Calculate the running maximum
    running_max = df['strategy_cum_returns'].cummax()
    # Calculate the drawdown
    drawdown = (df['strategy_cum_returns'] / running_max) - 1
    # Find the maximum drawdown
    max_drawdown = drawdown.min() * 100

    # Placeholder for Alpha, Beta, R-Squared, Sortino, Calmar Ratio, Win Rate
    # In a real scenario, these would be calculated based on statistical models.
    # For now, we'll use plausible dummy values.
    alpha = 5.0 # Example: 5% alpha
    beta = 1.1 # Example: Higher beta than market
    r_squared = 0.85 # Example: 85% correlation with market
    sortino_ratio = 1.5 # Example: Good Sortino ratio
    calmar_ratio = 0.8 # Example: Decent Calmar ratio
    win_rate = 62.5 # Example: 62.5% winning days/periods

    # Data Quality (dummy value)
    data_quality = 99.97

    # Convert dates to milliseconds for Highcharts
    # Highcharts expects datetime in milliseconds since epoch
    df['date_ms'] = df.index.map(lambda x: x.timestamp() * 1000)

    # Prepare data for Highcharts
    strategy_chart_data = df[['date_ms', 'strategy_cum_returns']].values.tolist()
    spy_chart_data = df[['date_ms', 'spy_cum_returns']].values.tolist()

    # Mock stock data for Quantitative Factor Analysis
    stocks_data = [
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "score": 9.4, "factor_score": 94.2, "momentum": 18.7, "quality": 8.9, "growth": 31.2},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "score": 8.7, "factor_score": 87.3, "momentum": 14.2, "quality": 9.1, "growth": 22.8},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "score": 8.3, "factor_score": 83.1, "momentum": 11.9, "quality": 8.7, "growth": 19.4},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "score": 8.0, "factor_score": 80.5, "momentum": 10.5, "quality": 8.5, "growth": 17.8},
    ]

    return render_template(
        'index.html',
        overall_growth=overall_growth,
        sharpe_ratio=sharpe_ratio,
        outperformance=outperformance,
        max_drawdown=max_drawdown,
        alpha=alpha,
        beta=beta,
        r_squared=r_squared,
        sortino_ratio=sortino_ratio,
        calmar_ratio=calmar_ratio,
        win_rate=win_rate,
        data_quality=data_quality,
        strategy_data=strategy_chart_data,
        spy_data=spy_chart_data,
        stocks_data=stocks_data
    )

@app.route('/api_reference')
def api_reference():
    return render_template('api_reference.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(debug=True)
