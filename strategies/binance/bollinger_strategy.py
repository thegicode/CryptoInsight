# 미완성

import ccxt
import pandas as pd
import numpy as np

# 바이낸스에서 데이터 로드
def fetch_data_from_binance(market_name, interval, limit=500):
    """Binance에서 최근 데이터를 가져옵니다."""
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(market_name, timeframe=interval, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df['Close'] = df['Close'].astype(float)
    return df

# Bollinger Bands 계산
def calculate_bollinger_bands(df, window, num_std_dev):
    """볼린저 밴드를 계산하여 데이터프레임에 추가합니다."""
    df['Middle Band'] = df['Close'].rolling(window=window).mean()
    df['Std Dev'] = df['Close'].rolling(window=window).std()
    df['Upper Band'] = df['Middle Band'] + (df['Std Dev'] * num_std_dev)
    df['Lower Band'] = df['Middle Band'] - (df['Std Dev'] * num_std_dev)

# 매매 신호 생성
def generate_signals(df, proximity_threshold=0.95):
    """매수 및 매도 신호를 생성합니다."""
    signals = []
    df['Signal'] = ''  # 신호를 저장할 새로운 열 추가

    for i in range(1, len(df)):
        timestamp = df['Timestamp'][i]

        # 매수 신호: 하단 밴드를 아래에서 위로 돌파
        if df['Close'][i] > df['Lower Band'][i] and df['Close'][i-1] <= df['Lower Band'][i-1]:
            signals.append(('buy', timestamp, df['Close'][i]))
            df.at[i, 'Signal'] = 'Buy'

        # 매도 신호: 상단 밴드에 근접
        elif df['Close'][i] >= df['Upper Band'][i] * proximity_threshold:
            signals.append(('sell', timestamp, df['Close'][i]))
            df.at[i, 'Signal'] = 'Sell'

    return signals

# 신호 메시지 출력
def print_signals(signals):
    """생성된 신호를 메시지로 출력합니다."""
    if not signals:
        print("No signals generated.")
        return

    for action, time, price in signals:
        print(f"{action.capitalize()} signal at {time} with price: {price:.2f}")

# 신호가 있는 과거 거래 데이터 출력
def print_signal_data(df, num_records=5):
    """신호가 있는 과거 거래 데이터를 출력합니다."""
    signal_data = df[df['Signal'] != ''].tail(num_records)
    print("\n최근 신호가 있는 거래 데이터:")
    print(signal_data[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Signal']])

# 현재 신호 출력
def print_current_signal(df):
    """현재 시점의 신호를 출력합니다."""
    latest = df.iloc[-1]
    signal = latest['Signal']
    if signal:
        print(f"\n현재 신호: {signal} signal at {latest['Timestamp']} with price: {latest['Close']:.2f}")
    else:
        print("\n현재 신호: No current signal.")

# 신호 생성 실행
def run_signal_generation(market_name, interval, window, num_std_dev, proximity_threshold=0.95):
    """볼린저 밴드 기반 신호를 생성합니다."""
    # Fetch data from Binance
    df = fetch_data_from_binance(market_name, interval)

    # Calculate Bollinger Bands
    calculate_bollinger_bands(df, window, num_std_dev)

    # Generate signals
    signals = generate_signals(df, proximity_threshold)

    # Print recent signals
    print_signals(signals)

    # Print past 5 trading data with signals
    print_signal_data(df)

    # Print current signal
    print_current_signal(df)

if __name__ == "__main__":
    # Example usage
    run_signal_generation(market_name='SOL/USDT', interval='4h', window=20, num_std_dev=2, proximity_threshold=0.95)
