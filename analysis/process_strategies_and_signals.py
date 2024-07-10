import asyncio
import datetime
import sys
import os
import subprocess
import json
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from strategies import golden_dead_cross_signals, daily_average_signals, volatility_strategy, afternoon_strategy
from analyze_backtest import analyze_backtest
from coins import coin_list
from fetchers.fetchers import fetchers
from utils.telegram import get_chat_ids, send_telegram_image, send_telegram_message

# backtest.py 파일의 경로를 추가하고 backtest 함수를 가져옴
import importlib.util

backtest_path = os.path.join(os.path.dirname(current_dir), "backtest.py")
backtest_spec = importlib.util.spec_from_file_location("backtest", backtest_path)
backtest = importlib.util.module_from_spec(backtest_spec)
backtest_spec.loader.exec_module(backtest)

chat_group_id = get_chat_ids()

# 모든 수치 결과를 소수점 두 자리까지 포맷
pd.options.display.float_format = '{:.2f}'.format

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

def save_dataframe_as_image(df, filename, title):
    fig, ax = plt.subplots(figsize=(12, df.shape[0] * 0.3 + 1))  # 적절한 크기로 조정
    fig.suptitle(title, fontsize=16, x=0.05, ha='left')
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

async def process_strategies_and_signals():
    # fetchers 실행
    await fetchers()

    # backtest 실행
    await backtest.backtest()

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

    messages = ""
    for ticker, df in backtest_results.items():
        signals_for_ticker = []
        for index, row in df.iterrows():
            strategy_name = row['Name']
            strategy_signals = signal_map.get(strategy_name, {})

            # 티커에 대한 신호를 찾음
            ticker_signal = strategy_signals.get(ticker, "No signal")
            signals_for_ticker.append(ticker_signal)

        df['Signal'] = signals_for_ticker

        title = f"=== {ticker} ==="
        df_string = df.to_string(index=False, float_format='{:.2f}'.format)
        last = "\n\n"

        messages += title + "\n" + df_string + last

        # DataFrame을 이미지로 저장
        image_filename = f"results/trade/{ticker}.png"
        save_dataframe_as_image(df, image_filename, title)

        # 이미지를 텔레그램으로 전송
        send_telegram_image(image_filename, chat_group_id)

    print(messages)

    # 메시지 길이가 너무 길면 나누어 전송
    # MAX_MESSAGE_LENGTH = 4096  # 텔레그램 메시지 길이 제한
    # for i in range(0, len(messages), MAX_MESSAGE_LENGTH):
    #     send_telegram_message(messages[i:i+MAX_MESSAGE_LENGTH])

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(process_strategies_and_signals())
