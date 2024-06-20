import numpy as np
import asyncio
from utils import fetch_latest_data_with_retry
# , send_telegram_message

""" 변동성 돌파 전략

1. range 계산
    원하는 가상화폐의 전일 고가 - 전일 저가
    하루 안에 가상화폐가 움직인 최대폭
2. 매수 기준
    시가 기준으로 가격이 'range * k' 이상 상승하면 해당 가격에 매수
    k는 0.5 ~ 1 (0.5 추천)
3. 매도 기준
    그 날 종가에 판다.
    이 전략으로 매수 신호 확인하는 코드
 """


def calculate_range(df):
    """
    변동성 돌파 전략의 range를 계산하는 함수
    :param df: 데이터프레임 (OHLCV)
    :return: 데이터프레임에 range 컬럼 추가
    """
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    return df


def generate_signals(df, k=0.5):
    """
    변동성 돌파 전략을 사용하여 매수 신호를 생성하는 함수
    :param df: 데이터프레임 (OHLCV)
    :param k: 변동성 비율 (기본값 0.5)
    :return: 매수 신호가 추가된 데이터프레임
    """
    df['target'] = df['open'] + df['range'] * k
    df['signal'] = np.where(df['close'] >= df['target'], 1, 0)
    df['positions'] = df['signal'].diff()
    return df


async def check_signals(market, count=40, k=0.5):
    """
    변동성 돌파 전략을 적용하여 매수 신호를 확인하는 함수
    :param market: 가상화폐 시장 코드
    :param count: 가져올 데이터의 수
    :param k: 변동성 비율 (기본값 0.5)
    :return: 매수 신호 메시지
    """
    df = await fetch_latest_data_with_retry(market, count)

    # 오래된 데이터부터 정렬
    df = df.sort_index()

    df = calculate_range(df)
    df = generate_signals(df, k)

    latest_signal = df['positions'].iloc[-1]
    latest_price = df['close'].iloc[-1]

    if latest_signal == 1:
        message = f"{market}: Buy signal at {latest_price}"
    else:
        message = f"{market}: No buy signal at {latest_price}"

    return message


async def volatility_strategy():
    markets = ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-AVAX', 'KRW-DOGE', 'KRW-BCH',
               "KRW-SHIB", "KRW-POLYX", "KRW-NEAR", "KRW-DOT",
               "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]
    k = 0.5

    while True:
        tasks = [check_signals(market, count=10, k=k) for market in markets]
        signals = await asyncio.gather(*tasks)

        # 모든 신호를 모아서 한꺼번에 출력하고 텔레그램으로 발송
        title = "\n[ Volatility Breakout Signals ]\n"
        all_signals_message = title + "\n".join(signals)
        print(all_signals_message)
        # send_telegram_message(all_signals_message)

        await asyncio.sleep(3600)  # 1시간 간격으로 실행


if __name__ == "__main__":
    asyncio.run(volatility_strategy())
