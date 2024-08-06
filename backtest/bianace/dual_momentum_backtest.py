import pandas as pd
import numpy as np
import ccxt  # 암호화폐 거래소 라이브러리
import os
from datetime import datetime, timedelta

def fetch_market_data(exchange, symbol, start_date, end_date, interval='1d'):
    """거래소에서 주어진 심볼의 과거 데이터를 가져옵니다."""
    since = exchange.parse8601(start_date)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=interval, since=since, limit=1000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df.loc[start_date:end_date]

def get_top_market_cap_symbols(exchange, exclude_symbols=set(), limit=20):
    """시가총액 상위 코인 목록을 반환합니다."""
    tickers = exchange.fetch_tickers()
    # 시가총액 추정치를 위해 거래량을 사용하여 정렬
    sorted_tickers = sorted(
        [ticker for ticker in tickers.values() if ticker['symbol'] not in exclude_symbols and '/USDT' in ticker['symbol']],
        key=lambda x: x['quoteVolume'],
        reverse=True
    )
    top_symbols = [ticker['symbol'] for ticker in sorted_tickers[:limit]]

    return top_symbols

def calculate_moving_average(df, window):
    """이동평균선을 계산합니다."""
    return df['close'].rolling(window=window).mean()

def calculate_weekly_return(df):
    """주간 수익률을 계산합니다."""
    if len(df) >= 7:
        df['weekly_return'] = df['close'].pct_change(periods=7)
    else:
        df['weekly_return'] = 0
    return df

def is_investment_allowed(btc_df, window=120):
    """비트코인의 이동평균선을 기준으로 투자 허용 여부를 확인합니다."""
    moving_average = calculate_moving_average(btc_df, window).iloc[-1]
    current_price = btc_df['close'].iloc[-1]
    return current_price > moving_average

def select_top_cryptos(crypto_data, n=3):
    """주간 수익률 기준 상위 N개의 암호화폐를 선택합니다."""
    weekly_returns = {symbol: df['weekly_return'].iloc[-1] for symbol, df in crypto_data.items() if not df.empty and 'weekly_return' in df.columns}
    sorted_cryptos = sorted(weekly_returns.items(), key=lambda x: x[1], reverse=True)
    top_cryptos = [crypto for crypto, return_ in sorted_cryptos if return_ > 0][:n]
    print(f"선택된 상위 {n} 암호화폐: {top_cryptos}")
    return top_cryptos


def simulate_backtest(start_date, end_date, exchange, initial_capital):
    """백테스트 시뮬레이션을 실행합니다."""
    capital = initial_capital
    portfolio_value = initial_capital
    portfolio = {}

    # 비트코인 데이터 가져오기
    btc_data = fetch_market_data(exchange, 'BTC/USDT', start_date, end_date)
    btc_data = calculate_weekly_return(btc_data)

    # 주간 반복
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    trades = 0
    wins = 0
    drawdowns = []
    max_drawdown = 0

    # 포트폴리오 가치 기록 및 거래 내역 저장
    portfolio_values = []
    trade_records = []

    while current_date < end_date:
        # 매주 상위 20개 코인 중 상위 3개 선택
        exclude_symbols = {'USDT', 'BUSD', 'USDC'}
        top_symbols = get_top_market_cap_symbols(exchange, exclude_symbols)
        weekly_data = {}
        for symbol in top_symbols:
            weekly_df = fetch_market_data(exchange, symbol, current_date.strftime('%Y-%m-%d'), (current_date + timedelta(days=7)).strftime('%Y-%m-%d'))
            if not weekly_df.empty:
                weekly_data[symbol] = calculate_weekly_return(weekly_df)

        start_portfolio_value = portfolio_value  # 주간 시작 포트폴리오 가치 저장
        # 투자 허용 여부 확인
        if not is_investment_allowed(btc_data.loc[:current_date]):
            # 투자 중단 및 현금 보유
            portfolio.clear()
        else:
            # 상위 3개의 암호화폐 선택
            selected_cryptos = select_top_cryptos({k: v for k, v in weekly_data.items() if not v.empty})
            if selected_cryptos:
                # 선택된 암호화폐에 자본을 균등 분배
                investment_per_crypto = capital / len(selected_cryptos)
                portfolio.clear()
                for crypto in selected_cryptos:
                    last_price = weekly_data[crypto].iloc[-1]['close']
                    quantity = investment_per_crypto / last_price
                    portfolio[crypto] = (quantity, last_price)
                    trades += 1
                    trade_records.append({
                        'Week Start': current_date.strftime('%Y-%m-%d'),
                        'Crypto': crypto,
                        'Action': 'buy',
                        'Price': last_price,
                        'Investment Amount': investment_per_crypto,
                        'Quantity': quantity,
                        'Rate of Return (%)': ((last_price * quantity - investment_per_crypto) / investment_per_crypto) * 100
                    })

        # 주말에 포트폴리오 가치 계산
        if portfolio:
            portfolio_value = sum(quantity * weekly_data[crypto].iloc[-1]['close'] for crypto, (quantity, _) in portfolio.items())
            capital = portfolio_value
            weekly_return = ((portfolio_value - start_portfolio_value) / start_portfolio_value) * 100 if start_portfolio_value > 0 else 0
            if weekly_return > 0:
                wins += 1

        # 최대 손실률 계산
        portfolio_values.append(portfolio_value)
        peak = max(portfolio_values)
        drawdown = (peak - portfolio_value) / peak * 100 if peak > 0 else 0
        drawdowns.append(drawdown)
        max_drawdown = max(max_drawdown, drawdown)

        # 다음 주로 이동
        current_date += timedelta(days=7)

    # 총 수익률 계산
    total_return = ((portfolio_value - initial_capital) / initial_capital) * 100
    win_rate = (wins / trades * 100) if trades > 0 else 0

    return {
        'Total Trades': trades,
        'Total Return (%)': total_return,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown,
        'First Date': start_date,
        'Last Date': end_date,
        'Trade Records': trade_records
    }

def save_trade_records(trade_records, file_path):
    """거래 기록을 CSV 파일로 저장합니다."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df = pd.DataFrame(trade_records)
    df.to_csv(file_path, index=False)
    print(f"Trade records saved to {file_path}")

def main():
    """주요 실행 로직"""
    # 설정
    initial_capital = 10000
    start_date = '2023-01-01'
    end_date = '2024-08-31'

    # 거래소 초기화
    exchange = ccxt.binance()

    # 백테스트 실행
    backtest_results = simulate_backtest(start_date, end_date, exchange, initial_capital)

    # 결과 출력
    results_df = pd.DataFrame([backtest_results])
    print("\nBacktest Summary Results:")
    print(results_df.drop(columns=['Trade Records']).to_string(index=False))

    # 거래 내역 저장
    save_trade_records(backtest_results['Trade Records'], 'results/binance/trades/dual_momentum.csv')

if __name__ == "__main__":
    main()
