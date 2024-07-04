import pandas as pd
from datetime import datetime

def get_recent_candles(market, count):
    """
    지정된 시장의 최근 일봉 데이터를 가져오는 함수.

    :param market: 시장 코드 (예: 'KRW-BTC')
    :param count: 가져올 데이터의 개수
    :return: 최근 일봉 데이터가 포함된 Pandas DataFrame
    """
    file_path = f'data/daily_candles/daily_candles_{market}.csv'

    df = pd.read_csv(file_path, index_col=0, parse_dates=True)

    recent_data = df.tail(count)

    return recent_data

def get_minute_candles_from_file(ticker, count, start_date):
    """
    파일에서 분봉 데이터를 가져오는 함수.

    :param ticker: 티커 (예: 'KRW-BTC')
    :param count: 가져올 데이터의 개수
    :param start_date: 시작 날짜
    :return: 분봉 데이터가 포함된 Pandas DataFrame
    """
    file_path = f'data/minutes_candles/minutes_candles_{ticker}_60.csv'

    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    df = df.sort_index()  # 날짜 순으로 정렬

    # start_date를 tz-naive로 변환
    if start_date.tzinfo is not None:
        start_date = start_date.replace(tzinfo=None)

    # 시작 날짜 이후의 데이터 필터링
    df_filtered = df[df.index >= start_date]

    # 가져올 데이터의 개수 제한
    if count:
        df_filtered = df_filtered.head(count)

    return df_filtered
