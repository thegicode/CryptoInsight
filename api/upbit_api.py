import requests
import pandas as pd
from api.constants import UPBIT_SERVER_URL


def get_daily_candles(market: str, count: int = 200):
    """
    업비트 API를 사용하여 일봉 데이터를 가져오는 함수.

    :param market: 코인 시장 코드 (예: 'KRW-BTC')
    :param count: 가져올 일봉 데이터의 수
    :return: Pandas DataFrame으로 변환된 일봉 데이터
    """
    url = f"{UPBIT_SERVER_URL}/v1/candles/days"
    params = {
        "market": market,
        "count": count
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # 요청이 실패하면 예외를 발생시킴
    data = response.json()

    # JSON 데이터를 DataFrame으로 변환
    df = pd.DataFrame(data)
    # 날짜 형식을 datetime 객체로 변환
    df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
    # 필요한 열만 선택
    df = df[['candle_date_time_kst', 'opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume']]
    # 열 이름을 더 간단하게 변경
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    # 'date' 열을 인덱스로 설정
    df.set_index('date', inplace=True)

    return df

def get_minute_candles(market, interval, count, to):
    url = f"{UPBIT_SERVER_URL}/v1/candles/minutes/{interval}"
    params = {
        "market": market,
        "count": count,
        "to": to
    }
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # 요청이 실패하면 예외를 발생시킴
    data = response.json()


    # JSON 데이터를 DataFrame으로 변환
    df = pd.DataFrame(data)
    df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
     # 필요한 열만 선택
    df = df[['candle_date_time_kst', 'opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume']]
    # 열 이름을 더 간단하게 변경
    df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    # 'date' 열을 인덱스로 설정
    df.set_index('date', inplace=True)

    return df



def get_markets():
    url = f"{UPBIT_SERVER_URL}/v1/market/all"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 요청 실패 시 예외 발생

    markets = response.json()

    # "market_warning"이 존재하고 "NONE"인 경우 및 "KRW"로 시작하는 마켓만 필터링
    filtered_markets = [
        market['market'] for market in markets
        if market.get('market_warning', 'NONE') == "NONE" and market['market'].startswith("KRW")
    ]

    return filtered_markets
