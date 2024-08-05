import pandas as pd
import numpy as np
import os

def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Open Time', 'Close Time'])
    df['Close'] = df['Close'].astype(float)
    return df

def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    """MACD와 신호선을 계산합니다."""
    df['EMA_short'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_long'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal Line']

def simulate_trading(df, initial_capital=10000, fee_rate=0.001):
    """MACD 전략에 따른 매매 시뮬레이션을 수행합니다."""
    in_position = False
    trades = []
    capital = initial_capital
    quantity = 0

    for i in range(1, len(df)):
        # 매수 신호: MACD가 신호선을 상향 돌파할 때
        if df['MACD'][i] > df['Signal Line'][i] and df['MACD'][i-1] <= df['Signal Line'][i-1] and not in_position:
            buy_price = df['Close'][i] * (1 + fee_rate)
            quantity = capital / buy_price
            capital -= buy_price * quantity
            in_position = True
            trades.append(('buy', df['Close Time'][i], buy_price, capital, None, None))

        # 매도 신호: MACD가 신호선을 하향 돌파할 때
        elif df['MACD'][i] < df['Signal Line'][i] and df['MACD'][i-1] >= df['Signal Line'][i-1] and in_position:
            sell_price = df['Close'][i] * (1 - fee_rate)
            profit = (sell_price - buy_price) * quantity
            rate_of_return = (profit / (buy_price * quantity)) * 100
            capital += sell_price * quantity
            in_position = False
            trades.append(('sell', df['Close Time'][i], sell_price, capital, profit, rate_of_return))

    return trades

def calculate_performance(trades, initial_capital=10000):
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
            peak = max(peak, trade[3])
        elif trade[0] == 'sell':
            drawdown = (peak - trade[3]) / peak if peak != 0 else 0
            drawdown = max(drawdown, 0)
            drawdowns.append(drawdown)

    max_drawdown = (max(drawdowns) * 100) if drawdowns else 0

    return {
        'Total Trades': len(profits),
        'Total Return (%)': percent_return,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown
    }

def save_trades_to_file(trades, result_dir):
    if not trades:
        return

    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, 'trades_macd.csv')

    trades_df = pd.DataFrame(trades, columns=['Action', 'Time', 'Price', 'Capital', 'Profit', 'Rate of Return (%)'])
    trades_df.to_csv(file_path, index=False)
    print(f"Trades saved to {file_path}")

def save_performance_to_file(performance, result_dir):
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, 'macd_backtest.csv')

    performance_df = pd.DataFrame([performance])
    performance_df.to_csv(file_path, index=False)
    print(f"Performance summary saved to {file_path}")

def run_backtest(file_path, initial_capital):
    df = load_data(file_path)
    result_dir = 'results/binance/trades/macd_strategy/'

    # MACD 계산
    calculate_macd(df)

    # 거래 시뮬레이션 실행
    trades = simulate_trading(df, initial_capital)
    performance = calculate_performance(trades, initial_capital)

    # 거래 및 성과 저장
    save_trades_to_file(trades, result_dir)
    save_performance_to_file(performance, result_dir)

    return performance

# 파일 경로, 초기값
file_path = 'data/binance/daily_candles_BTCUSDT.csv'
initial_capital = 10000

# 결과 출력 및 저장
backtest_results = run_backtest(file_path, initial_capital)
print(pd.DataFrame([backtest_results]).to_string(index=False))
