# Factor Rotation Backtest Dashboard

A Flask-based web dashboard for backtesting a momentum-based factor rotation strategy on top US tech stocks, using yfinance for data and Plotly for interactive visualization.

## Strategy Overview

- **Universe:** Top 8 US tech stocks (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, AMD) plus SPY (S&P 500 ETF).
- **Momentum Signal:** For each stock, sum the past 3-month, 6-month, and 12-month returns (3M + 6M + 12M).
- **Rebalancing:** Every month, select the top 3 stocks by momentum signal and allocate equal weights.
- **Benchmark:** SPY (S&P 500 ETF).
- **Backtest Period:** Last 10 years (by default).
- **Visualization:** Cumulative return of the strategy vs. SPY, plotted with Plotly.

## Features

- Fetches historical price data automatically with yfinance
- Runs a monthly-rotating, momentum-based portfolio
- Interactive, professional dashboard with Plotly and custom CSS
- Easy to deploy (e.g., Render, Heroku)

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd factor-rotation-backtest
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask app**

   ```bash
   python app.py
   ```

4. **View the dashboard**

   Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## How It Works

- The app downloads 10 years of daily price data for the selected tickers.
- At the start of each month, it calculates the sum of 3M, 6M, and 12M returns for each stock.
- The top 3 stocks by this momentum signal are selected and held equally for the next month.
- The strategy's cumulative return is compared to simply holding SPY over the same period.
- The dashboard visualizes both curves for easy comparison.

## Deployment

A `Procfile` is included for easy deployment to platforms like Render or Heroku:

```
web: python app.py
```

## License

MIT
