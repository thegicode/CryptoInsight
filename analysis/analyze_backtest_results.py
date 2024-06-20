import pandas as pd
import os

# CSV 파일 경로
daily_average_csv_path = 'results/daily_average_backtest_200.csv'
golden_cross_csv_path = 'results/golden_dead_cross_backtest_200.csv'
volatility_csv_path = 'results/volatility_backtest_200.csv'
volatility_ma_csv_path = 'results/volatility_checkMA_backtest_200.csv'

# CSV 파일 불러오기
daily_average_df = pd.read_csv(daily_average_csv_path)
golden_cross_df = pd.read_csv(golden_cross_csv_path)
volatility_df = pd.read_csv(volatility_csv_path)
volatility_ma_df = pd.read_csv(volatility_ma_csv_path)

# 결과 저장 디렉토리 생성
output_dir = 'results'
os.makedirs(output_dir, exist_ok=True)


# 코인별로 분석하고 결과를 텍스트 파일로 저장하는 함수
def analyze_coin(coin, daily_average_df, golden_cross_df, volatility_df, volatility_ma_df, output_file):
    # 필터링하여 해당 코인의 데이터 가져오기
    daily_average_coin_df = daily_average_df[daily_average_df['Market'] == coin]
    golden_cross_coin_df = golden_cross_df[golden_cross_df['Market'] == coin]
    volatility_coin_df = volatility_df[volatility_df['Market'] == coin]
    volatility_ma_coin_df = volatility_ma_df[volatility_ma_df['Market'] == coin]

    # 결과를 하나의 데이터프레임으로 합치기
    combined_df = pd.DataFrame({
        'Backtest': ['Daily Average', 'Golden Cross', 'Volatility Breakout', 'Volatility Breakout (MA Check)'],
        'Cumulative Return (%)': [
            daily_average_coin_df['Cumulative Return (%)'].values[0] if not daily_average_coin_df.empty else None,
            golden_cross_coin_df['Cumulative Return (%)'].values[0] if not golden_cross_coin_df.empty else None,
            volatility_coin_df['Cumulative Return (%)'].values[0] if not volatility_coin_df.empty else None,
            volatility_ma_coin_df['Cumulative Return (%)'].values[0] if not volatility_ma_coin_df.empty else None
        ],
        'Win Rate (%)': [
            daily_average_coin_df['Win Rate (%)'].values[0] if not daily_average_coin_df.empty else None,
            golden_cross_coin_df['Win Rate (%)'].values[0] if not golden_cross_coin_df.empty else None,
            volatility_coin_df['Win Rate (%)'].values[0] if not volatility_coin_df.empty else None,
            volatility_ma_coin_df['Win Rate (%)'].values[0] if not volatility_ma_coin_df.empty else None
        ],
        'Max Drawdown (MDD) (%)': [
            daily_average_coin_df['Max Drawdown (MDD) (%)'].values[0] if not daily_average_coin_df.empty else None,
            golden_cross_coin_df['Max Drawdown (MDD) (%)'].values[0] if not golden_cross_coin_df.empty else None,
            volatility_coin_df['Max Drawdown (MDD) (%)'].values[0] if not volatility_coin_df.empty else None,
            volatility_ma_coin_df['Max Drawdown (MDD) (%)'].values[0] if not volatility_ma_coin_df.empty else None
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
coins = ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-AVAX', 'KRW-DOGE', 'KRW-BCH', "KRW-SHIB", "KRW-POLYX", "KRW-NEAR", "KRW-DOT", "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]

# 텍스트 파일 경로
output_file = os.path.join(output_dir, 'backtest_analysis.txt')

# 기존 텍스트 파일 삭제 (이미 존재할 경우)
if os.path.exists(output_file):
    os.remove(output_file)

# 각 코인별로 결과 분석 및 텍스트 파일 저장
for coin in coins:
    analyze_coin(coin, daily_average_df, golden_cross_df, volatility_df, volatility_ma_df, output_file)
