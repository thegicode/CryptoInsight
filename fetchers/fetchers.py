# fetchers/fetchers.py

import sys
import os
import asyncio

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from coins import coin_list
from .fetch_daily_candles import fetch_and_save_daily_candles
from .fetch_minute_candles import fetch_and_save_minutes_candles

async def fetchers():
    COUNT = 200
    # coin_list = ["KRW-SOL"]

    # Fetch and save daily candles
    await fetch_and_save_daily_candles(coin_list, COUNT)

    # Fetch and save minute candles
    await fetch_and_save_minutes_candles(coin_list, 60, COUNT)

if __name__ == "__main__":
    asyncio.run(fetchers())
