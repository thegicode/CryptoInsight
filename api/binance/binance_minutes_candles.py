import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_candles(symbol, interval, start_date, end_date=None):
    """주어진 심볼의 지정된 간격의 캔들 데이터를 시작 날짜부터 종료 날짜까지 가져옵니다."""
    url = 'https://api.binance.com/api/v3/klines'

    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    start_timestamp = int(pd.to_datetime(start_date).timestamp() * 1000)
    end_timestamp = int(pd.to_datetime(end_date).timestamp() * 1000)

    all_data = []

    while start_timestamp < end_timestamp:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_timestamp,
            'endTime': end_timestamp,
            'limit': 1000
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            all_data.extend(data)
            start_timestamp = data[-1][6]  # 마지막 데이터의 Close Time을 다음 요청의 시작 시간으로 설정
        else:
            raise Exception("Failed to fetch data from API")

    df = pd.DataFrame(all_data, columns=[
        'Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
        'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume',
        'Taker Buy Quote Asset Volume', 'Ignore'
    ])
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')

    # 인덱스 번호 추가
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Index Number'}, inplace=True)

    # 캔들의 수 출력
    print(f"Candle size for {symbol} ({interval}): {len(df)}")

    return df

def save_to_csv(df, symbol, interval):
    """데이터프레임을 CSV 파일로 저장합니다."""
    file_path = f"data/binance/{interval}_candles_{symbol}.csv"
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

def fetch_binance_candles(market_name, interval, start_date, end_date=None):
    """주어진 시장 심볼의 데이터를 시작 날짜부터 종료 날짜까지 처리하여 CSV로 저장하고 출력합니다."""
    # 일봉 데이터 맞추기

    # 데이터 가져오기
    df = fetch_candles(market_name, interval, start_date, end_date)

    # 데이터 저장
    save_to_csv(df, market_name, interval)

    # 데이터프레임 출력
    print("\nDataframe head:")
    print(df.head())
    print(df.tail())


def get_date_from_daily_candles(market_name) :
    file_path = f'data/binance/daily_candles_{market_name}.csv'
    df = pd.read_csv(file_path)
    open_time_0 = df.loc[0, 'Open Time']
    return open_time_0


start_date = get_date_from_daily_candles('SOLUSDT')
fetch_binance_candles('SOLUSDT', '4h', start_date)
