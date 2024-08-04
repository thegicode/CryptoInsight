import requests
import pandas as pd

def fetch_daily_candles(market_name):
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': market_name,
        'interval': '1d'
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=[
            'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
            'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume',
            'Taker Buy Quote Asset Volume', 'Ignore'
        ])
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
        return df
    else:
        raise Exception("Failed to fetch data from API")

def save_to_csv(df, market_name):
    file_path = f"data/binance/daily_candles_{market_name}.csv"
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

# 사용 예
market_name = 'BTCUSDT'
df = fetch_daily_candles(market_name)
save_to_csv(df, market_name)
