import time
import numpy as np
from api.upbit_api import get_daily_candles
from utils import save_market_backtest_result, save_backtest_results, calculate_cumulative_return, calculate_mdd, calculate_win_rate
from utils.data_utils import get_recent_candles


def calculate_moving_averages(df, short_window=5, long_window=20):
    df = df.sort_index()
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    return df


def generate_signals(df, short_window):
    df['signal'] = 0
    df.loc[df.index[short_window:], 'signal'] = np.where(
        df.loc[df.index[short_window:], 'short_mavg'] > df.loc[df.index[short_window:], 'long_mavg'], 1, 0)
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


def run_backtest(market, count, initial_capital, short_window=5, long_window=20, investment_fraction=0.5):
    # df = get_daily_candles(market, count)
    df = get_recent_candles(market, count)
    df = calculate_moving_averages(df, short_window, long_window)
    df = generate_signals(df, short_window)
    df = backtest_strategy(df, initial_capital, investment_fraction)

    # 결과를 파일로 저장
    if count == 200 :
        save_market_backtest_result(market, df, count, "golden_dead_cross")

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


def run_golden_cross_backtests(markets, count=200, initial_capital=10000):
    # 책에서는 long_window가 60이지만 코인에서 적용해보니 20일이 수익률이 좋다.
    results = []

    print("\n{ Golden Dead Cross Backtest }")

    for market in markets:
        print(f"Golden dead cross backtest for {market}...")
        result = run_backtest(market, count, initial_capital, short_window=5, long_window=20, investment_fraction=1)
        results.append(result)
        time.sleep(2)  # 각 API 호출 사이에 2초 지연

    result_df = save_backtest_results(results, count, "golden_dead_cross")

    print(result_df)


if __name__ == "__main__":
    run_golden_cross_backtests()
