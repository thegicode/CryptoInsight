import asyncio
from scripts import golden_dead_cross_signals, daily_average_signals

async def main():
    task1 = asyncio.create_task(golden_dead_cross_signals())
    task2 = asyncio.create_task(daily_average_signals())
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())