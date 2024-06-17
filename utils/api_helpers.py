from api.upbit_api import get_daily_candles
import asyncio
import requests

async def fetch_latest_data_with_retry(market, count=5, delay=2):
    for _ in range(3):  # 최대 3번 재시도
        try:
            df = get_daily_candles(market, count)
            return df
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                print(f"Rate limit exceeded for {market}. Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                raise e
    raise Exception(f"Failed to retrieve data for {market} after 3 retries.")