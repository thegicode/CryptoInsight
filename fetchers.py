"""
fetchers.py
"""

import asyncio
from fetchers.fetch_daily_candles import fetch_and_save_daily_candles
from fetchers.fetch_minute_candles import fetch_and_save_minutes_candles
from coins import coin_list

async def fetchers():
    COUNT = 200
    # coin_list = ["KRW-SOL"]

    # Fetch and save daily candles
    await fetch_and_save_daily_candles(coin_list, COUNT)

    # Fetch and save minute candles
    await fetch_and_save_minutes_candles(coin_list, 60, COUNT)


if __name__ == "__main__":
    asyncio.run(fetchers())