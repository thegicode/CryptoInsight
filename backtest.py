from backtest.golden_dead_cross_backtest import run_golden_cross_backtests
from backtest.daily_average_backtest import run_daily_average_backtest
from backtest.volatility_backtest import run_volatility_backtest
from coins import coin_list

if __name__ == "__main__":
    COUNT = 200
    INTITAL_CAPITAL = 10000

    run_golden_cross_backtests(coin_list, COUNT, INTITAL_CAPITAL)
    run_daily_average_backtest(coin_list, COUNT, INTITAL_CAPITAL)
    run_volatility_backtest(coin_list, COUNT, INTITAL_CAPITAL)
    run_volatility_backtest(coin_list, COUNT, INTITAL_CAPITAL, check_ma=True)
    run_volatility_backtest(coin_list, COUNT, INTITAL_CAPITAL, check_ma=True, check_volume=True)
