import os
import sys
import ccxt
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from api.binance.binance_api_helpers import create_exchange


def fetch_order_sample(symbol, order_id):
    """특정 주문의 세부 정보를 가져와 DataFrame으로 출력합니다."""
    try:
        exchange = create_exchange()

        # 특정 주문 정보 가져오기
        order = exchange.fetch_order(order_id, symbol)

        # 주문 정보를 딕셔너리로 변환
        order_data = {
            'Order ID': order['id'],
            'Symbol': order['symbol'],
            'Order Type': order['type'],
            'Side': order['side'],
            'Price': order['price'],
            'Amount': order['amount'],
            'Filled': order['filled'],
            'Remaining': order['remaining'],
            'Status': order['status'],
            'Datetime': order['datetime'],
            'Fee Cost': order['fee']['cost'] if 'fee' in order and order['fee'] else None,
            'Fee Currency': order['fee']['currency'] if 'fee' in order and order['fee'] else None
        }

        # DataFrame으로 변환
        order_df = pd.DataFrame([order_data])

        # 주문 정보 출력
        print("주문 상세 정보 (DataFrame):")
        print(order_df)

    except ccxt.NetworkError as e:
        print(f"네트워크 오류: {e}")
    except ccxt.ExchangeError as e:
        print(f"거래소 오류: {e}")
    except Exception as e:
        print(f"예외가 발생했습니다: {e}")

if __name__ == "__main__":
    # 예제: SOL/USDT 거래쌍의 특정 주문 ID로 정보 가져오기
    order_id = ''  # 실제 주문 ID로 변경
    fetch_order_sample('SOL/USDT', order_id)
