import time
import pandas as pd
import numpy as np
from api.upbit_api import get_daily_candles
from dotenv import load_dotenv
import os
import asyncio
import requests

# .env 파일 로드
load_dotenv()

# 텔레그램 봇 토큰과 채팅 ID 설정
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# HTTP 요청 타임아웃 설정
REQUEST_TIMEOUT = 60  # 초 단위로 설정 (예: 60초)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}. Retrying...")
        time.sleep(5)
        send_telegram_message(message)

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

def get_latest_data(market, count=40):
    df = get_daily_candles(market, count)
    return df

async def check_signals(market, count=40, short_window=5, long_window=20):
    df = get_latest_data(market, count)
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

    print(message)
    send_telegram_message(message)

async def main():
    markets = ['KRW-AVAX', 'KRW-DOT', 'KRW-POLYX']
    
    while True:
        tasks = [check_signals(market, count=40, short_window=5, long_window=20) for market in markets]
        await asyncio.gather(*tasks)
        await asyncio.sleep(3600)  # 1시간 간격으로 실행

if __name__ == "__main__":
    asyncio.run(main())
