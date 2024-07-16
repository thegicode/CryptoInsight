import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

import asyncio
import numpy as np
import sys
import os


# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from utils.data_utils import get_recent_candles



def calculate_ma_score(data):
    """이동평균선 점수 계산"""
    score = 0
    price = data['close']
    for ma in [5, 20, 60, 120]:
        if price >= data[f'MA_{ma}']:
            score += 0.2
    return score

def backtest(ticker, start_date, end_date):
    # 데이터 다운로드
    data = get_recent_candles(ticker, count=500)  # 최대 500일 데이터 요청
    # data = data.loc[start_date:end_date]

    # 이동평균선 계산
    for ma in [5, 20, 60, 120]:
        data[f'MA_{ma}'] = data['close'].rolling(window=ma).mean()

    # 최소 120일의 데이터가 필요하므로 처음 120일 제거
    data = data.iloc[120:]

    # 점수 및 투자 비중 계산
    data['Score'] = data.apply(calculate_ma_score, axis=1)
    data['Weight'] = data['Score'] * 100

    # 수익률 계산
    data['Return'] = data['close'].pct_change()
    data['Strategy_Return'] = data['Return'] * data['Weight'].shift(1) / 100

    # 누적 수익률 계산
    data['Cumulative_Return'] = (1 + data['Return']).cumprod()
    data['Cumulative_Strategy_Return'] = (1 + data['Strategy_Return']).cumprod()

    print(data)

    return data

# 백테스트 실행
ticker = "KRW-BTC"  # 업비트의 비트코인 티커
start_date = "2020-01-01"
end_date = "2023-12-31"

result = backtest(ticker, start_date, end_date)

if not result.empty:
    print(f"전략 최종 수익률: {result['Cumulative_Strategy_Return'].iloc[-1]:.2f}")
    print(f"Buy and Hold 수익률: {result['Cumulative_Return'].iloc[-1]:.2f}")

    # 결과 시각화
    plt.figure(figsize=(12,6))
    plt.plot(result.index, result['Cumulative_Return'], label='Buy and Hold')
    plt.plot(result.index, result['Cumulative_Strategy_Return'], label='Strategy')
    plt.title('Backtest Result')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.show()
else:
    print("데이터를 가져오는데 실패했습니다.")