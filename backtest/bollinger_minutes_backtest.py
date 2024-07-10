# backtest/bollinger_minutes_backtest.py

import pandas as pd
import numpy as np
from datetime import datetime

# 데이터 불러오기
df = pd.read_csv('data/minutes_candles/minutes_candles_KRW-SOL_60.csv')

# 날짜 형식 변환
df['date'] = pd.to_datetime(df['date'])

# 불린저 밴드 계산 함수
def bollinger_bands(data, window=20, num_std=2):
    rolling_mean = data['close'].rolling(window=window).mean()
    rolling_std = data['close'].rolling(window=window).std()

    data['upper_band'] = rolling_mean + (rolling_std * num_std)
    data['lower_band'] = rolling_mean - (rolling_std * num_std)
    data['middle_band'] = rolling_mean

    return data

# 불린저 밴드 적용
df = bollinger_bands(df)

# 백테스트 함수
def backtest_bollinger_bands(data):
    position = 0
    balance = 100000000  # 초기 자본금 (1억원)
    buy_price = 0
    trades = []

    for i in range(len(data)):
        if position == 0 and data['close'].iloc[i] < data['lower_band'].iloc[i]:
            # 매수 신호
            position = balance // data['close'].iloc[i]
            buy_price = data['close'].iloc[i]
            balance -= position * buy_price
            trades.append(('Buy', data['date'].iloc[i], buy_price, position))

        elif position > 0 and data['close'].iloc[i] > data['upper_band'].iloc[i]:
            # 매도 신호
            sell_price = data['close'].iloc[i]
            balance += position * sell_price
            trades.append(('Sell', data['date'].iloc[i], sell_price, position))
            position = 0

    # 마지막에 포지션이 남아있다면 청산
    if position > 0:
        last_price = data['close'].iloc[-1]
        balance += position * last_price
        trades.append(('Sell', data['date'].iloc[-1], last_price, position))

    return balance, trades

# 백테스트 실행
final_balance, trades = backtest_bollinger_bands(df)

# 결과 출력
print(f"최종 잔고: {final_balance:,.0f}원")
print(f"총 거래 횟수: {len(trades)}")

# 일부 거래 내역 출력
print("\n일부 거래 내역:")
for trade in trades[:5]:
    print(f"{trade[0]} at {trade[1]}: Price {trade[2]:,.0f}, Amount {trade[3]:.4f}")