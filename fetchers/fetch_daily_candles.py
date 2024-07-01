"""
fetchers/fetch_daily_candles.py
"""

import os
import pandas as pd
import datetime
import pytz
import asyncio
from requests.exceptions import HTTPError

from api.upbit_api import get_daily_candles

async def fetch_and_save_daily_candles(markets, count):
    """ 여러 시장의 과거 일봉 데이터를 가져와 저장합니다 """
    save_dir = "data/daily_candles"
    os.makedirs(save_dir, exist_ok=True)

    for market in markets:
        save_path = os.path.join(save_dir, f"daily_candles_{market}_{count}.csv")
        print(f"Fetching daily candles for {market}...")

        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = end - datetime.timedelta(days=count)

        df_list = []
        if os.path.exists(save_path):
            existing_data = pd.read_csv(save_path, index_col=0, parse_dates=True)
            last_date = existing_data.index[-1]
            if last_date.tzinfo is None:
                last_date = last_date.tz_localize('Asia/Seoul')
            else:
                last_date = last_date.tz_convert('Asia/Seoul')

            if last_date >= end:
                print(f"Data for {market} is already up to date.")
                continue

            start = last_date + datetime.timedelta(days=1)
            df_list.append(existing_data)

        while start < end:
            try:
                df = get_daily_candles(market, min(count, (end - start).days))
                df = df.sort_index()  # 인덱스를 기준으로 오래된 시간 순으로 정렬
                df_list.append(df)
                start += datetime.timedelta(days=min(count, (end - start).days))
                await asyncio.sleep(1)  # 요청 간 지연 시간 추가
            except HTTPError as http_err:
                if http_err.response.status_code == 429:
                    print(f"HTTPError: {http_err}. Too many requests, sleeping for 10 seconds.")
                    await asyncio.sleep(10)
                else:
                    raise

        if df_list:
            full_df = pd.concat(df_list)
            full_df = full_df[~full_df.index.duplicated(keep='last')]
            full_df.to_csv(save_path)
            print(f"Data for {market} saved to {save_path}")

if __name__ == "__main__":
    asyncio.run(fetch_and_save_daily_candles())
