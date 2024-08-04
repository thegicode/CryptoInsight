import ccxt
import pandas as pd
import numpy as np
import datetime

def fetch_binance_data(symbol, timeframe, limit=100):
    # 바이낸스 API 설정
    exchange = ccxt.binance()
    # 데이터 가져오기
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    # 데이터를 DataFrame으로 변환
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

def calculate_moving_average(data, period):
    # n일 이동평균선 계산
    return data['close'].rolling(window=period).mean()

def generate_signals(data, ma_period):
    # 이동평균선 계산
    data['MA'] = calculate_moving_average(data, ma_period)

    # 매수 및 매도 신호 생성
    data['signal'] = np.where(data['close'] > data['MA'], 'buy', 'sell')

    return data

# 파라미터 설정
symbol = 'BTC/USDT'  # 거래할 암호화폐 심볼
timeframe = '1d'     # 데이터 시간 프레임 (e.g., '1d', '1h')
n = 40               # 이동평균선 기간
data_limit = int(n + n/2)   # 가져올 데이터 개수 (n + 추가 데이터)

# 바이낸스에서 데이터 가져오기
data = fetch_binance_data(symbol, timeframe, limit=data_limit)

# 신호 생성
signal_data = generate_signals(data, n)

# 마지막 며칠간의 데이터와 신호를 출력
print(signal_data.tail())
