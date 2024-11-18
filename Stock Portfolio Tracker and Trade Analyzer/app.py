from flask import Flask, render_template
import yfinance as yf
import pandas as pd
from stock_portfolio_tracker.portfolio import Portfolio, PortfolioPerformance
from stock_portfolio_tracker.trade_analyzer import moving_average_crossover, TradeSimulator
from stock_portfolio_tracker.data_collection import fetch_real_time_data, fetch_historical_data

app = Flask(__name__)

# List of stock symbols to track
symbols = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'GOOGL', 'NFLX', 'NVDA', 'META', 'SPY', 'BABA']

# Sample portfolio
initial_stocks = {'AAPL': 10, 'TSLA': 5, 'AMZN': 3, 'MSFT': 7}

@app.route('/')
def index():
    # Fetch real-time data
    real_time_data = fetch_real_time_data(symbols)
    
    # Fetch historical data (last 3 months)
    historical_data = fetch_historical_data(symbols)

    # Create portfolio object
    portfolio = Portfolio(initial_stocks)
    portfolio_value = portfolio.get_current_value(real_time_data)

    # Performance tracking
    performance = PortfolioPerformance(portfolio, historical_data)
    start_value, end_value, percent_change = performance.calculate_performance()

    # Generate trade signals (Moving Average Crossover)
    buy_sell_signals = {}
    for symbol, data in historical_data.items():
        signals = moving_average_crossover(data)
        buy_sell_signals[symbol] = signals

    # Simulate trades
    simulator = TradeSimulator()
    for symbol, signals in buy_sell_signals.items():
        for action, date, price in signals:
            simulator.execute_trade(action, symbol, 1, price)

    final_value = simulator.capital + simulator.get_portfolio_value(real_time_data)

    # Render the results in the webpage
    return render_template(
        'index.html',
        portfolio_value=portfolio_value,
        start_value=start_value,
        end_value=end_value,
        percent_change=percent_change,
        final_value=final_value,
        buy_sell_signals=buy_sell_signals,
        trade_history=simulator.trade_history,
        real_time_data=real_time_data
    )

if __name__ == '__main__':
    app.run(debug=True)
