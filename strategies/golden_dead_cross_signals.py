import asyncio
import numpy as np

from utils import fetch_latest_data_with_retry
# , send_telegram_message


def calculate_moving_averages(df, short_window=5, long_window=20):
    df = df.sort_index()
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    return df


def generate_signals(df, short_window):
    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(
        df.loc[df.index[short_window:], 'short_mavg'] > df.loc[df.index[short_window:], 'long_mavg'],
        1, 0
    )
    df['positions'] = df['signal'].diff()
    return df


async def check_signals(market, count=40, short_window=5, long_window=20):
    df = await fetch_latest_data_with_retry(market, count)
    df = calculate_moving_averages(df, short_window, long_window)
    df = generate_signals(df, short_window)

    latest_signal = df['positions'].iloc[-1]
    latest_price = df['close'].iloc[-1]
    latest_date = df.index[-1].strftime('%Y-%m-%d')

    if latest_signal == 1:
        message = f"{market}: Buy signal at {latest_price} on {latest_date}"
    elif latest_signal == -1:
        message = f"{market}: Sell signal at {latest_price} on {latest_date}"
    else:
        message = f"{market}: No signal at {latest_price} on {latest_date}"

    return message


async def golden_dead_cross_signals(markets):
    while True:
        tasks = [check_signals(market, count=40, short_window=5, long_window=20) for market in markets]
        signals = await asyncio.gather(*tasks)

        # 모든 신호를 모아서 한꺼번에 출력하고 텔레그램으로 발송
        title = "\n[ Golden Cross Signals ]\n"
        all_signals_message = title + "\n".join(signals)
        # print(all_signals_message)
        # send_telegram_message(all_signals_message)

        return all_signals_message

        # await asyncio.sleep(3600)  # 1시간 간격으로 실행


if __name__ == "__main__":
    asyncio.run(golden_dead_cross_signals())
