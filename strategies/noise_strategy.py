import numpy as np
import asyncio
from utils import fetch_latest_data_with_retry
import time


async def calculate_noise(df, window=30):
    """
    각 종목의 30일 평균 노이즈 값을 계산하는 함수.

    :param df: 데이터프레임 (OHLCV)
    :param window: 평균을 계산할 기간 (기본값 30일)
    :return: 데이터프레임에 30일 평균 노이즈 값 추가
    """
    # 오래된 데이터부터 정렬
    df = df.sort_index()

    # 노이즈 계산
    df['noise'] = 1 - abs(df['open'] - df['close']) / (df['high'] - df['low'])

    # 무한대 값과 NaN 값 처리
    df['noise'] = df['noise'].replace([np.inf, -np.inf], np.nan).fillna(0)

    # 30일 평균 노이즈 값 계산
    df[f'noise_avg_{window}'] = df['noise'].rolling(window=window, min_periods=30).mean()
    return df


async def get_lowest_noise_stocks(markets, count=30, top_n=5):
    """
    투자 직전의 30일 평균 노이즈 값이 가장 작은 종목 n개를 선정하는 함수.

    :param markets: 종목 리스트
    :param count: 가져올 데이터의 수
    :param top_n: 선정할 종목의 수 (기본값 5)
    :return: 노이즈 값이 가장 작은 종목 n개의 리스트
    """
    noise_values = []

    for market in markets:
        df = await fetch_latest_data_with_retry(market, count)
        df = await calculate_noise(df)
        latest_noise_avg = df[f'noise_avg_{count}'].iloc[-1]
        if (latest_noise_avg <= 0.55) :
            noise_values.append((market, latest_noise_avg))
        time.sleep(1)

    # 노이즈 값 기준으로 정렬하여 가장 작은 n개 종목 선정
    noise_values.sort(key=lambda x: x[1])
    selected_stocks = noise_values[:top_n]

    return selected_stocks


async def noise_strategy(markets):

    top_n = 7  # 노이즈 값이 가장 작은 종목 7개 선정

    selected_stocks = await get_lowest_noise_stocks(markets, count=30, top_n=top_n)

    title = "\n[ Noise Strategy ]"
    # 선정된 종목 출력
    result_message = f"Top {top_n} stocks with the lowest noise values:\n"
    for stock, noise in selected_stocks:
        result_message += f"{stock}: {noise:.6f}\n"

    all_signals_message = title + "\n" + result_message

    # print(result_message)

    # 결과를 텍스트 파일로 저장
    # output_file = 'results/noise_strategy_result.txt'
    # with open(output_file, 'a') as f:
    #     f.write(result_message + "\n")

    return all_signals_message


if __name__ == "__main__":
    asyncio.run(noise_strategy())
