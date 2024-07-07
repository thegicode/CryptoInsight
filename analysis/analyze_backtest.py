# analysis/analyze_backtest.py

import json
import os
import sys
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from coins import coin_list

# CSV 파일 경로
CSV_PATHS = {
    'daily_average': 'results/backtest/daily_average_backtest_200.csv',
    'golden_cross': 'results/backtest/golden_dead_cross_backtest_200.csv',
    'volatility': 'results/backtest/volatility_backtest_200.csv',
    'volatility_ma': 'results/backtest/volatility_checkMA_backtest_200.csv',
    'volatility_volume': 'results/backtest/volatility_checkMA_checkVolume_backtest_200.csv',
    'afternoon': 'results/backtest/afternoon_backtest_200.csv'
}

# CSV 파일 불러오기
dataframes = {name: pd.read_csv(path) for name, path in CSV_PATHS.items()}

# 결과 저장 디렉토리 생성
output_dir = 'results/analysis'
os.makedirs(output_dir, exist_ok=True)


# 코인별로 분석하고 결과를 텍스트 파일로 저장하는 함수
def analyze_coin(ticker, dataframes):
    backtests = ['daily_average', 'golden_cross', 'volatility', 'volatility_ma', 'volatility_volume', 'afternoon']
    backtest_names = ['Daily Average', 'Golden Cross', 'Volatility Breakout',
                      '+ (MA Check)', '+ (Volume Check)', 'Afternoon']

    # 결과를 하나의 데이터프레임으로 합치기
    df = pd.DataFrame({
        'Name': backtest_names,
        'Cumulative Return (%)': [
            dataframes[bt][dataframes[bt]['Market'] == ticker]['Cumulative Return (%)'].values[0]
            if not dataframes[bt][dataframes[bt]['Market'] == ticker].empty else None
            for bt in backtests
        ],
        'Win Rate (%)': [
            dataframes[bt][dataframes[bt]['Market'] == ticker]['Win Rate (%)'].values[0]
            if not dataframes[bt][dataframes[bt]['Market'] == ticker].empty else None
            for bt in backtests
        ],
        'Max Drawdown (%)': [
            dataframes[bt][dataframes[bt]['Market'] == ticker]['Max Drawdown (%)'].values[0]
            if not dataframes[bt][dataframes[bt]['Market'] == ticker].empty else None
            for bt in backtests
        ]
    })

    return df


def print_and_save_result(ticker, df, output_file):
    # 결과를 텍스트 파일로 저장
    with open(output_file, 'a') as f:
        f.write(f"=== {ticker} ===\n")
        f.write(df.to_string(index=False))
        f.write("\n\n")

    # 결과 출력
    print(f"=== {ticker} ===")
    print(df)
    print("\n")

def backup_file(output_file):
    if os.path.exists(output_file):
        current_datetime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # 현재 날짜를 가져와 형식에 맞게 변환
        backup_file = os.path.join(output_dir, f'analysis_backtest_{current_datetime}.txt')
        os.rename(output_file, backup_file)
        print(f"기존 파일을 {backup_file}로 백업했습니다.")


def analyze_backtest():
    # 텍스트 파일 경로에 날짜 추가
    output_file = os.path.join(output_dir, 'analysis_backtest.txt')

    # 기존 파일이 있을 경우 백업 (이 경우는 거의 없겠지만, 안전을 위해 유지)
    backup_file(output_file)

    # 각 코인별로 결과 분석 및 텍스트 파일 저장
    results = {}
    for ticker in coin_list:
        df = analyze_coin(ticker, dataframes)
        print_and_save_result(ticker, df, output_file)
        results[ticker] = df

    return results


if __name__ == "__main__":
    analyze_backtest()