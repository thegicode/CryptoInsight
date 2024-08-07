import requests
import pandas as pd

def fetch_daily_candles(symbol):
    """주어진 심볼의 일간 캔들 데이터를 가져옵니다."""
    url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
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

        # 인덱스 번호 추가
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Index Number'}, inplace=True)

        # 캔들의 수 출력
        print(f"Candle size for {symbol}: {len(df)}")

        return df
    else:
        raise Exception("Failed to fetch data from API")

def save_to_csv(df, symbol):
    """데이터프레임을 CSV 파일로 저장합니다."""
    file_path = f"data/binance/daily_candles_{symbol}.csv"
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

def fetch_binanace_daily_candles(market_name):
    """주어진 시장 심볼의 데이터를 처리하여 CSV로 저장하고 출력합니다."""
    # 데이터 가져오기
    df = fetch_daily_candles(market_name)

    # 데이터 저장
    save_to_csv(df, market_name)

    # 데이터프레임 출력
    print("\nDataframe head:")
    print(df.head())

# 함수 호출 예시
# fetch_binanace_daily_candles('BTCUSDT')
fetch_binanace_daily_candles('SOLUSDT')
# fetch_binanace_daily_candles('ETHUSDT')
# fetch_binanace_daily_candles('XRPUSDT')
# fetch_binanace_daily_candles('SHIBUSDT')
# fetch_binanace_daily_candles('BNBUSDT')
# fetch_binanace_daily_candles('DOGEUSDT')


