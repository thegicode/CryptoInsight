import os
import sys
import ccxt
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from api.binance.binance_api_helpers import create_exchange

def fetch_open_orders(symbol=None):
    """미체결 주문을 조회하여 DataFrame으로 출력합니다."""
    try:
        exchange = create_exchange()

        # 심볼이 지정되지 않으면 모든 미체결 주문을 가져옵니다
        if symbol:
            open_orders = exchange.fetch_open_orders(symbol)
        else:
            open_orders = exchange.fetch_open_orders()

        if not open_orders:
            print("현재 미체결 주문이 없습니다.")
            return

        # 미체결 주문 데이터를 DataFrame으로 변환
        orders_data = {
            'Order ID': [],
            'Symbol': [],
            'Type': [],
            'Side': [],
            'Price': [],
            'Amount': [],
            'Status': [],
            'Datetime': []
        }

        for order in open_orders:
            orders_data['Order ID'].append(order['id'])
            orders_data['Symbol'].append(order['symbol'])
            orders_data['Type'].append(order['type'])
            orders_data['Side'].append(order['side'])
            orders_data['Price'].append(order['price'])
            orders_data['Amount'].append(order['amount'])
            orders_data['Status'].append(order['status'])
            orders_data['Datetime'].append(order['datetime'])

        orders_df = pd.DataFrame(orders_data)

        print("미체결 주문 목록 (DataFrame):")
        print(orders_df)

    except ccxt.NetworkError as e:
        print(f"네트워크 오류: {e}")
    except ccxt.ExchangeError as e:
        print(f"거래소 오류: {e}")
    except Exception as e:
        print(f"예외가 발생했습니다: {e}")

if __name__ == "__main__":
    # 모든 미체결 주문을 확인
    # fetch_open_orders()

    # 특정 심볼의 미체결 주문을 확인 (예: 'SOL/USDT')
    fetch_open_orders('SOL/USDT')
