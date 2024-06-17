from backtest.golden_dead_cross_backtest import run_golden_cross_backtests
from backtest.daily_average_backtest import run_daily_average_backtest

if __name__ == "__main__":
    markets = ['KRW-BTC', 'KRW-ETH', 'KRW-AVAX', 'KRW-DOGE', 'KRW-BCH', "KRW-SHIB", "KRW-POLYX", "KRW-NEAR", "KRW-DOT", "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]
    count = 100
    initial_capital = 10000
    run_golden_cross_backtests(markets, count, initial_capital)
    run_daily_average_backtest(markets, count, initial_capital)
