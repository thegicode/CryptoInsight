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

옵션 - 상승장 적용
    - 각 화폐의 가격이 5일 이동 평균보다 높은지 여부 파악
          - 낮을 경우 투자 대상에서 제외
 """


def calculate_range(df):
    """
    변동성 돌파 전략의 range를 계산하는 함수
    :param df: 데이터프레임 (OHLCV)
    :return: 데이터프레임에 range 컬럼 추가
    """
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    return df


def calculate_moving_average(df, window=5):
    """
    이동 평균을 계산하는 함수
    :param df: 데이터프레임 (OHLCV)
    :param window: 이동 평균 윈도우 크기 (기본값 5)
    :return: 이동 평균이 추가된 데이터프레임
    """
    df[f'mavg_{window}'] = df['close'].rolling(window=window, min_periods=1).mean()
    return df


def generate_signals(df, k=0.5, check_ma=False, ma_window=5):
    """
    변동성 돌파 전략을 사용하여 매수 신호를 생성하는 함수
    :param df: 데이터프레임 (OHLCV)
    :param k: 변동성 비율 (기본값 0.5)
    :param check_ma: 이동 평균값 확인 여부 (기본값 False)
    :param ma_window: 이동 평균 윈도우 크기 (기본값 5)
    :return: 매수 신호가 추가된 데이터프레임
    """
    if (check_ma) :
        df = calculate_moving_average(df, window=ma_window)
        df['target'] = df['open'] + df['range'] * k
        # 현재 가격이 이동 평균보다 낮은 경우 매수 신호 제거
        df['signal'] = np.where((df['close'] >= df['target']) & (df['close'] > df[f'mavg_{ma_window}']), 1, 0)
    else :
        df['target'] = df['open'] + df['range'] * k
        df['signal'] = np.where(df['close'] >= df['target'], 1, 0)

    df['positions'] = df['signal'].diff()
    return df


async def check_signals(market, count=40, k=0.5, check_ma=False):
    """
    변동성 돌파 전략을 적용하여 매수 신호를 확인하는 함수
    :param market: 가상화폐 시장 코드
    :param count: 가져올 데이터의 수
    :param k: 변동성 비율 (기본값 0.5)
    :param check_ma: 이동 평균값 확인 여부 (기본값 False)
    :return: 매수 신호 메시지
    """
    df = await fetch_latest_data_with_retry(market, count)

    # 오래된 데이터부터 정렬
    df = df.sort_index()

    df = calculate_range(df)
    df = generate_signals(df, k, check_ma)

    latest_signal = df['positions'].iloc[-1]
    latest_price = df['close'].iloc[-1]

    if latest_signal == 1:
        message = f"{market}: Buy signal at {latest_price}"
    elif latest_signal == -1:
        message = f"{market}: Sell signal at {latest_price}"
    else:
        message = f"{market}: No signal at {latest_price}"

    return message


async def volatility_strategy(markets, check_ma=False):
    k = 0.5

    while True:
        tasks = [check_signals(market, count=10, k=k, check_ma=check_ma) for market in markets]
        signals = await asyncio.gather(*tasks)

        # 모든 신호를 모아서 한꺼번에 출력하고 텔레그램으로 발송
        title = "\n[ Volatility Breakout Signals"
        if check_ma:
            title += " with Moving Average Check"
        title += " ]\n"

        all_signals_message = title + "\n".join(signals)
        print(all_signals_message)
        # send_telegram_message(all_signals_message)

        return all_signals_message

        # await asyncio.sleep(3600)  # 1시간 간격으로 실행


if __name__ == "__main__":
    asyncio.run(volatility_strategy())
