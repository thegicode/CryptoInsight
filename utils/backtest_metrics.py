
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
