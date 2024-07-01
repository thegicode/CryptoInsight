"""
strategies/afternoon_strategy.py
투자전략:
    - 오전 0시에 가상화폐의 전일 오후(12시 ~ 24시) 수익률과 거래량 체크
    - 매수: 전일 오후 수익률 > 0, 전일 오후 거래량 > 오전 거래량
    - 자금 관리: 가상화폐별 투입 금액은 (타깃 변동성 / 특정 화폐의 전일 오후 변동성) / 투자대상 화폐수
    - 매도: 정오
"""

import sys
import os
import datetime
import pytz
import asyncio
from requests.exceptions import HTTPError

# 현재 파일의 위치를 기준으로 상위 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from api.upbit_api import get_minute_candles

def calculate_candle_return_rate(candles):
    """ 전일 수익률 계산 """
    open_price = candles.iloc[0]['open']
    close_price = candles.iloc[-1]['close']
    return (close_price - open_price) / open_price


def check_signal(morning_data, afternoon_data):
    """ 매수 신호 체크 """
    afternoon_return = calculate_candle_return_rate(afternoon_data)
    morning_volume = morning_data['volume'].sum()
    afternoon_volume = afternoon_data['volume'].sum()

    return 1 if afternoon_return > 0 and afternoon_volume > morning_volume else 0


def check_sell_signal():
    """ 매도 신호 체크 - 매일 정오에 매도 """
    now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    if now.hour == 12 and now.minute == 0:
        return True
    return False

async def fetch_data(ticker):
    """ 전날 0시부터 24시까지 데이터를 가져옵니다 """
    while True:
        try:
            now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
            end = now.replace(hour=0, minute=0, second=0, microsecond=0)

            df = get_minute_candles(ticker, 60, 24, end.isoformat())
            df = df.sort_index()  # 인덱스를 기준으로 오래된 시간 순으로 정렬

            morning_data = df.iloc[:12] # 0시 ~ 11시
            afternoon_data = df.iloc[12:] # 12시 ~ 23시

            return morning_data, afternoon_data
        except HTTPError as http_err:
            if http_err.response.status_code == 429:
                print(f"HTTPError: {http_err}. Too many requests, sleeping for 10 seconds.")
                await asyncio.sleep(10)
            else:
                raise

async def afternoon_strategy(tickers):
    """ 거래 실행 """
    results = []
    for ticker in tickers:
        # 데이터 가져오기
        morning_data, afternoon_data = await fetch_data(ticker)

        # 신호 체크
        signal =  check_signal(morning_data, afternoon_data)
        message = "Buy signal" if signal == 1 else "Sell signal, 정오에 매도"
        results.append(f"{ticker} : {message}")

        # 요청 간에 지연 시간을 추가하여 API 속도 제한을 피함
        await asyncio.sleep(1.5)  # 1.5초 지연

    title = "\n[ Afternoon Strategy ]\n"
    all_message = title + "\n".join(results)
    return all_message

if __name__ == "__main__":
    asyncio.run(afternoon_strategy())
