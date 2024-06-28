import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, timedelta

# 가상화폐의 N분 캔들 데이터를 불러오는 함수
def fetch_minute_candles(market, interval, to=None, count=200):
    url = f'https://api.upbit.com/v1/candles/minutes/{interval}?market={market}&count={count}'
    if to:
        url += f"&to={to}"
    try:
        response = requests.get(url)
        data = response.json()
        if not data or 'error' in data:
            print(f"No data or error for URL: {url}")
            return pd.DataFrame()  # 빈 데이터프레임 반환
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['candle_date_time_utc'])
        df.set_index('timestamp', inplace=True)
        df = df[['opening_price', 'high_price', 'low_price', 'trade_price']]
        df.columns = ['open', 'high', 'low', 'close']
        print(f"Fetched {len(df)} rows from {df.index.min()} to {df.index.max()}")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# 특정 기간 동안의 데이터를 수집하는 함수
def fetch_data_for_days(market, days, interval):
    all_data = []
    to = None
    candles_per_day = 1440 // interval  # 분봉이 하루에 몇 개 있는지 계산
    total_requests = (days * candles_per_day) // 200 + 1
    total_candles_needed = days * candles_per_day

    while total_candles_needed > 0:
        df = fetch_minute_candles(market, interval, to=to)
        if df.empty:
            print("Empty dataframe received")
            break  # 데이터가 없으면 중단
        all_data.append(df)
        total_candles_needed -= len(df)
        to = (df.index.min() - timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%SZ')

    print("Number of dataframes in all_data: ", len(all_data))
    for i, dataframe in enumerate(all_data):  # 추가된 디버깅 출력
        print(f"DataFrame {i}: {dataframe.shape} rows, index range {dataframe.index.min()} to {dataframe.index.max()}")

    if all_data:
        try:
            all_data = pd.concat(all_data).sort_index()
        except ValueError as e:  # 추가된 오류 확인
            print(f"Error concatenating data: {e}")
            raise e
        if (all_data.index[-1] - all_data.index[0]).days < days:
            raise ValueError("Not enough data to cover the requested number of days")
    else:
        raise ValueError("No data available for the requested period")

    print("Data collected: ")
    print(all_data.head())
    print(all_data.tail())

    return all_data

# 불린저 밴드 계산 함수
def calculate_bollinger_bands(df, window=20, num_std_dev=2):
    df['SMA'] = df['close'].rolling(window=window).mean()
    df['std_dev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['SMA'] + (num_std_dev * df['std_dev'])
    df['lower_band'] = df['SMA'] - (num_std_dev * df['std_dev'])
    return df

# 불린저 밴드 전략 백테스트 함수
def bollinger_bands_backtest(df, initial_capital=1000000):
    cash = initial_capital
    position = 0.0
    df['signal'] = 0
    df['positions'] = 0.0
    df['holdings'] = 0.0
    df['cash'] = initial_capital
    df['total'] = initial_capital

    for i in range(1, len(df)):
        if df['close'].iloc[i] < df['lower_band'].iloc[i] and position == 0:
            position = cash / df['close'].iloc[i]
            cash = 0
            df.loc[df.index[i], 'signal'] = 1  # 매수 신호
        elif df['close'].iloc[i] > df['upper_band'].iloc[i] and position > 0:
            cash = position * df['close'].iloc[i]
            position = 0
            df.loc[df.index[i], 'signal'] = -1  # 매도 신호

        df.loc[df.index[i], 'positions'] = float(position)
        df.loc[df.index[i], 'holdings'] = position * df['close'].iloc[i]
        df.loc[df.index[i], 'cash'] = cash
        df.loc[df.index[i], 'total'] = cash + position * df['close'].iloc[i]

    return df

def save_results(df, filename='bollinger_bands_backtest_results.csv'):
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=True)
    print(f"Results saved to {output_path}")

def main(market, days, interval, initial_capital=10000):
    try:
        df = fetch_data_for_days(market, days, interval)
    except ValueError as e:
        print(e)
        return

    if df.empty:
        print("No data available for the requested period")
        return

    df = calculate_bollinger_bands(df)
    df = bollinger_bands_backtest(df, initial_capital=initial_capital)

    # save_results(df)
    print(df[['close', 'SMA', 'upper_band', 'lower_band', 'signal', 'positions', 'holdings', 'cash', 'total']])

    # Calculate performance metrics
    cumulative_return_percent = ((df['total'].iloc[-1] - initial_capital) / initial_capital) * 100
    win_rate = (df['signal'].value_counts().get(1, 0) / df['signal'].value_counts().sum()) * 100
    mdd = ((df['total'].cummax() - df['total']) / df['total'].cummax()).max() * 100

    result = {
        "Market": market,
        "Days": days,
        "Interval": interval,
        "Initial Capital": initial_capital,
        "Cumulative Return (%)": cumulative_return_percent,
        "Win Rate (%)": win_rate,
        "Max Drawdown (MDD) (%)": mdd
    }

    print(result)
    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Bollinger Bands Backtest')
    parser.add_argument('--market', type=str, default='KRW-BTC', help='Market symbol to backtest')
    parser.add_argument('--days', type=int, default=30, help='Number of days to backtest')
    parser.add_argument('--interval', type=int, default=5, help='Minute interval for candles')
    parser.add_argument('--initial_capital', type=float, default=10000, help='Initial capital for backtest')
    args = parser.parse_args()

    main(market=args.market, days=args.days, interval=args.interval, initial_capital=args.initial_capital)
