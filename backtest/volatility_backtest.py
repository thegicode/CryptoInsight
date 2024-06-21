import time
import numpy as np
from api.upbit_api import get_daily_candles
from utils import save_market_backtest_result, save_backtest_results, calculate_cumulative_return, calculate_mdd, calculate_win_rate


def calculate_range(df):
    """
    변동성 돌파 전략의 range를 계산하는 함수
    :param df: 데이터프레임 (OHLCV)
    :return: 데이터프레임에 range 컬럼 추가
    """
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    return df


def calculate_moving_average(df, window=5, column='close'):
    """
    이동 평균을 계산하는 함수
    :param df: 데이터프레임 (OHLCV)
    :param window: 이동 평균 윈도우 크기 (기본값 5)
    :param column: 이동 평균을 계산할 컬럼 (기본값 'close')
    :return: 이동 평균이 추가된 데이터프레임
    """
    df[f'mavg_{window}_{column}'] = df[column].rolling(window=window, min_periods=1).mean()
    return df


def generate_signals(df, k=0.5, check_ma=False, check_volume=False, ma_window=5, vol_window=5):
    """
    변동성 돌파 전략을 사용하여 매수 신호를 생성하는 함수
    :param df: 데이터프레임 (OHLCV)
    :param k: 변동성 비율 (기본값 0.5)
    :param check_ma: 이동 평균값 확인 여부 (기본값 False)
    :param check_volume: 거래량 확인 여부 (기본값 False)
    :param ma_window: 이동 평균 윈도우 크기 (기본값 5)
    :param vol_window: 거래량 이동 평균 윈도우 크기 (기본값 5)
    :return: 매수 신호가 추가된 데이터프레임
    """
    if check_ma:
        df = calculate_moving_average(df, window=ma_window)
        df['target'] = df['open'] + df['range'] * k
        df['signal'] = np.where((df['close'] >= df['target']) & (df['close'] > df[f'mavg_{ma_window}_close']), 1, 0)
    else:
        df['target'] = df['open'] + df['range'] * k
        df['signal'] = np.where(df['close'] >= df['target'], 1, 0)

    if check_volume:
        df = calculate_moving_average(df, window=vol_window, column='volume')
        df['signal'] = np.where((df['signal'] == 1) & (df['volume'].shift(1) > df[f'mavg_{vol_window}_volume']), df['signal'], 0)

    df['positions'] = df['signal'].diff()
    return df


def backtest_strategy(df, initial_capital, investment_fraction=0.2):
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


def run_backtest(market, count, initial_capital, k=0.5, investment_fraction=0.2, check_ma=False, check_volume=False, ma_window=5, vol_window=5):
    df = get_daily_candles(market, count)

    # 오래된 데이터부터 정렬
    df = df.sort_index()

    df = calculate_range(df)
    df = generate_signals(df, k, check_ma, check_volume, ma_window, vol_window)
    df = backtest_strategy(df, initial_capital, investment_fraction)

    # 결과를 파일로 저장
    if count == 200:
        save_market_backtest_result(market, df, count, "volatility", check_ma=check_ma, check_volume=check_volume)

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


def run_volatility_backtest(markets, count=200, initial_capital=10000, check_ma=False, check_volume=False):
    results = []

    title = "\n{ Volatility Backtest"
    if check_ma:
        title += " with Moving Average Check"
    if check_volume:
        title += " with Volume Check"
    title += " }\n"
    print(title)

    for market in markets:
        print(f"Volatility backtest for {market}...")
        result = run_backtest(market, count, initial_capital, k=0.5, investment_fraction=1, check_ma=check_ma, check_volume=check_volume)
        results.append(result)
        time.sleep(2)  # 각 API 호출 사이에 2초 지연

    result_df = save_backtest_results(results, count, "volatility" + ("_checkMA" if check_ma else "") + ("_checkVolume" if check_volume else ""))

    print(result_df)


if __name__ == "__main__":
    run_volatility_backtest()
