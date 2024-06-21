import asyncio
import datetime
import os
from strategies import golden_dead_cross_signals, daily_average_signals, volatility_strategy, noise_strategy


async def main():
    markets = ['KRW-AVAX', 'KRW-BCH', 'KRW-BTC', 'KRW-DOGE', 'KRW-DOT', 'KRW-ETH', 'KRW-NEAR', 'KRW-POLYX', 'KRW-SHIB', 'KRW-SOL', 'KRW-THETA', 'KRW-TFUEL', 'KRW-ZRX']

    # 실행 날짜와 시간을 포함한 파일 이름
    execution_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_file = 'results/strategies_result.txt'

    # 기존 텍스트 파일 삭제 (이미 존재할 경우)
    if os.path.exists(output_file):
        os.remove(output_file)

    with open(output_file, 'w') as f:
        def print_and_save(msg):
            print(msg)
            f.write(msg + "\n")

        # 실행 날짜와 시간을 파일에 기록
        print_and_save(f"Execution Date: {execution_datetime}\n")

        # 각 전략의 결과를 받아오기
        task1 = asyncio.create_task(golden_dead_cross_signals(markets))
        task2 = asyncio.create_task(daily_average_signals(markets))
        task3 = asyncio.create_task(volatility_strategy(markets))
        task3_ma = asyncio.create_task(volatility_strategy(markets, check_ma=True))
        task3_ma_volume = asyncio.create_task(volatility_strategy(markets, check_ma=True, check_volume=True))
        task4 = asyncio.create_task(noise_strategy(markets))

        results = await asyncio.gather(task1, task2, task3, task3_ma, task3_ma_volume, task4)

        # 각 결과를 파일에 기록
        for result in results:
            print_and_save(result)


if __name__ == "__main__":
    asyncio.run(main())
