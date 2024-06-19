import time
import numpy as np
from api.upbit_api import get_daily_candles
from dotenv import load_dotenv
from utils import save_market_backtest_result, save_backtest_results, calculate_cumulative_return, calculate_mdd, calculate_win_rate

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


def run_backtest(market, count, initial_capital, window=5, investment_fraction=0.5):
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
    save_market_backtest_result(market, df, count, "daily_average")

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


def run_daily_average_backtest(markets, count=200, initial_capital=10000):
    results = []

    print("\n{ Daily Average Backtest }",)

    for market in markets:
        print(f"Daily average backtest for {market}...")
        result = run_backtest(market, count, initial_capital, window=5, investment_fraction=1)
        results.append(result)
        time.sleep(2)  # 각 API 호출 사이에 2초 지연

    result_df = save_backtest_results(results, count, "daily_average")

    print(result_df)


if __name__ == "__main__":
    run_daily_average_backtest()
