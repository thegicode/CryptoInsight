import pandas as pd
import numpy as np
import os

def load_data(file_path):
    """CSV 파일에서 데이터 로드"""
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
    """거래 기록으로부터 성과 지표를 계산합니다."""
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

def save_trades_to_file(trades, result_dir, symbol):
    """거래 데이터를 CSV 파일로 저장합니다."""
    if not trades:
        return

    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, f'trades_macd_{symbol}.csv')

    trades_df = pd.DataFrame(trades, columns=['Action', 'Time', 'Price', 'Capital', 'Profit', 'Rate of Return (%)'])
    trades_df.to_csv(file_path, index=False)
    print(f"Trades for {symbol} saved to {file_path}")

def save_performance_to_file(performance, result_dir, symbol):
    """성과 데이터를 CSV 파일로 저장합니다."""
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, f'macd_backtest_{symbol}.csv')

    performance_df = pd.DataFrame([performance])
    performance_df.to_csv(file_path, index=False)
    print(f"Performance summary for {symbol} saved to {file_path}")

def run_backtest(symbols, initial_capital):
    """백테스트를 여러 심볼에 대해 실행하고 결과를 반환합니다."""
    results = []
    for symbol in symbols:
        file_path = f'data/binance/daily_candles_{symbol}.csv'
        df = load_data(file_path)
        result_dir = f'results/binance/trades/macd_strategy/{symbol}/'

        # MACD 계산
        calculate_macd(df)

        # 거래 시뮬레이션 실행
        trades = simulate_trading(df, initial_capital)
        performance = calculate_performance(trades, initial_capital)

        # 거래 및 성과 저장
        save_trades_to_file(trades, result_dir, symbol)
        save_performance_to_file(performance, result_dir, symbol)

        performance['Symbol'] = symbol
        results.append(performance)

    return results

# 멀티 심볼 백테스트 실행 예시
symbols = ['BTCUSDT', 'SOLUSDT', 'ETHUSDT', 'XRPUSDT' ,'SHIBUSDT', 'BNBUSDT', 'DOGEUSDT']
backtest_results = run_backtest(symbols, 10000)
results_df = pd.DataFrame(backtest_results)

# 심볼별로 출력 구분
for symbol in symbols:
    symbol_results = results_df[results_df['Symbol'] == symbol]
    print(f"\nMarket: {symbol}")
    print(symbol_results.drop(columns=['Symbol']).to_string(index=False))
