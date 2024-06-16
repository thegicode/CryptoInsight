import os
import pandas as pd
import numpy as np
from api.upbit_api import get_daily_candles
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


def calculate_moving_average(df, window=5):
    """
    이동평균 계산 함수

    :param df: 원본 데이터프레임
    :param window: 이동평균 기간
    :return: 이동평균이 추가된 데이터프레임
    """
    df = df.sort_index()  # 오래된 데이터가 위로 오게 정렬
    df['moving_avg'] = df['close'].rolling(window=window, min_periods=1).mean()
    return df

def generate_signals(df):
    """
    매수 및 매도 신호 생성 함수

    :param df: 이동평균이 추가된 데이터프레임
    :return: 매수 및 매도 신호가 추가된 데이터프레임
    """
    df['signal'] = 0
    df['signal'] = np.where(df['close'] > df['moving_avg'], 1, 0)
    df['positions'] = df['signal'].diff()
    return df

def backtest_strategy(df, initial_capital, investment_fraction=0.2):
    """
    생성된 신호를 기반으로 간단한 백테스트를 수행하는 함수

    :param df: 신호가 추가된 데이터프레임
    :param initial_capital: 초기 자본
    :param investment_fraction: 매수 시 투자 비율
    :return: 백테스트 결과가 추가된 데이터프레임
    """
    cash = initial_capital
    shares = 0
    df['holdings'] = 0.0
    df['cash'] = float(initial_capital)
    df['total'] = float(initial_capital)

    for i in range(1, len(df)):
        if df['positions'].iloc[i] == 1:  # 매수 신호
            investment = cash * investment_fraction
            shares += investment / df['close'].iloc[i]
            cash -= investment
        elif df['positions'].iloc[i] == -1:  # 매도 신호
            cash += shares * df['close'].iloc[i]
            shares = 0
        df.loc[df.index[i], 'holdings'] = shares * df['close'].iloc[i]
        df.loc[df.index[i], 'cash'] = cash
        df.loc[df.index[i], 'total'] = df.loc[df.index[i], 'holdings'] + df.loc[df.index[i], 'cash']

    df['returns'] = df['total'].pct_change()

    return df

def calculate_cumulative_return(df, initial_capital):
    """
    총 누적 수익률을 계산하는 함수

    :param df: 백테스트 결과가 추가된 데이터프레임
    :param initial_capital: 초기 자본
    :return: 총 누적 수익률
    """
    final_value = df['total'].iloc[-1]
    cumulative_return = (final_value / initial_capital) - 1
    cumulative_return_percent = cumulative_return * 100
    return cumulative_return_percent

def calculate_win_rate(df):
    """
    승률을 계산하는 함수

    :param df: 백테스트 결과가 추가된 데이터프레임
    :return: 승률
    """
    df_trades = df[df['positions'] != 0].copy()
    df_trades['trade_returns'] = df_trades['total'].diff()
    sell_trades = df_trades[df_trades['positions'] == -1]
    wins = sell_trades[sell_trades['trade_returns'] > 0].shape[0]
    total_trades = sell_trades.shape[0]
    
    if total_trades == 0:
        win_rate = 0
    else:
        win_rate = wins / total_trades * 100
    return win_rate

def calculate_mdd(df):
    """
    최대 낙폭(MDD)을 계산하는 함수

    :param df: 백테스트 결과가 추가된 데이터프레임
    :return: 최대 낙폭(MDD)
    """
    df['peak'] = df['total'].cummax()
    df['drawdown'] = df['total'] / df['peak'] - 1
    mdd = df['drawdown'].min()
    mdd_percent = mdd * 100
    return mdd_percent

def run_backtest(market, count=200, window=5, initial_capital=10000, investment_fraction=0.5):
    """
    백테스트를 실행하는 메인 함수

    :param market: 가상화폐 시장 코드
    :param count: 가져올 일봉 데이터의 수
    :param window: 이동 평균 기간
    :param initial_capital: 초기 자본
    :param investment_fraction: 매수 시 투자 비율
    :return: 백테스트 결과 딕셔너리
    """
    df = get_daily_candles(market, count)
    df = calculate_moving_average(df, window)
    df = generate_signals(df)
    df = backtest_strategy(df, initial_capital, investment_fraction)

    # 결과를 파일로 저장
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'daily_average_backtest_result_{market}.csv')
    df.to_csv(output_file, index=True)

    cumulative_return_percent = calculate_cumulative_return(df, initial_capital)
    win_rate = calculate_win_rate(df)
    mdd_percent = calculate_mdd(df)
    
    result = {
        "Market": market,
        "Count": count,
        "Investment Fraction": investment_fraction,
        "Cumulative Return (%)": cumulative_return_percent,
        "Win Rate (%)": win_rate,
        "Max Drawdown (MDD) (%)": mdd_percent
    }
    
    return result

def main():
    # markets = [ "KRW-DOT", "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]
    markets = ['KRW-BTC', 'KRW-ETH', 'KRW-AVAX', 'KRW-DOGE', 'KRW-BCH', "KRW-SHIB", "KRW-POLYX", "KRW-NEAR", "KRW-DOT", "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]
    results = []

    for market in markets:
        print(f"daily_average_backtest for {market}...")
        result = run_backtest(market, count=200, window=5, initial_capital=10000, investment_fraction=0.2)
        results.append(result)

    results_df = pd.DataFrame(results)

    # Win Rate 기준으로 정렬
    results_df = results_df.sort_values(by="Win Rate (%)", ascending=False)

    # 결과를 저장할 디렉터리 생성
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'daily_average_backtest_result.csv')

    # CSV 파일로 저장
    results_df.to_csv(output_file, index=False)
    print(f"Backtest results saved to '{output_file}'.")

    # CSV 파일 읽기
    result_df = pd.read_csv(output_file)
    print(result_df)

if __name__ == "__main__":
    main()
