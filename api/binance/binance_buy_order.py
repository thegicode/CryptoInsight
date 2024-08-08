import os
import sys
import ccxt
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from api.binance.binance_api_helpers import create_exchange

def place_buy_order(symbol, amount, price=None, order_type='limit'):
    """바이낸스에서 매수 주문을 실행하고 결과를 DataFrame으로 출력합니다."""
    try:
        exchange = create_exchange()

        # 매수 주문 생성
        if order_type == 'limit':
            # 지정가 주문
            order = exchange.create_limit_buy_order(symbol, amount, price)
        elif order_type == 'market':
            # 시장가 주문
            order = exchange.create_market_buy_order(symbol, amount)
        else:
            print("지원되지 않는 주문 유형입니다.")
            return

        # 주문 정보를 데이터로 변환
        order_data = {
            'Order ID': [order['id']],
            'Symbol': [order['symbol']],
            'Type': [order['type']],
            'Side': [order['side']],
            'Price': [order['price']],
            'Amount': [order['amount']],
            'Filled': [order['filled']],
            'Remaining': [order['remaining']],
            'Status': [order['status']],
            'Datetime': [order['datetime']],
            'Fee Cost': [order['fee']['cost'] if 'fee' in order and order['fee'] else None],
            'Fee Currency': [order['fee']['currency'] if 'fee' in order and order['fee'] else None]
        }

        # DataFrame으로 변환
        order_df = pd.DataFrame(order_data)

        # DataFrame 출력
        print("매수 주문 결과 (DataFrame):")
        print(order_df)

    except ccxt.NetworkError as e:
        print(f"네트워크 오류: {e}")
    except ccxt.ExchangeError as e:
        print(f"거래소 오류: {e}")
    except Exception as e:
        print(f"예외가 발생했습니다: {e}")

if __name__ == "__main__":
    # 예제: SOL/USDT 거래쌍에 대해 0.047 SOL을 지정가 140 USDT에 매수
    place_buy_order('SOL/USDT', amount=0.047, price=140, order_type='limit')

    # 예제: SOL/USDT 거래쌍에 대해 0.1 SOL을 시장가로 매수
    # place_buy_order('SOL/USDT', amount=0.1, order_type='market')
