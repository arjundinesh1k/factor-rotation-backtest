from flask import Flask, render_template
import pandas as pd
from datetime import datetime
from utils import run_factor_rotation_backtest, calculate_metrics

app = Flask(__name__)

@app.route('/')
def index():
    # Run backtest and get DataFrame
    df = run_factor_rotation_backtest()
    
    # Prepare chart data
    strategy_data_for_chart = [[date.timestamp() * 1000, (row['strategy_cum_returns'] - 1) * 100] 
                              for date, row in df.iterrows()]
    spy_data_for_chart = [[date.timestamp() * 1000, (row['spy_cum_returns'] - 1) * 100] 
                         for date, row in df.iterrows()]
    
    # Calculate all metrics
    metrics = calculate_metrics(df)
    
    # Fixed stock data for Quantitative Analysis
    stocks_data = [
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "score": 9.2, "factor_score": 91.5, "momentum": 28.3, "quality": 8.7, "growth": 35.1},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "score": 8.8, "factor_score": 89.1, "momentum": 18.9, "quality": 9.1, "growth": 25.7},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "score": 8.5, "factor_score": 87.2, "momentum": 15.2, "quality": 8.5, "growth": 22.4},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "score": 8.0, "factor_score": 82.3, "momentum": 12.5, "quality": 7.9, "growth": 19.8},
        {"symbol": "AAPL", "name": "Apple Inc.", "score": 8.7, "factor_score": 88.0, "momentum": 17.1, "quality": 9.0, "growth": 24.5},
        {"symbol": "TSLA", "name": "Tesla Inc.", "score": 7.5, "factor_score": 78.9, "momentum": 10.0, "quality": 7.2, "growth": 15.0},
        {"symbol": "META", "name": "Meta Platforms Inc.", "score": 8.3, "factor_score": 85.5, "momentum": 20.5, "quality": 8.3, "growth": 28.0},
        {"symbol": "NFLX", "name": "Netflix Inc.", "score": 7.8, "factor_score": 80.1, "momentum": 11.8, "quality": 7.5, "growth": 17.3}
    ]

    # Render template
    return render_template(
        'index.html',
        strategy_data=strategy_data_for_chart,
        spy_data=spy_data_for_chart,
        overall_growth=metrics['overall_growth'],
        sharpe_ratio=metrics['sharpe_ratio'],
        outperformance=metrics['outperformance'],
        max_drawdown=metrics['max_drawdown'],
        alpha=metrics['alpha'],
        beta=metrics['beta'],
        r_squared=metrics['r_squared'],
        sortino_ratio=metrics['sortino_ratio'],
        calmar_ratio=metrics['calmar_ratio'],
        win_rate=metrics['win_rate'],
        stocks_data=stocks_data,
        data_quality=98.75,
        last_updated_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )

@app.route('/api_reference')
def api_reference():
    return render_template('api_reference.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)