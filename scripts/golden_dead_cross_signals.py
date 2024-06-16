# golden_dead_cross_signals.py
# python3 scripts/golden_dead_cross_signals.py

import sys
import os

# 현재 스크립트의 디렉토리 경로를 가져와서 프로젝트 루트 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from api.upbit_api import get_daily_candles
from utils.moving_averages import calculate_short_long_moving_averages

def find_cross_signals(df, short_window=50, long_window=200):
    print("Finding cross signals...")
    df['signal'] = 0
    df['signal'][short_window:] = np.where(df['short_mavg'][short_window:] > df['long_mavg'][short_window:], 1, 0)
    df['position'] = df['signal'].diff()
    
    golden_cross = df[df['position'] == 1]
    dead_cross = df[df['position'] == -1]
    
    print("Cross signals found:")
    print(f"Golden Crosses:\n{golden_cross[['close', 'short_mavg', 'long_mavg']]}")
    print(f"Dead Crosses:\n{dead_cross[['close', 'short_mavg', 'long_mavg']]}")
    
    return golden_cross, dead_cross

def plot_candles_and_signals(df, golden_cross, dead_cross, market, short_window, long_window):
    print(f"Plotting data for {market}...")
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='Closing Price', color='blue')
    plt.plot(df.index, df['short_mavg'], label=f'Short-term MA ({short_window} days)', color='orange')
    plt.plot(df.index, df['long_mavg'], label=f'Long-term MA ({long_window} days)', color='green')
    
    plt.scatter(dead_cross.index, df.loc[dead_cross.index]['short_mavg'], label='GoldenCross', marker='^', color='red')
    plt.scatter(golden_cross.index, df.loc[golden_cross.index]['short_mavg'], label='Dead Cross', marker='v', color='green')
    
    plt.title(f'{market} Golden Cross & Dead Cross Signals')
    plt.xlabel('Date')
    plt.ylabel('Price (KRW)')
    plt.legend()
    plt.show()
    print(f"Plotting complete for {market}.")

def analyze_markets(markets, count=200, short_window=50, long_window=200):
    for market in markets:
        print(f"Analyzing {market}...")
        df = get_daily_candles(market, count)
        print(f"Data retrieved for {market}. Calculating moving averages...")
        df = calculate_short_long_moving_averages(df, short_window, long_window)
        print(f"Moving averages calculated for {market}.")
        golden_cross, dead_cross = find_cross_signals(df, short_window, long_window)
        plot_candles_and_signals(df, golden_cross, dead_cross, market, short_window, long_window)
        print(f"Analysis complete for {market}.\n")

# 사용 예시
markets = ["KRW-BTC", "KRW-ETH", "KRW-XRP"]  # 원하는 코인 마켓 코드를 여기에 추가
analyze_markets(markets)
