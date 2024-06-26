import requests
import pandas as pd
import numpy as np
import datetime

# 업비트 API를 통해 캔들 데이터를 수집하는 함수
def get_candle_data(market, interval, count):
    url = f"https://api.upbit.com/v1/candles/{interval}"
    querystring = {"market":market,"count":count}
    response = requests.get(url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
    df.set_index('candle_date_time_kst', inplace=True)
    df = df.sort_index()
    return df

# 불린저 밴드를 계산하는 함수
def calculate_bollinger_bands(df, window=20, std_dev=2):
    df['middle_band'] = df['trade_price'].rolling(window).mean()
    df['std_dev'] = df['trade_price'].rolling(window).std()
    df['upper_band'] = df['middle_band'] + (df['std_dev'] * std_dev)
    df['lower_band'] = df['middle_band'] - (df['std_dev'] * std_dev)
    return df

# 백테스트를 수행하는 함수
def backtest_bollinger_bands(df, initial_cash):
    cash = initial_cash
    holdings = 0
    for i in range(1, len(df)):
        if df['trade_price'][i] < df['lower_band'][i] and cash > df['trade_price'][i]:
            # 하단 밴드 이하에서 매수
            holdings += cash / df['trade_price'][i]
            cash = 0
        elif df['trade_price'][i] > df['upper_band'][i] and holdings > 0:
            # 상단 밴드 이상에서 매도
            cash += holdings * df['trade_price'][i]
            holdings = 0
    # 최종 자산 평가
    final_value = cash + holdings * df['trade_price'][-1]
    return final_value

# 마켓명과 기간, 캔들 기준, 초기 자본 설정
markets = ["KRW-BTC"]
period = 30
interval = "minutes1" # 1분 | 3분 | 5분 | 10분 | 60분 | 120분
initial_cash = 10000

# 백테스트 실행
for market in markets:
    print(f"백테스트 중: {market}")
    df = get_candle_data(market, interval, period * 1440) # 30일 데이터, 1분당 1440개의 캔들
    df = calculate_bollinger_bands(df)
    final_value = backtest_bollinger_bands(df, initial_cash)
    print(f"{market} 최종 자산 가치: {final_value:.2f}원")

