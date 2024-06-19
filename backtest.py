from backtest.golden_dead_cross_backtest import run_golden_cross_backtests
from backtest.daily_average_backtest import run_daily_average_backtest

if __name__ == "__main__":
    markets = ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-AVAX', 'KRW-DOGE', 'KRW-BCH',
               "KRW-SHIB", "KRW-POLYX", "KRW-NEAR", "KRW-DOT",
               "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]
    COUNT = 200
    INTITAL_CAPITAL = 10000
    run_golden_cross_backtests(markets, COUNT, INTITAL_CAPITAL)
    run_daily_average_backtest(markets, COUNT, INTITAL_CAPITAL)
