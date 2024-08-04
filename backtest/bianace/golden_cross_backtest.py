import pandas as pd
import os

# Function to perform backtest
def run_backtest(file_path, initial_capital, short_window, long_window, trading_fee=0.001):
    # Load data
    data = pd.read_csv(file_path)
    data['Open Time'] = pd.to_datetime(data['Open Time'])
    data = data.sort_values('Open Time').reset_index(drop=True)

    # Calculate moving averages
    data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()

    # Generate trading signals
    data['Signal'] = 0  # Default 0, no position
    data.loc[data['SMA_Short'] > data['SMA_Long'], 'Signal'] = 1  # Buy signal
    data.loc[data['SMA_Short'] < data['SMA_Long'], 'Signal'] = -1 # Sell signal

    # Initialize positions
    data['Position'] = data['Signal'].shift()

    # Initialize variables
    cash = initial_capital
    position = 0
    previous_cash = initial_capital

    # Portfolio value initialization
    data['Portfolio Value'] = float(initial_capital)

    # Trading simulation
    trades = []
    for i in range(1, len(data)):
        if data.loc[i, 'Position'] == 1 and data.loc[i-1, 'Position'] != 1:
            # Buy
            position = cash / data.loc[i, 'Close']
            cash -= cash * trading_fee  # Deduct trading fee
            trades.append({'Action': 'buy', 'Time': data.loc[i, 'Open Time'], 'Price': data.loc[i, 'Close'], 'Capital': cash, 'Profit': None, 'Rate of Return (%)': None})
            cash = 0
        elif data.loc[i, 'Position'] == -1 and data.loc[i-1, 'Position'] != -1:
            # Sell
            cash = position * data.loc[i, 'Close']
            cash -= cash * trading_fee  # Deduct trading fee
            profit = cash - previous_cash
            rate_of_return = (profit / previous_cash * 100) if previous_cash != 0 else 0
            trades.append({'Action': 'sell', 'Time': data.loc[i, 'Open Time'], 'Price': data.loc[i, 'Close'], 'Capital': cash, 'Profit': profit, 'Rate of Return (%)': rate_of_return})
            previous_cash = cash
            position = 0
        # Update portfolio value
        data.loc[i, 'Portfolio Value'] = cash + position * data.loc[i, 'Close']

    # Save trades to CSV
    trades_df = pd.DataFrame(trades)
    output_file_path = os.path.join(output_dir, f'{short_window}_{long_window}.csv')
    trades_df.to_csv(output_file_path, index=False)

    # Calculate performance metrics
    total_return = (data['Portfolio Value'].iloc[-1] - initial_capital) / initial_capital * 100
    trades_count = len(trades_df)
    win_trades = ((trades_df['Action'] == 'sell') & (trades_df['Profit'] > 0)).sum()
    win_rate = win_trades / (trades_count / 2) * 100 if trades_count != 0 else 0
    max_drawdown = ((data['Portfolio Value'].cummax() - data['Portfolio Value']) / data['Portfolio Value'].cummax()).max() * 100

    # Return the results
    return {
        'Window': f'{short_window}, {long_window}',
        'Total Trades': trades_count / 2,
        'Total Return (%)': total_return,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown
    }

# Define initial settings
file_path = 'data/binance/daily_candles_BTCUSDT.csv'
initial_capital = 10000

# Define output directory for results
output_dir = 'results/binance/trades/golden_cross'
os.makedirs(output_dir, exist_ok=True)

# Run backtests for different window combinations
results = []
window_combinations = [(5, 20), (10, 20), (5, 40), (10, 40)]
for short_window, long_window in window_combinations:
    results.append(run_backtest(file_path, initial_capital, short_window, long_window))

# Display results
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# Save the performance summary to CSV
performance_summary_path = os.path.join(output_dir, 'performance_summary.csv')
results_df.to_csv(performance_summary_path, index=False)
