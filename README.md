# Factor Rotation Backtest Engine

This project implements a dynamic **Factor Rotation Strategy** that evaluates multiple investment factors—**Momentum**, **Volatility**, and **Value**—to select the optimal stocks for monthly rotation. Utilizing historical price data and fundamental metrics, the engine ranks stocks by factor performance, backtests each factor’s returns, and constructs a portfolio that rotates monthly into the best-performing factor’s top stocks.

## Key Features

- **Multi-factor analysis:** Momentum (1-month returns), Volatility (1-month rolling volatility), and Value (inverse P/E ratio)
- **Monthly ranking and rotation:** Automatically selects the top 3 stocks per factor and rotates monthly based on prior factor performance
- **Benchmark comparison:** Compares strategy returns to SPY ETF as a market baseline
- **Performance metrics:** Calculates cumulative return, annualized Sharpe ratio, and maximum drawdown
- **Clear actionable output:** Displays monthly stock picks for the overall best factor and each individual factor
- **Timeless & adaptable:** Dynamically uses current date, enabling ongoing use without manual date updates
- **Open-source & reproducible:** Fully scripted in Python with standard libraries and `yfinance` for data retrieval

## Usage

Run the script in a Jupyter Notebook or Google Colab environment. The output includes:

- Cumulative return chart comparing the factor rotation strategy vs SPY benchmark
- Portfolio performance summary with key risk-adjusted metrics
- Current month’s recommended stocks to buy for each factor and the overall strategy
- Clear monthly instructions on portfolio rebalancing and investment approach

## Disclaimer

This backtest excludes transaction costs, taxes, and slippage, which can materially impact real-world returns. The strategy is for educational and research purposes only and should be validated further before live deployment.
