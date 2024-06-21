import pandas as pd
import os

# CSV 파일 경로
CSV_PATHS = {
    'daily_average': 'results/daily_average_backtest_200.csv',
    'golden_cross': 'results/golden_dead_cross_backtest_200.csv',
    'volatility': 'results/volatility_backtest_200.csv',
    'volatility_ma': 'results/volatility_checkMA_backtest_200.csv',
    'volatility_volume': 'results/volatility_checkMA_checkVolume_backtest_200.csv'
}

# CSV 파일 불러오기
dataframes = {name: pd.read_csv(path) for name, path in CSV_PATHS.items()}

# 결과 저장 디렉토리 생성
output_dir = 'results'
os.makedirs(output_dir, exist_ok=True)


# 코인별로 분석하고 결과를 텍스트 파일로 저장하는 함수
def analyze_coin(coin, dataframes, output_file):
    backtests = ['daily_average', 'golden_cross', 'volatility', 'volatility_ma', 'volatility_volume']
    backtest_names = ['Daily Average', 'Golden Cross', 'Volatility Breakout',
                      '+ (MA Check)', '+ (Volume Check)']

    # 결과를 하나의 데이터프레임으로 합치기
    combined_df = pd.DataFrame({
        'Backtest': backtest_names,
        'Cumulative Return (%)': [
            dataframes[bt][dataframes[bt]['Market'] == coin]['Cumulative Return (%)'].values[0]
            if not dataframes[bt][dataframes[bt]['Market'] == coin].empty else None
            for bt in backtests
        ],
        'Win Rate (%)': [
            dataframes[bt][dataframes[bt]['Market'] == coin]['Win Rate (%)'].values[0]
            if not dataframes[bt][dataframes[bt]['Market'] == coin].empty else None
            for bt in backtests
        ],
        'Max Drawdown (MDD) (%)': [
            dataframes[bt][dataframes[bt]['Market'] == coin]['Max Drawdown (MDD) (%)'].values[0]
            if not dataframes[bt][dataframes[bt]['Market'] == coin].empty else None
            for bt in backtests
        ]
    })

    # 결과를 텍스트 파일로 저장
    with open(output_file, 'a') as f:
        f.write(f"=== {coin} ===\n")
        f.write(combined_df.to_string(index=False))
        f.write("\n\n")

    # 결과 출력
    print(f"=== {coin} ===")
    print(combined_df)
    print("\n")


# 분석할 코인 리스트
coins = ['KRW-AVAX', 'KRW-BCH', 'KRW-BTC', 'KRW-DOGE', 'KRW-DOT', 'KRW-ETH', 'KRW-NEAR', 'KRW-POLYX', 'KRW-SHIB', 'KRW-SOL', 'KRW-THETA', 'KRW-TFUEL', 'KRW-ZRX']

# 텍스트 파일 경로
output_file = os.path.join(output_dir, 'analysis_backtest.txt')

# 기존 텍스트 파일 삭제 (이미 존재할 경우)
if os.path.exists(output_file):
    os.remove(output_file)

# 각 코인별로 결과 분석 및 텍스트 파일 저장
for coin in coins:
    analyze_coin(coin, dataframes, output_file)
