import asyncio
import numpy as np

from utils import fetch_latest_data_with_retry
# send_telegram_message


def calculate_moving_average(df, window=5):
    df = df.sort_index()  # 오래된 데이터가 위로 오게 정렬
    df['moving_avg'] = df['close'].rolling(window=window, min_periods=1).mean()
    return df


def generate_signals(df):
    df['signal'] = 0
    df['signal'] = np.where(df['close'] > df['moving_avg'], 1, 0)
    df['positions'] = df['signal'].diff()
    return df


async def check_signals(market, count, window=5):
    df = await fetch_latest_data_with_retry(market, count)
    df = calculate_moving_average(df, window)
    df = generate_signals(df)

    latest_positions = df['positions'].iloc[-1]
    latest_price = df['close'].iloc[-1]
    latest_signal = df['signal'].iloc[-1]

    if latest_positions == 1:
        message = f"{market}: Buy signal at {latest_price}"
    elif latest_positions == -1:
        message = f"{market}: Sell signal at {latest_price}"
    elif latest_positions == 0 and latest_signal == 1:
        message = f"{market}: Hold signal at {latest_price}"
    else:
        message = f"{market}: No signal at {latest_price}"

    return message


async def daily_average_signals(markets):
    while True:
        tasks = [check_signals(market, count=10, window=5) for market in markets]
        signals = await asyncio.gather(*tasks)

        # 모든 신호를 모아서 한꺼번에 출력하고 텔레그램으로 발송
        title = "\n[ Daily Average Signals ]\n"
        all_signals_message = title + "\n".join(signals)
        # print(all_signals_message)
        # send_telegram_message(all_signals_message)

        return all_signals_message

        # await asyncio.sleep(3600)  # 1시간 간격으로 실행
