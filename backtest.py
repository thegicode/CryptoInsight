from backtest.golden_dead_cross_backtest import run_golden_cross_backtests
from backtest.daily_average_backtest import run_daily_average_backtest
from backtest.volatility_backtest import run_volatility_backtest

if __name__ == "__main__":
    markets = ['KRW-AVAX', 'KRW-BCH', 'KRW-BTC', 'KRW-DOGE', 'KRW-DOT', 'KRW-ETH', 'KRW-NEAR', 'KRW-POLYX', 'KRW-SHIB', 'KRW-SOL', 'KRW-THETA', 'KRW-TFUEL', 'KRW-ZRX']
    COUNT = 200
    INTITAL_CAPITAL = 10000

    run_golden_cross_backtests(markets, COUNT, INTITAL_CAPITAL)
    run_daily_average_backtest(markets, COUNT, INTITAL_CAPITAL)
    run_volatility_backtest(markets, COUNT, INTITAL_CAPITAL)
    run_volatility_backtest(markets, COUNT, INTITAL_CAPITAL, check_ma=True)
