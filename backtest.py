"""
backtest.py
"""

import asyncio
from backtest.golden_dead_cross_backtest import run_golden_cross_backtests
from backtest.daily_average_backtest import run_daily_average_backtest
from backtest.volatility_backtest import run_volatility_backtest
from backtest.afternoon_backtest import run_afternoon_backtest
from coins import coin_list

async def backtest():
    COUNT = 200
    INITIAL_CAPITAL = 10000

    # coin_list = ["KRW-SOL"]

    run_golden_cross_backtests(coin_list, COUNT, INITIAL_CAPITAL)
    run_daily_average_backtest(coin_list, COUNT, INITIAL_CAPITAL)
    run_volatility_backtest(coin_list, COUNT, INITIAL_CAPITAL)
    run_volatility_backtest(coin_list, COUNT, INITIAL_CAPITAL, check_ma=True)
    run_volatility_backtest(coin_list, COUNT, INITIAL_CAPITAL, check_ma=True, check_volume=True)
    await run_afternoon_backtest(coin_list, COUNT, INITIAL_CAPITAL)

if __name__ == "__main__":
    asyncio.run(backtest())
