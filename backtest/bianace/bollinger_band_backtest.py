# 미완성

import pandas as pd
import numpy as np
import os

# 데이터 로드
def load_data(file_path):
    """파일에서 데이터를 로드합니다."""
    df = pd.read_csv(file_path, parse_dates=['Open Time', 'Close Time'])
    df['Close'] = df['Close'].astype(float)  # 데이터 타입 보정
    return df

# Bollinger Bands 계산
def calculate_bollinger_bands(df, window, num_std_dev):
    """볼린저 밴드를 계산하여 데이터프레임에 추가합니다."""
    df['Middle Band'] = df['Close'].rolling(window=window).mean()
    df['Std Dev'] = df['Close'].rolling(window=window).std()
    df['Upper Band'] = df['Middle Band'] + (df['Std Dev'] * num_std_dev)
    df['Lower Band'] = df['Middle Band'] - (df['Std Dev'] * num_std_dev)

# 매매 전략 시뮬레이션
def simulate_bollinger_trading(df, window, num_std_dev, initial_capital=10000, fee_rate=0.001):
    """볼린저 밴드 기반의 매매 전략을 시뮬레이션합니다."""
    in_position = False
    trades = []
    capital = initial_capital
    quantity = 0

    for i in range(1, len(df)):
        if df['Close'][i] > df['Lower Band'][i] and df['Close'][i-1] <= df['Lower Band'][i-1] and not in_position:
            # 매수: 전체 자본금으로 매수
            buy_price = df['Close'][i] * (1 + fee_rate)  # 매수 시 수수료 적용
            quantity = capital / buy_price  # 매수 수량 결정
            capital -= buy_price * quantity
            in_position = True
            trades.append(('buy', df['Close Time'][i], buy_price, capital, None, None))  # profit과 rate 없음

        elif df['Close'][i] < df['Upper Band'][i] and df['Close'][i-1] >= df['Upper Band'][i-1] and in_position:
            # 매도: 전체 수량 매도
            sell_price = df['Close'][i] * (1 - fee_rate)  # 매도 시 수수료 적용
            profit = (sell_price - buy_price) * quantity
            rate_of_return = (profit / (buy_price * quantity)) * 100  # 수익률 계산
            capital += sell_price * quantity  # 매도 후 자본금 추가
            in_position = False
            trades.append(('sell', df['Close Time'][i], sell_price, capital, profit, rate_of_return))

    return trades

# 성과 지표 계산
def calculate_performance(trades, window, initial_capital=10000):
    """매매 전략의 성과 지표를 계산합니다."""
    if not trades:
        return {}

    profits = [trade[4] for trade in trades if trade[0] == 'sell']
    total_returns = sum(profits)
    percent_return = (total_returns / initial_capital) * 100
    win_rate = (len([p for p in profits if p > 0]) / len(profits)) * 100 if profits else 0
    drawdowns = []
    peak = initial_capital
    for trade in trades:
        if trade[0] == 'buy':
            peak = max(peak, trade[3])  # capital after buy
        elif trade[0] == 'sell':
            drawdown = (peak - trade[3]) / peak if peak != 0 else 0  # capital after sell
            drawdown = max(drawdown, 0)  # Ensure drawdown is non-negative
            drawdowns.append(drawdown)

    max_drawdown = (max(drawdowns) * 100) if drawdowns else 0

    return {
        'Window': window,
        'Total Trades': len(profits),
        'Total Return (%)': percent_return,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown
    }

# 거래 데이터 저장
def save_trades_to_file(trades, window, result_path):
    """거래 데이터를 CSV 파일로 저장합니다."""
    if not trades:
        return

    # Ensure the result directory exists
    os.makedirs(os.path.dirname(result_path), exist_ok=True)

    # Create DataFrame from trades
    trades_df = pd.DataFrame(trades, columns=['Action', 'Time', 'Price', 'Capital', 'Profit', 'Rate of Return (%)'])

    # Save to CSV
    trades_df.to_csv(result_path, index=False)
    print(f"Trades saved to {result_path}")

# 성과 결과 저장
def save_performance_to_file(performance, result_path):
    """성과 결과를 CSV 파일로 저장합니다."""
    performance_df = pd.DataFrame([performance])
    performance_file_path = result_path.replace('.csv', '_performance.csv')

    # Save to CSV
    performance_df.to_csv(performance_file_path, index=False)
    print(f"Performance summary saved to {performance_file_path}")

# 백테스트 실행
def run_bollinger_backtest(market_name, interval, initial_capital, window, num_std_dev):
    """볼린저 밴드 기반 백테스트를 실행합니다."""
    file_path = f'data/binance/{interval}_candles_{market_name}.csv'
    result_path = f'results/binance/trades/bollinger_band/bollinger_SOLUSDT_4h_trade.csv'

    # Load data
    df = load_data(file_path)

    # Calculate Bollinger Bands
    calculate_bollinger_bands(df, window, num_std_dev)

    # Simulate trading
    trades = simulate_bollinger_trading(df, window, num_std_dev, initial_capital)

    # Calculate performance
    performance = calculate_performance(trades, window, initial_capital)

    # Save trades and performance to file
    save_trades_to_file(trades, window, result_path)
    save_performance_to_file(performance, result_path)

    # Output results
    print("\nBacktest Results:")
    print(pd.DataFrame([performance]).to_string(index=False))

if __name__ == "__main__":
    # Example usage
    run_bollinger_backtest(market_name='SOLUSDT', interval='4h', initial_capital=10000, window=20, num_std_dev=2)
