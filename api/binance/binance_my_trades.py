import sys
import os
import ccxt
import pandas as pd

# 프로젝트 루트 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))  # 루트 경로로 설정
sys.path.append(project_root)  # 루트 경로를 sys.path에 추가

from api.binance.binance_api_helpers import create_exchange

def fetch_average_buy_price(symbol='SOL/USDT'):
    """지정된 심볼에 대한 평균 매수 가격을 계산하고 거래 정보를 테이블로 출력합니다."""
    try:
        exchange = create_exchange()

        # 거래 내역 가져오기
        trades = exchange.fetch_my_trades(symbol)
        total_cost = 0
        total_amount = 0

        # 거래 내역 리스트를 만들기 위한 빈 리스트
        trade_list = []

        # 거래 내역을 순회하며 매수 가격과 수량을 합산
        for trade in trades:
            trade_info = {
                'ID': trade['id'],
                'Timestamp': trade['timestamp'],
                'Datetime': trade['datetime'],
                'Symbol': trade['symbol'],
                'Order': trade['order'],
                'Type': trade['type'],
                'Side': trade['side'],
                'Price': trade['price'],
                'Amount': trade['amount'],
                'Cost': trade['cost'],
                'Fee': trade['fee']['cost'] if trade['fee'] else None,
                'Fee Currency': trade['fee']['currency'] if trade['fee'] else None,
                'Taker/Maker': trade['takerOrMaker']
            }
            trade_list.append(trade_info)

            if trade['side'] == 'buy':
                total_cost += trade['price'] * trade['amount']
                total_amount += trade['amount']

        # 평균 매수 가격 계산
        average_buy_price = total_cost / total_amount if total_amount > 0 else 0

        # 거래 정보 테이블 생성
        trades_df = pd.DataFrame(trade_list)
        print("\n거래 정보:")
        print(trades_df.to_string(index=False))

        print(f"\n{symbol}의 평균 매수 가격: {average_buy_price:.2f}")

    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_average_buy_price()
