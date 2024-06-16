import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from api.upbit_api import get_daily_candles

def calculate_moving_averages(df, short_window, long_window):
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    return df

def generate_signals(df, short_window):
    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(
        df.loc[df.index[short_window:], 'short_mavg'] > df.loc[df.index[short_window:], 'long_mavg'], 1, 0)
    df['positions'] = df['signal'].diff()
    return df

def backtest_strategy(df, initial_capital, investment_fraction=0.2):
    cash = initial_capital
    shares = 0
    df['holdings'] = 0.0
    df['cash'] = float(initial_capital)
    df['total'] = float(initial_capital)

    for i in range(1, len(df)):
        if df['positions'].iloc[i] == 1:
            investment = cash * investment_fraction
            shares += investment / df['close'].iloc[i]
            cash -= investment
        elif df['positions'].iloc[i] == -1:
            cash += shares * df['close'].iloc[i]
            shares = 0
        df.loc[df.index[i], 'holdings'] = shares * df['close'].iloc[i]
        df.loc[df.index[i], 'cash'] = cash
        df.loc[df.index[i], 'total'] = df.loc[df.index[i], 'holdings'] + df.loc[df.index[i], 'cash']

    df['returns'] = df['total'].pct_change()
    return df

def calculate_performance(df, initial_capital):
    cumulative_return_percent = (df['total'].iloc[-1] / initial_capital - 1) * 100
    win_rate = calculate_win_rate(df)
    mdd_percent = calculate_mdd(df)
    return cumulative_return_percent, win_rate, mdd_percent

def calculate_win_rate(df):
    df_trades = df[df['positions'] != 0].copy()
    df_trades['trade_returns'] = df_trades['total'].diff()
    sell_trades = df_trades[df_trades['positions'] == -1]
    wins = sell_trades[sell_trades['trade_returns'] > 0].shape[0]
    total_trades = sell_trades.shape[0]
    if total_trades == 0:
        win_rate = 0
    else:
        win_rate = wins / total_trades * 100
    return win_rate

def calculate_mdd(df):
    df['peak'] = df['total'].cummax()
    df['drawdown'] = df['total'] / df['peak'] - 1
    mdd = df['drawdown'].min()
    mdd_percent = mdd * 100
    return mdd_percent

def run_backtest(market='KRW-BTC', count=100, initial_capital=1000000, investment_fraction=0.2):
    df = get_daily_candles(market, count)
    
    windows = [(5, 20), (10, 20), (10, 50), (20, 50)]
    results = []

    for short_window, long_window in windows:
        df_copy = df.copy()
        df_copy = calculate_moving_averages(df_copy, short_window, long_window)
        df_copy = generate_signals(df_copy, short_window)
        df_copy = backtest_strategy(df_copy, initial_capital, investment_fraction)
        performance = calculate_performance(df_copy, initial_capital)
        results.append((short_window, long_window, *performance))

    for result in results:
        print(f"Short window: {result[0]}, Long window: {result[1]}, "
              f"Cumulative Return: {result[2]:.2f}%, Win Rate: {result[3]:.2f}%, MDD: {result[4]:.2f}%")

if __name__ == "__main__":
    run_backtest()
