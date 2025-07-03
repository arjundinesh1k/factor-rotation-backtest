# Factor Rotation Backtest Engine

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Google Colab](https://img.shields.io/badge/Open%20in-Colab-blue?logo=googlecolab)](https://colab.research.google.com/github/your-username/your-repo-name/blob/main/your-notebook-name.ipynb)

## Overview

This project implements a quantitative investment strategy that dynamically rotates monthly between multiple equity factors—Momentum, Volatility, and Value—to optimize portfolio performance. Using historical stock data, it calculates factor signals, ranks stocks, constructs factor-specific portfolios, and allocates capital to the best-performing factor each month.

## Features

- Calculates monthly factor signals:  
  - Momentum (1-month return)  
  - Volatility (1-month rolling standard deviation)  
  - Value (inverse Price-to-Earnings ratio, mocked static data)  
- Ranks stocks and selects top holdings per factor  
- Rotates portfolio monthly into the factor with the highest recent return  
- Compares strategy performance against the S&P 500 (SPY) benchmark  
- Computes key performance metrics: Sharpe ratio, maximum drawdown  
- Built with Python, using `yfinance`, `pandas`, `numpy`, and `matplotlib`  
- Runs smoothly in Google Colab for easy reproducibility

## Usage

1. Open the notebook in [Google Colab](https://colab.research.google.com/github/your-username/your-repo-name/blob/main/your-notebook-name.ipynb).  
2. Run all cells sequentially to perform data loading, factor calculation, backtesting, and visualization.  
3. Modify tickers, factors, or parameters in the notebook as needed.  
4. Export or share results as needed.

## Results

The strategy aims to capture shifts in market regimes by dynamically allocating to the most successful factor each month, offering potential for enhanced risk-adjusted returns compared to a static benchmark.

## Author

Arjun Dinesh — Future Quantitative Portfolio Manager | Future MIT Applicant
