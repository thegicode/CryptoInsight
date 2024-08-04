import pandas as pd
import numpy as np
import os

# 데이터 로드
def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Open Time', 'Close Time'])
    df['Close'] = df['Close'].astype(float)  # 데이터 타입 보정
    return df

# 이동 평균 계산
def calculate_moving_average(df, window):
    df[f'{window}MA'] = df['Close'].rolling(window=window).mean()

# 매매 전략 시뮬레이션
def simulate_trading(df, window, initial_capital=10000, fee_rate=0.001):
    ma_column = f'{window}MA'
    in_position = False
    trades = []
    capital = initial_capital
    quantity = 0

    for i in range(1, len(df)):
        if df['Close'][i] > df[ma_column][i] and df['Close'][i-1] <= df[ma_column][i-1] and not in_position:
            # 매수: 전체 자본금으로 매수
            buy_price = df['Close'][i] * (1 + fee_rate)  # 매수 시 수수료 적용
            quantity = capital / buy_price  # 매수 수량 결정
            capital -= buy_price * quantity
            in_position = True
            trades.append(('buy', df['Close Time'][i], buy_price, capital, quantity))

        elif df['Close'][i] < df[ma_column][i] and df['Close'][i-1] >= df[ma_column][i-1] and in_position:
            # 매도: 전체 수량 매도
            sell_price = df['Close'][i] * (1 - fee_rate)  # 매도 시 수수료 적용
            profit = (sell_price - buy_price) * quantity
            capital += sell_price * quantity  # 매도 후 자본금 추가
            in_position = False
            trades.append(('sell', df['Close Time'][i], sell_price, capital, profit))

    return trades

# 성과 지표 계산
def calculate_performance(trades, window, initial_capital=10000):
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
def save_trades_to_file(trades, window, result_dir):
    if not trades:
        return

    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, f'trades_{window}MA.csv')

    # Create DataFrame from trades
    trades_df = pd.DataFrame(trades, columns=['Action', 'Time', 'Price', 'Capital', 'Quantity'])

    # Save to CSV
    trades_df.to_csv(file_path, index=False)
    print(f"Trades for {window}MA saved to {file_path}")

# 성과 결과 저장
def save_performance_to_file(performance_df, result_dir):
    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, 'performance_summary.csv')

    # Save to CSV
    performance_df.to_csv(file_path, index=False)
    print(f"Performance summary saved to {file_path}")

# 백테스트 실행
def run_backtest(file_path, initial_capital):
    df = load_data(file_path)
    results = []
    result_dir = 'results/binance/trades/daily_SMA/'

    # Get the first and last date in the dataset
    first_date = df['Open Time'].iloc[0].strftime('%Y-%m-%d')
    last_date = df['Open Time'].iloc[-1].strftime('%Y-%m-%d')

    for window in [5, 10, 20, 50, 100, 200]:
        calculate_moving_average(df, window)
        trades = simulate_trading(df, window, initial_capital)
        performance = calculate_performance(trades, window, initial_capital)
        performance['First Date'] = first_date
        performance['Last Date'] = last_date
        results.append(performance)

        # Save each window's trades to file
        save_trades_to_file(trades, window, result_dir)

    # Save performance summary to file
    performance_df = pd.DataFrame(results)
    save_performance_to_file(performance_df, result_dir)
    return results

# 파일 경로, 초기값
file_path = 'data/binance/daily_candles_BTCUSDT.csv'
initial_capital = 10000

# 결과 출력 및 저장
backtest_results = run_backtest(file_path, initial_capital)
results_df = pd.DataFrame(backtest_results)
print(results_df.to_string(index=False))