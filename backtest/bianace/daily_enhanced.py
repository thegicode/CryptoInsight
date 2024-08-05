import pandas as pd
import numpy as np
import os

# 데이터 로드
def load_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Open Time', 'Close Time'])
    df['Close'] = df['Close'].astype(float)  # 데이터 타입 보정
    df['Volume'] = df['Volume'].astype(float)  # 거래량 데이터 타입 보정
    return df

# 이동 평균 계산
def calculate_moving_average(df, window):
    df[f'{window}MA'] = df['Close'].rolling(window=window).mean()

# 매매 전략 시뮬레이션
def simulate_moving_average_trading(df, window=40, initial_capital=1000000, fee_rate=0.001):
    ma_column = f'{window}MA'
    in_position = False
    trades = []
    capital = initial_capital
    quantity = 0
    investment = 0  # 투자금 변수 추가

    for i in range(1, len(df)):
        # 40일 이동평균선 전략 매수 (잔액 전액 매수)
        if df['Close'][i] > df[ma_column][i] and df['Close'][i-1] <= df[ma_column][i-1] and not in_position:
            # 매수: 가격이 40일 이동평균선을 상향 돌파할 때 잔액 전액 매수
            buy_price = df['Close'][i] * (1 + fee_rate)
            buy_quantity = capital / buy_price
            investment = capital  # 투자금 = 현재 자본금
            capital -= buy_price * buy_quantity
            quantity += buy_quantity
            trades.append(('buy', df['Close Time'][i], buy_price, capital, investment, None, None, df[ma_column][i]))
            in_position = True

        # 상승장에서 추가 매수 (40일 조건에 들지 않았을 때만)
        elif not in_position and df['Close'][i] > df['Close'][i-1] and df['Volume'][i] > df['Volume'][i-1]:
            # 추가 매수: 상승장(가격과 거래량이 증가)일 때 남은 자본금의 1%만큼 매수
            additional_investment_amount = capital * 0.01  # 남은 자본금의 1%
            additional_buy_price = df['Close'][i] * (1 + fee_rate)
            if capital >= additional_investment_amount:
                additional_quantity = additional_investment_amount / additional_buy_price
                investment += additional_investment_amount  # 추가 매수에 따른 투자금 증가
                capital -= additional_buy_price * additional_quantity
                quantity += additional_quantity
                trades.append(('additional_buy', df['Close Time'][i], additional_buy_price, capital, investment, None, None, df[ma_column][i]))

        # 40일 이동평균선 전략 매도
        elif df['Close'][i] < df[ma_column][i] and df['Close'][i-1] >= df[ma_column][i-1] and in_position:
            # 매도: 가격이 40일 이동평균선을 하향 돌파할 때 모든 보유량 매도
            sell_price = df['Close'][i] * (1 - fee_rate)
            profit = (sell_price * quantity) - investment
            rate_of_return = (profit / investment) * 100  # 수익률 = 투자금 대비 수익률
            capital += sell_price * quantity
            in_position = False
            trades.append(('sell', df['Close Time'][i], sell_price, capital, investment, profit, rate_of_return, df[ma_column][i]))

            # 보유량 및 투자금 초기화
            quantity = 0
            investment = 0

    return trades

# 성과 지표 계산
def calculate_performance(trades, initial_capital=1000000):
    if not trades:
        return {}

    profits = [trade[5] for trade in trades if trade[0] == 'sell']
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
        'Total Trades': len(profits),
        'Total Return (%)': percent_return,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown
    }

# 거래 데이터 저장
def save_trades_to_file(trades, result_dir):
    if not trades:
        return

    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, 'daily_enhanced_trade.csv')  # 파일명 변경

    # Create DataFrame from trades
    trades_df = pd.DataFrame(trades, columns=['Action', 'Time', 'Price', 'Capital', 'Investment', 'Profit', 'Rate of Return (%)', '40_MA'])

    # Save to CSV
    trades_df.to_csv(file_path, index=False)
    print(f"Trades saved to {file_path}")

# 성과 결과 저장
def save_performance_to_file(performance_df, result_dir):
    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, 'daily_enhanced.csv')  # 파일명 변경

    # Save to CSV
    performance_df.to_csv(file_path, index=False)
    print(f"Performance summary saved to {file_path}")

# 백테스트 실행
def run_backtest(file_path, initial_capital):
    df = load_data(file_path)
    results = []
    result_dir = 'results/binance/trades/daily_enhanced/'

    # 40일 이동평균선 계산
    calculate_moving_average(df, 40)

    # 매매 전략 실행
    trades = simulate_moving_average_trading(df, 40, initial_capital)
    performance = calculate_performance(trades, initial_capital)

    # 데이터셋의 첫 번째 및 마지막 날짜
    first_date = df['Open Time'].iloc[0].strftime('%Y-%m-%d')
    last_date = df['Open Time'].iloc[-1].strftime('%Y-%m-%d')

    performance['First Date'] = first_date
    performance['Last Date'] = last_date
    results.append(performance)

    # 거래 결과 저장
    save_trades_to_file(trades, result_dir)

    # 성과 결과 저장
    performance_df = pd.DataFrame(results)
    save_performance_to_file(performance_df, result_dir)
    return results

# 파일 경로, 초기값
file_path = 'data/binance/daily_candles_BTCUSDT.csv'
initial_capital = 1000000  # 초기 자본금 100만원

# 결과 출력 및 저장
backtest_results = run_backtest(file_path, initial_capital)
results_df = pd.DataFrame(backtest_results)
print(results_df.to_string(index=False))
