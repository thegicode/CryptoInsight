import ccxt
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from utils.telegram import send_telegram_message  # telegram.py의 함수 가져오기

def load_environment_variables():
    """환경 변수를 로드합니다."""
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    return api_key, secret_key

def create_exchange(api_key, secret_key):
    """바이낸스 거래소 객체를 생성합니다."""
    return ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        'enableRateLimit': True,
    })

def fetch_binance_data(exchange, symbol, timeframe, limit=100):
    """바이낸스에서 OHLCV 데이터를 가져옵니다."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data.set_index('timestamp', inplace=True)
    return data

def calculate_moving_average(data, period):
    """n일 이동평균선을 계산합니다."""
    return data['close'].rolling(window=period).mean()

def generate_signals(data, ma_period):
    """이동평균선을 기반으로 매수, 매도, 매수 유지, 유지 신호를 생성합니다."""
    data['MA'] = calculate_moving_average(data, ma_period)

    # 초기 신호 생성
    data['signal'] = np.where(data['close'] > data['MA'], 1, 0)  # 1: 매수, 0: 매도
    data['positions'] = data['signal'].diff()  # 신호 변화 계산

    # 신호 해석
    data['signal'] = np.where(data['positions'] == 1, 'buy',  # 매수 신호
                              np.where(data['positions'] == -1, 'sell',  # 매도 신호
                                       np.where((data['signal'].shift() == 1) & (data['signal'] == 1), 'hold',  # 매수 유지
                                                np.where((data['signal'].shift() == 0) & (data['signal'] == 0), 'idle',  # 매도 후 상태
                                                         'wait'))))
    return data

def place_order(exchange, symbol, side, amount):
    """매수 또는 매도 주문을 실행합니다."""
    try:
        order = exchange.create_market_order(symbol, side, amount)
        print(f"Order placed: {order}")
    except Exception as e:
        print(f"Error placing order: {e}")

def get_balance(exchange, asset):
    """해당 자산의 잔고를 가져옵니다."""
    balance = exchange.fetch_balance()
    return balance['free'].get(asset, 0)

def check_and_execute_trade(signal_data, exchange, symbol, buy_percentage, sell_percentage):
    """매수 및 매도 신호에 따라 거래를 실행합니다."""
    last_signal = signal_data['signal'].iloc[-1]
    print(f"Last signal: {last_signal}")

    base_asset = symbol.split('/')[0]  # BTC/USDT => BTC
    quote_asset = symbol.split('/')[1]  # BTC/USDT => USDT

    message = f"이동평균선 신호: {last_signal}\n"

    if last_signal == 'buy':
        # 매수 주문 실행 - USDT의 일정 비율로 매수
        usdt_balance = get_balance(exchange, quote_asset)
        buy_amount = usdt_balance * buy_percentage
        if buy_amount > 0:
            print(f"Buying {buy_amount} {quote_asset} worth of {base_asset}")
            # place_order(exchange, symbol, 'buy', buy_amount)  # Uncomment to place order
            message += f"Buying {buy_amount} {quote_asset} worth of {base_asset}\n"
        else:
            print(f"No {quote_asset} balance to buy.")
            message += f"No {quote_asset} balance to buy.\n"
    elif last_signal == 'sell':
        # 매도 주문 실행 - 보유 자산의 일정 비율로 매도
        base_balance = get_balance(exchange, base_asset)
        sell_amount = base_balance * sell_percentage
        if sell_amount > 0:
            print(f"Selling {sell_amount} {base_asset}")
            # place_order(exchange, symbol, 'sell', sell_amount)  # Uncomment to place order
            message += f"Selling {sell_amount} {base_asset}\n"
        else:
            print(f"No {base_asset} balance to sell.")
            message += f"No {base_asset} balance to sell.\n"
    elif last_signal == 'hold':
        print("Holding position...")
        message += "Holding position...\n"
    elif last_signal == 'idle':
        print("Idle after selling, maintaining state...")
        message += "Idle after selling, maintaining state...\n"
    else:
        print("Waiting, no action required.")
        message += "Waiting, no action required.\n"

    # Send the result message via Telegram
    send_telegram_message(message)

def main():
    """주요 실행 로직"""
    # 설정
    symbol = 'BTC/USDT'  # 거래할 암호화폐 심볼
    timeframe = '1d'     # 데이터 시간 프레임 (e.g., '1d', '1h')
    n = 40               # 이동평균선 기간
    data_limit = int(n + n/2)  # 가져올 데이터 개수
    buy_percentage = 1 # 매수 시 사용할 USDT 비율 0.5
    sell_percentage = 1 # 매도 시 매도할 자산 비율 0.5

    # 환경 변수 로드
    api_key, secret_key = load_environment_variables()

    # 거래소 객체 생성
    exchange = create_exchange(api_key, secret_key)

    # 데이터 가져오기
    data = fetch_binance_data(exchange, symbol, timeframe, limit=data_limit)

    # 신호 생성
    signal_data = generate_signals(data, n)

    # 최근 3일간의 신호 출력
    recent_signals = signal_data.tail(3)
    print(recent_signals[['close', 'MA', 'positions', 'signal']])

    # 거래 실행 및 텔레그램 알림 전송
    check_and_execute_trade(signal_data, exchange, symbol, buy_percentage, sell_percentage)

if __name__ == "__main__":
    main()
