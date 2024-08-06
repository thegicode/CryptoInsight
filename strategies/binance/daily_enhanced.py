# 전략 설명
"""
이 전략은 비트코인 가격을 대상으로 40일 이동평균선을 기준으로 매수 및 매도를 결정하며,
추가 매수는 현재 남은 자본금의 1%로 설정합니다. 다음은 이 전략의 상세 내용입니다:

1. 초기 자본금: 100만원
   - 초기 자본금으로 모든 거래를 시작합니다.

2. 매수 조건:
   - 가격이 40일 이동평균선을 상향 돌파할 때 잔액 전액 매수.
   - 가격이 40일 이동평균선 아래에 있고 매도 신호가 아닌 날에 전날보다 가격과 거래량이 상승하면
     남은 자본금의 1%로 추가 매수.

3. 매도 조건:
   - 가격이 40일 이동평균선을 하향 돌파하면 보유한 모든 자산을 매도.

4. 거래 시간:
   - 주로 높은 유동성과 변동성을 활용하기 위해 UTC 12:00 ~ 20:00 (한국 시간 21:00 ~ 05:00)
     사이에 거래를 집중합니다.
   - 이 시간대는 북미와 유럽 시장이 겹치며, 암호화폐 거래량이 높은 시기입니다.

5. 수수료:
   - 모든 거래에는 0.1%의 수수료가 부과되어 실질적인 거래 비용을 반영합니다.

6. 목표:
   - 이 전략은 상승 추세를 따라가며 하락 위험을 최소화하여 자본을 성장시키는 것을 목표로 합니다.
   - 지속적인 상승장에서의 수익 극대화를 위해 자본금의 일정 비율로 추가 매수를 진행합니다.
"""

import pandas as pd
import numpy as np
import ccxt  # 암호화폐 거래소 API를 위한 라이브러리
from dotenv import load_dotenv
import sys
import os

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from utils.telegram import send_telegram_message  # telegram.py의 함수 가져오기

# 환경 변수 로드 함수
def load_environment_variables():
    """환경 변수를 로드합니다."""
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    return api_key, secret_key

# 바이낸스 거래소 객체 생성 함수
def create_exchange(api_key, secret_key):
    """바이낸스 거래소 객체를 생성합니다."""
    return ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        'enableRateLimit': True,
    })

# 바이낸스 데이터 가져오기 함수
def fetch_binance_data(exchange, symbol, limit=45):
    """바이낸스에서 OHLCV 데이터를 가져옵니다."""
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=limit)
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)
    return df

# 이동 평균 계산
def calculate_moving_average(df, window):
    """이동 평균을 계산하여 데이터프레임에 추가합니다."""
    df[f'{window}MA'] = df['Close'].rolling(window=window).mean()

# 매수 및 매도 신호 생성 함수
def get_signals(df, capital, last_trade_date, window=40, fee_rate=0.001):
    """매수 및 매도 신호를 생성합니다."""
    calculate_moving_average(df, window)
    signals = []

    in_position = False  # 현재 포지션 상태를 확인하는 변수
    quantity = 0

    for i in range(window, len(df)):  # window일 이후부터 신호 생성 가능
        current_date = df.index[i].date()

        # 매도 신호: 40일 이동평균선 하향 돌파
        is_sell_signal = (
            df['Close'].iloc[i] < df[f'{window}MA'].iloc[i] and
            df['Close'].iloc[i-1] >= df[f'{window}MA'].iloc[i-1] and
            in_position
        )
        if is_sell_signal:
            quantity, capital = execute_sell(df, i, quantity, capital, fee_rate)
            signals.append(('sell', df.index[i], df['Close'].iloc[i], quantity))
            in_position = False
            continue  # 매도 신호가 발생하면 추가 매수를 무시

        # 매수 신호: 40일 이동평균선 상향 돌파
        is_buy_signal = (
            df['Close'].iloc[i] > df[f'{window}MA'].iloc[i] and
            df['Close'].iloc[i-1] <= df[f'{window}MA'].iloc[i-1] and
            not in_position
        )
        if is_buy_signal and current_date != last_trade_date:
            quantity, capital = execute_buy(df, i, capital, fee_rate)
            signals.append(('buy', df.index[i], df['Close'].iloc[i], quantity))
            in_position = True
            last_trade_date = current_date

        # 추가 매수 신호: 40일 이동평균선 아래, 전일보다 가격 및 거래량 상승
        is_additional_buy_signal = (
            df['Close'].iloc[i] < df[f'{window}MA'].iloc[i] and
            not in_position and
            df['Close'].iloc[i] > df['Close'].iloc[i-1] and
            df['Volume'].iloc[i] > df['Volume'].iloc[i-1]
        )
        if is_additional_buy_signal and current_date != last_trade_date:
            quantity, capital = execute_additional_buy(df, i, capital, fee_rate)
            signals.append(('additional_buy', df.index[i], df['Close'].iloc[i], quantity))
            last_trade_date = current_date

    return signals, capital, last_trade_date


# 매수 실행 함수
def execute_buy(df, i, capital, fee_rate):
    """매수 실행을 처리합니다."""
    buy_price = df['Close'].iloc[i] * (1 + fee_rate)
    quantity = capital / buy_price
    capital -= buy_price * quantity  # 자본금에서 매수 금액 차감
    return quantity, capital

# 추가 매수 실행 함수
def execute_additional_buy(df, i, capital, fee_rate):
    """추가 매수 실행을 처리합니다."""
    additional_investment = capital * 0.01
    additional_buy_price = df['Close'].iloc[i] * (1 + fee_rate)
    additional_quantity = additional_investment / additional_buy_price
    capital -= additional_buy_price * additional_quantity  # 자본금에서 추가 매수 금액 차감
    return additional_quantity, capital

# 매도 실행 함수
def execute_sell(df, i, quantity, capital, fee_rate):
    """매도 실행을 처리합니다."""
    sell_price = df['Close'].iloc[i] * (1 - fee_rate)
    capital += sell_price * quantity  # 매도로 인한 자본금 증가
    quantity = 0
    return quantity, capital

# 신호 처리 및 거래 내역 생성
def process_signals(signals):
    """생성된 신호를 처리하고 거래 내역을 생성합니다."""
    trades = []
    for signal in signals:
        trades.append({
            'Action': signal[0],
            'Time': signal[1],
            'Price': signal[2],
            'Quantity': signal[3]
        })
    return trades

# 거래 내역 출력 및 메시지 전송
def send_trade_report(strategy_name, trades, df, window, fee_rate):
    """거래 내역을 출력하고 텔레그램으로 전송합니다."""
    if trades:
        trade_messages = "\n".join(
            [f"{trade['Action']} {trade['Quantity']:.6f} BTC at {trade['Price']} on {trade['Time']}" for trade in trades]
        )
        full_message = f"{strategy_name}\n오늘의 거래 내역:\n{trade_messages}"
    else:
        full_message = f"{strategy_name}\n오늘 거래가 없습니다."

    # 최근 5일간의 거래 신호 추가
    recent_signals = generate_recent_signals(df, window, fee_rate)
    recent_signals_message = "\n".join(recent_signals) if recent_signals else "최근 5일간의 거래 신호가 없습니다."
    full_message += f"\n최근 5일간의 거래 신호:\n{recent_signals_message}"

    print(full_message)
    send_telegram_message(full_message)  # 전체 메시지를 텔레그램으로 전송

# 최근 5일간의 거래 신호 생성
def generate_recent_signals(df, window, fee_rate):
    """최근 5일간의 거래 신호를 생성합니다."""
    recent_signals = []
    for i in range(len(df) - 5, len(df)):  # 최근 5일간의 데이터에서 신호 생성
        if df['Close'].iloc[i] > df[f'{window}MA'].iloc[i] and df['Close'].iloc[i-1] <= df[f'{window}MA'].iloc[i-1]:
            price = df['Close'].iloc[i] * (1 + fee_rate)
            recent_signals.append(f"buy signal at {price} on {df.index[i]}")
        elif df['Close'].iloc[i] < df[f'{window}MA'].iloc[i] and df['Close'].iloc[i-1] >= df[f'{window}MA'].iloc[i-1]:
            price = df['Close'].iloc[i] * (1 - fee_rate)
            recent_signals.append(f"sell signal at {price} on {df.index[i]}")
        # 어제보다 가격과 거래량이 상승한 경우
        elif df['Close'].iloc[i] < df[f'{window}MA'].iloc[i] and df['Close'].iloc[i] > df['Close'].iloc[i-1] and df['Volume'].iloc[i] > df['Volume'].iloc[i-1]:
            price = df['Close'].iloc[i] * (1 + fee_rate)
            recent_signals.append(f"price and volume up signal at {price} on {df.index[i]}")
    return recent_signals

# 메인 거래 실행 함수
def run_daily_trading(symbol='BTC/USDT', initial_capital=1000000):
    strategy_name = "40일 이동평균선 전략"
    window = 40
    capital = initial_capital
    last_trade_date = None
    fee_rate = 0.001  # 거래 수수료 0.1%

    # 환경 변수 로드
    api_key, secret_key = load_environment_variables()

    # 거래소 객체 생성
    exchange = create_exchange(api_key, secret_key)

    # 데이터 수집
    df = fetch_binance_data(exchange, symbol)

    # 매수/매도 신호 생성 및 자본금 업데이트
    signals, capital, last_trade_date = get_signals(df, capital, last_trade_date, window, fee_rate=fee_rate)

    # 거래 내역 생성
    trades = process_signals(signals)

    # 거래 내역 출력 및 메시지 전송
    send_trade_report(strategy_name, trades, df, window, fee_rate)

# 거래 실행
run_daily_trading(symbol='BTC/USDT', initial_capital=1000000)
