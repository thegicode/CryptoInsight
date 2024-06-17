import numpy as np
from api.upbit_api import get_daily_candles
import asyncio
import requests

from utils import send_telegram_message

def calculate_moving_averages(df, short_window=5, long_window=20):
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    return df

def generate_signals(df, short_window):
    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(
        df.loc[df.index[short_window:], 'short_mavg'] > df.loc[df.index[short_window:], 'long_mavg'], 1, 0)
    df['positions'] = df['signal'].diff()
    return df

async def get_latest_data(market, count=40, delay=2):
    for _ in range(3):  # 최대 3번 재시도
        try:
            df = get_daily_candles(market, count)
            return df
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                print(f"Rate limit exceeded for {market}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                raise e
    raise Exception(f"Failed to retrieve data for {market} after 3 retries.")

async def check_signals(market, count=40, short_window=5, long_window=20):
    df = await get_latest_data(market, count)
    df = calculate_moving_averages(df, short_window, long_window)
    df = generate_signals(df, short_window)
    
    latest_signal = df['positions'].iloc[-1]
    latest_price = df['close'].iloc[-1]

    if latest_signal == 1:
        message = f"{market}: Buy signal at {latest_price}"
    elif latest_signal == -1:
        message = f"{market}: Sell signal at {latest_price}"
    else:
        message = f"{market}: No signal at {latest_price}"

    return message


async def golden_dead_cross_signals():
    markets = ['KRW-AVAX', 'KRW-DOT', 'KRW-POLYX']
    
    while True:
        tasks = [check_signals(market, count=40, short_window=5, long_window=20) for market in markets]
        signals = await asyncio.gather(*tasks)

        # 모든 신호를 모아서 한꺼번에 출력하고 텔레그램으로 발송
        title = "\n[ Golden Cross Signals ]\n"
        all_signals_message = title +  "\n".join(signals)
        print(all_signals_message)
        send_telegram_message(all_signals_message)

        await asyncio.sleep(3600)  # 1시간 간격으로 실행
