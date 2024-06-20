import asyncio
from strategies import golden_dead_cross_signals, daily_average_signals, volatility_strategy


async def main():
    markets = ['KRW-BTC', 'KRW-ETH', 'KRW-SOL', 'KRW-AVAX', 'KRW-DOGE', 'KRW-BCH',
               "KRW-SHIB", "KRW-POLYX", "KRW-NEAR", "KRW-DOT",
               "KRW-THETA", "KRW-TFUEL", "KRW-ZRX"]

    task1 = asyncio.create_task(golden_dead_cross_signals(markets))
    task2 = asyncio.create_task(daily_average_signals(markets))
    task3 = asyncio.create_task(volatility_strategy(markets))
    task3_ma = asyncio.create_task(volatility_strategy(markets, check_ma=True))

    await asyncio.gather(task1, task2, task3, task3_ma)


if __name__ == "__main__":
    asyncio.run(main())
