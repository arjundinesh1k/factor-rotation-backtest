# Factor Rotation Backtest Engine

## Overview

This project builds a quantitative strategy that **rotates monthly between three core stock factors** — Momentum (growth), Volatility (stability), and Value (price) — to dynamically select the top 3 stocks for investment. The model uses historical price data to rank stocks per factor and allocates capital monthly to the factor with the best recent performance.

## Key Features

- Calculates monthly factor signals: momentum, volatility, and value  
- Ranks stocks within each factor and selects top 3 holdings monthly  
- Rotates portfolio monthly to the best-performing factor  
- Compares strategy performance to the S&P 500 benchmark  
- Computes essential performance metrics: Sharpe ratio, maximum drawdown  
- Runs fully in Python on Google Colab with `yfinance` data  
- Outputs detailed, easy-to-understand performance summaries and visualizations  

## Usage Notes

- The notebook is saved as `.ipynb` for full interactivity, preserving code, plots, and markdown explanations  
- Updates to the notebook **do not automatically sync** with GitHub. You must manually save or upload updated versions via Google Colab’s “Save a copy in GitHub” feature or by uploading directly  
- You can delete files in your GitHub repository anytime through the GitHub web interface or using git commands to maintain a clean repo  

---

Feel free to reach out if you want help adding badges, usage instructions, or contributing guidelines!
