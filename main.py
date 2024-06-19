import asyncio
from strategies import golden_dead_cross_signals, daily_average_signals, volatility_adjusted_moving_average_strategy


async def main():
    task1 = asyncio.create_task(golden_dead_cross_signals())
    task2 = asyncio.create_task(daily_average_signals())
    task3 = asyncio.create_task(volatility_adjusted_moving_average_strategy())
    await asyncio.gather(task1, task2, task3)

    # task1 = asyncio.create_task(golden_dead_cross_signals())
    # await asyncio.gather(task1)


if __name__ == "__main__":
    asyncio.run(main())
