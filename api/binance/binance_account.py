import sys
import os
import ccxt
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from api.binance.binance_api_helpers import create_exchange

def fetch_account_balance():
    """계좌 잔고를 조회하여 DataFrame으로 출력합니다."""
    try:
        exchange = create_exchange()

        # 계좌 잔고 가져오기
        balance = exchange.fetch_balance()

        # 잔고 데이터를 DataFrame으로 변환
        balance_data = {
            'Currency': [],
            'Total Balance': [],
            'Free Balance': [],
            'Used Balance': []
        }

        for currency in balance['total']:
            total_balance = balance['total'][currency]
            free_balance = balance['free'][currency]
            used_balance = balance['used'][currency]
            if total_balance > 0:
                balance_data['Currency'].append(currency)
                balance_data['Total Balance'].append(total_balance)
                balance_data['Free Balance'].append(free_balance)
                balance_data['Used Balance'].append(used_balance)

        balance_df = pd.DataFrame(balance_data)
        print("계좌 잔고 (DataFrame):")
        print(balance_df)

    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_account_balance()
