"""
backtest/afternoon_backtest.py

투자전략:
    - 오전 0시에 가상화폐의 전일 오후(12시 ~ 24시) 수익률과 거래량 체크
    - 매수: 전일 오후 수익률 > 0, 전일 오후 거래량 > 오전 거래량
    - 자금 관리: 가상화폐별 투입 금액은 (타깃 변동성 / 특정 화폐의 전일 오후 변동성) / 투자대상 화폐수
    - 매도: 정오 -> 일단은 매일 매도가 아닌 신호 확인 후 매도
"""

import sys
import os
import datetime
import pytz
import asyncio
import pandas as pd
from requests.exceptions import HTTPError
from strategies.afternoon_strategy import check_signal
from utils import save_market_backtest_result, save_backtest_results, calculate_cumulative_return, calculate_mdd, calculate_win_rate
from utils.data_utils import get_minute_candles_from_file

# 현재 파일의 위치를 기준으로 상위 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

async def fetch_candles_from_file(ticker, count):
    """ 파일에서 과거 데이터를 가져옵니다 """
    print(f"Fetching for {ticker} from file...")

    now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    end = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - datetime.timedelta(days=count)

    file_path = os.path.join("data", f"minutes_candles_{ticker}_{count}.csv")

    df = get_minute_candles_from_file(ticker, count, start)


    return df

def generate_signal(df):
    daily_results = []
    for i in range(0, len(df), 24):  # 하루 단위로 데이터 처리
        if i + 24 > len(df):
            break
        daily_data = df.iloc[i:i+24]
        morning_data = daily_data.iloc[:12]
        afternoon_data = daily_data.iloc[12:]

        # 날짜
        date = daily_data.index[12]

        # 신호 체크
        signal = check_signal(morning_data, afternoon_data)

        # close price
        close = daily_data.iloc[-1].close

        # 정오 가격
        noon_close = morning_data.iloc[-1].close

        # 결과 저장
        daily_results.append({
            "date": date,
            "signal": signal,
            "close": close,
            "noon_close": noon_close
        })

    # 일별 결과를 데이터프레임으로 변환
    df = pd.DataFrame(daily_results)
    df['positions'] = df['signal'].diff()

    return df

def backtest_strategy(df, initial_capital, investment_fraction):
    cash = initial_capital
    shares = 0
    df['holdings'] = 0.0
    df['cash'] = float(initial_capital)
    df['total'] = float(initial_capital)

    for i in range(1, len(df)):
        if df['positions'].iloc[i] == 1:  # 매수 신호
            investment = cash * investment_fraction
            shares += investment / df['close'].iloc[i]
            cash -= investment
        elif df['positions'].iloc[i] == -1 and i < len(df) - 1:  # 매도 신호
            noon_close = df['noon_close'].iloc[i + 1]
            cash += shares * noon_close
            shares = 0
        elif df['positions'].iloc[i] == -1 and i == len(df) - 1:  # 마지막 매도
            cash += shares * df['close'].iloc[i]
            shares = 0
        df.loc[df.index[i], 'holdings'] = shares * df['close'].iloc[i]
        df.loc[df.index[i], 'cash'] = cash
        df.loc[df.index[i], 'total'] = df.loc[df.index[i], 'holdings'] + df.loc[df.index[i], 'cash']

    df['returns'] = df['total'].pct_change()

    # 소수점 없이 표현
    df['holdings'] = df['holdings'].astype(int)
    df['cash'] = df['cash'].astype(int)
    df['total'] = df['total'].astype(int)

    return df

async def run_backtest(market, count, initial_capital, investment_fraction):
    """
    백테스트를 실행하는 메인 함수

    :param market: 가상화폐 시장 코드
    :param count: 가져올 일봉 데이터의 수
    :param initial_capital: 초기 자본
    :return: 백테스트 결과 딕셔너리
    """
    print(f"Afternoon backtest for {market}...")
    candle_df = await fetch_candles_from_file(market, count)
    df = generate_signal(candle_df)
    df = backtest_strategy(df, initial_capital, investment_fraction)

    # 결과를 파일로 저장
    if count == 200:
        save_market_backtest_result(market, df, count, "afternoon")

    cumulative_return_percent = calculate_cumulative_return(df, initial_capital)
    win_rate = calculate_win_rate(df)
    mdd_percent = calculate_mdd(df)

    result = {
        "Market": market,
        "Count": count,
        "Investment Fraction": investment_fraction,
        "Cumulative Return (%)": cumulative_return_percent,
        "Win Rate (%)": win_rate,
        "Max Drawdown (%)": mdd_percent
    }

    return result

async def run_afternoon_backtest(markets=None, count=200, initial_capital=10000, investment_fraction=1):
    """ 백테스트 실행 """
    if markets is None:
        markets = ["KRW-BTC", "KRW-ETH", "KRW-SOL"]

    print("\n{ Afternoon Backtest }")

    tasks = [run_backtest(market, count, initial_capital, investment_fraction) for market in markets]
    results = await asyncio.gather(*tasks)
    result_df = save_backtest_results(results, count, "afternoon")
    print(result_df)

if __name__ == "__main__":
    asyncio.run(run_afternoon_backtest())
