# analysis/process_strategies_and_signals.py

import datetime
import sys
import os
import asyncio

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from strategies import golden_dead_cross_signals, daily_average_signals, volatility_strategy, afternoon_strategy
from analyze_backtest import analyze_backtest
from coins import coin_list
from fetchers.fetchers import fetchers

# backtest.py 파일의 경로를 추가하고 backtest 함수를 가져옴
import importlib.util

backtest_path = os.path.join(os.path.dirname(current_dir), "backtest.py")
backtest_spec = importlib.util.spec_from_file_location("backtest", backtest_path)
backtest = importlib.util.module_from_spec(backtest_spec)
backtest_spec.loader.exec_module(backtest)

# 문자열 신호를 파싱하여 딕셔너리로 변환하는 함수
def parse_signals(signal_str):
    lines = signal_str.strip().split('\n')
    signals = {}
    for line in lines[1:]:  # 첫 줄은 제목이므로 제외
        if ':' in line:
            ticker, signal = line.split(':', 1)
            signals[ticker.strip()] = signal.strip()
    return signals

def backup_file(file_path):
    if os.path.exists(file_path):
        # 현재 날짜와 시간을 얻습니다.
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 백업 파일 이름을 생성합니다.
        backup_file_path = f"{file_path}_{current_time}.txt"

        # 기존 파일을 백업 파일로 이동합니다.
        os.rename(file_path, backup_file_path)
        print(f"Existing file backed up to: {backup_file_path}")

async def process_strategies_and_signals():
    # fetchers 실행
    # await fetchers()

    # backtest 실행
    # await backtest.backtest()

    # analyze_backtest 실행
    backtest_results = analyze_backtest()

    # signal
    tasks = [
        asyncio.create_task(golden_dead_cross_signals(coin_list)),
        asyncio.create_task(daily_average_signals(coin_list)),
        asyncio.create_task(volatility_strategy(coin_list)),
        asyncio.create_task(volatility_strategy(coin_list, check_ma=True)),
        asyncio.create_task(volatility_strategy(coin_list, check_ma=True, check_volume=True)),
        asyncio.create_task(afternoon_strategy(coin_list)),
    ]
    signals = await asyncio.gather(*tasks)

    # 각 전략 이름을 신호와 매핑
    signal_map = {
        'Golden Cross': parse_signals(signals[0]),
        'Daily Average': parse_signals(signals[1]),
        'Volatility Breakout': parse_signals(signals[2]),
        '+ (MA Check)': parse_signals(signals[3]),
        '+ (Volume Check)': parse_signals(signals[4]),
        'Afternoon': parse_signals(signals[5]),
    }

    # 결과를 텍스트 파일로 저장
    output_file = 'results/trade/process_strategies_and_signals.txt'

    # 파일 백업
    backup_file(output_file)

    with open(output_file, 'w') as f:
        # 신호를 백테스트 결과에 추가
        for ticker, df in backtest_results.items():
            # print(f"Processing {ticker}...\n")

            signals_for_ticker = []
            for index, row in df.iterrows():
                strategy_name = row['Name']
                strategy_signals = signal_map.get(strategy_name, {})

                # 티커에 대한 신호를 찾음
                ticker_signal = strategy_signals.get(ticker, "No signal")
                signals_for_ticker.append(ticker_signal)

            df['Signal'] = signals_for_ticker
            f.write(f"\n=== {ticker} ===\n")
            f.write(df.to_string(index=False))
            f.write("\n\n")

            print(f"\n=== {ticker} ===\n")
            print(df.to_string(index=False))
            print("\n\n")


    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(process_strategies_and_signals())
