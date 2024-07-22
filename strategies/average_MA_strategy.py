"""
strategies/average_MA_strategy.py

5일, 20일, 60일, 120일 이동평균선을 각각 구한다.
가격이 해당 이동평균선 위에 있으면 이동평균선당 0.2점, 아래에 있으면 0점을 부여한다.
다섯 개 이동평균선의 점수를 더한 후 이 비율에 따라 투자 비중을 결정한다.
(예: 0.6점의 경우 투자 비중은 60%)

1. 5일선 돌파 : 0.2
2. 5일선 & 20일선 돌파 : 0.4
3. 5일선 & 20일선 & 60일선 돌파 : 0.6
4. 5일선 & 20일선 & 60일선 돌파 & 120일선 돌파 : 0.8
5. 5일선 & 20일선 & 60일선 돌파 & 120일선 & 200일선 돌파 : 1
"""

import asyncio
import numpy as np
import sys
import os


# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from utils.api_helpers import fetch_latest_data_with_retry


def calculate_moving_averages(df, windows):
    df = df.sort_index()  # 오래된 데이터가 위로 오게 정렬
    for period in windows:
        df[f'MA_{period}'] = df['close'].rolling(window=period, min_periods=1).mean()
    return df

def calculate_score(df, windows):
    # 각 이동평균에 대한 비교 점수 계산
    for ma in windows:
        df[f'score_MA_{ma}'] = (df['close'] > df[f'MA_{ma}']).astype(float) * 0.2

    # 총 점수 계산
    df['total_score'] = df[['score_MA_5', 'score_MA_20', 'score_MA_60', 'score_MA_120', 'score_MA_200']].sum(axis=1)
    return df

def generate_signals(df):
    df['signal'] = np.where(df['total_score'] > 0, 1, 0)
    df['positions'] = df['signal'].diff()
    return df


async def check_signals(market, windows, investment_amount):
    df = await fetch_latest_data_with_retry(market, windows[-1] + 1)
    df = calculate_moving_averages(df, windows)
    df = calculate_score(df, windows)
    print(df)
    df = generate_signals(df)

    latest_data = df.iloc[-1]
    latest_positions = latest_data['positions']
    latest_price = latest_data["close"]
    latest_signal = latest_data['signal']
    latest_score = latest_data['total_score']

    investment = latest_score * investment_amount

    if latest_positions == 1:
        message = f"{market}: Buy signal at {latest_price}, investment: {investment}"
    elif latest_positions == -1:
        message = f"{market}: Sell signal at {latest_price}"
    elif latest_positions == 0 and latest_signal == 1:
        message = f"{market}: Hold or Add buy signal at {latest_price}, investment: {investment}"
    else:
        message = f"{market}: No signal at {latest_price}"
    return message



async def average_MA_strategy(markets=["KRW-BTC"], windows = [5, 20, 60, 120, 200], investment_amount = 10000):
    tasks = [check_signals(market, windows, investment_amount) for market in markets]
    signals = await asyncio.gather(*tasks)

    # 모든 신호를 모아서 한꺼번에 출력하고 텔레그램으로 발송
    title = f"\n[ Average MA Strtegy ]\n"
    all_signals_message = title + "\n".join(signals)
    # print(all_signals_message)
    # send_telegram_message(all_signals_message)

    return all_signals_message


if __name__ == "__main__":
    result = asyncio.run(average_MA_strategy())
    # print(result)