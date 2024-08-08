import os
import sys
import ccxt
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from api.binance.binance_api_helpers import create_exchange

def cancel_order(symbol, order_id):
    """지정된 주문을 취소합니다."""
    try:
        exchange = create_exchange()

        # 주문 취소
        cancellation = exchange.cancel_order(order_id, symbol)

        # 취소된 주문 정보 출력
        print("주문이 성공적으로 취소되었습니다:")
        print(f"  주문 ID: {cancellation['id']}")
        print(f"  심볼: {cancellation['symbol']}")
        print(f"  상태: {cancellation['status']}")
        print(f"  시간: {cancellation['datetime']}")

    except ccxt.NetworkError as e:
        print(f"네트워크 오류: {e}")
    except ccxt.ExchangeError as e:
        print(f"거래소 오류: {e}")
    except Exception as e:
        print(f"예외가 발생했습니다: {e}")

if __name__ == "__main__":
    # 예제: 특정 주문 ID를 사용하여 SOL/USDT 거래쌍의 주문 취소
    cancel_order('SOL/USDT', '')
