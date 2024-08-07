import pandas as pd
import numpy as np
import os

def calculate_moving_averages(data, periods):
    """여러 기간에 대한 이동평균선을 계산합니다."""
    for period in periods:
        data[f'MA_{period}'] = data['close'].rolling(window=period).mean()
    return data

def assign_scores(data, periods):
    """각 이동평균선에 대해 점수를 부여합니다."""
    data['score'] = 0
    for period in periods:
        ma_column = f'MA_{period}'
        data['score'] += np.where(data['close'] > data[ma_column], 0.2, 0)
    return data

def backtest_strategy(data, periods):
    """백테스팅 전략을 실행하고, 거래 데이터를 수집합니다."""
    data['investment_ratio'] = data['score']  # 투자 비중은 점수와 동일
    initial_balance = 10000  # 초기 자본
    current_balance = initial_balance  # 현재 자본
    trades = 0
    wins = 0
    drawdowns = []
    trade_records = []
    position_open_price = None
    position_open_balance = None
    investment_amount = 0

    balance_history = [current_balance] * len(data)  # 초기화된 자본 기록

    for i in range(1, len(data)):
        previous_balance = current_balance
        current_return = (data['close'].iloc[i] - data['close'].iloc[i-1]) / data['close'].iloc[i-1]
        current_investment = previous_balance * data['investment_ratio'].iloc[i]

        # 매수 신호에서 매수 포지션을 설정합니다.
        if data['investment_ratio'].iloc[i] > 0 and data['investment_ratio'].iloc[i-1] == 0:
            trades += 1  # 거래 발생
            action = 'buy'
            position_open_price = data['close'].iloc[i]
            position_open_balance = previous_balance
            investment_amount = position_open_balance * data['investment_ratio'].iloc[i]  # 투자 금액 계산
            moving_averages_broken = [f'MA_{period}' for period in periods if data['close'].iloc[i] > data[f'MA_{period}'].iloc[i]]
            trade_records.append({
                'Action': action,
                'Time': data.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                'Price': data['close'].iloc[i],
                'Capital': position_open_balance,
                'Investment Amount': investment_amount,
                'Profit': '',
                'Rate of Return (%)': '',
                'Broken MAs': ', '.join(moving_averages_broken),
                'Score': data['score'].iloc[i]
            })

        # 매도 신호에서 수익과 수익률을 계산합니다.
        elif data['investment_ratio'].iloc[i] == 0 and data['investment_ratio'].iloc[i-1] > 0:
            trades += 1  # 거래 발생
            action = 'sell'
            profit = (data['close'].iloc[i] - position_open_price) * (investment_amount / position_open_price)
            rate_of_return = (profit / investment_amount) * 100
            current_balance = position_open_balance + profit  # 수익을 새 밸런스에 반영
            balance_history[i] = current_balance  # 매도 시점의 자본 기록
            moving_averages_broken = [f'MA_{period}' for period in periods if data['close'].iloc[i] < data[f'MA_{period}'].iloc[i]]
            trade_records.append({
                'Action': action,
                'Time': data.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                'Price': data['close'].iloc[i],
                'Capital': current_balance,
                'Investment Amount': investment_amount,
                'Profit': profit,
                'Rate of Return (%)': rate_of_return,
                'Broken MAs': ', '.join(moving_averages_broken),
                'Score': data['score'].iloc[i]
            })
            if profit > 0:
                wins += 1

        # 최대 손실률 계산
        peak = max(balance_history[:i+1])  # 현재 시점까지의 최고점에서 감소율을 계산
        drawdown = (peak - current_balance) / peak * 100
        drawdowns.append(drawdown)

    data['balance'] = balance_history
    total_return = ((current_balance - initial_balance) / initial_balance) * 100
    win_rate = (wins / trades * 100) if trades > 0 else 0
    max_drawdown = max(drawdowns)

    return trades, total_return, win_rate, max_drawdown, trade_records

def run_backtest(file_path, periods, initial_capital):
    """주어진 기간으로 백테스트를 실행하고 결과를 반환합니다."""
    # CSV 파일에서 데이터 가져오기
    data = pd.read_csv(file_path, parse_dates=['Open Time'], usecols=['Open Time', 'Close'])
    data.rename(columns={'Open Time': 'timestamp', 'Close': 'close'}, inplace=True)
    data.set_index('timestamp', inplace=True)

    # 이동평균선 및 점수 계산
    data = calculate_moving_averages(data, periods)
    data = assign_scores(data, periods)

    # 전략 백테스트 및 거래 데이터 수집
    trades, total_return, win_rate, max_drawdown, trade_records = backtest_strategy(data, periods)

    return {
        'Periods': str(periods),
        'Total Trades': trades,
        'Total Return (%)': total_return,
        'Win Rate (%)': win_rate,
        'Max Drawdown (%)': max_drawdown,
        'First Date': data.index[0].strftime('%Y-%m-%d'),
        'Last Date': data.index[-1].strftime('%Y-%m-%d'),
        'Trade Records': trade_records
    }

def save_trade_records(trade_records, output_dir, symbol, periods):
    """거래 데이터를 CSV 파일로 저장합니다."""
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f'trade_records_{symbol}_{",".join(map(str, periods))}.csv')
    df = pd.DataFrame(trade_records)
    df.to_csv(file_path, index=False)
    print(f"Trade records saved to {file_path}")

def ma_average_backtest(symbols=None, initial_capital = 10000):
    """주요 실행 로직"""
    # 설정
    if symbols is None:
        symbols = ['BTCUSDT', 'SOLUSDT']  # 심볼 리스트
    initial_capital = 10000  # 초기 자본
    output_dir_base = 'results/binance/trades/ma_average/'  # 결과 저장 경로 기본값

    # 여러 기간 세트에 대해 백테스트 실행
    periods_sets = [
        [5, 20, 60, 120, 200],
        [5, 40, 50, 120, 200],
        [10, 40, 50, 120, 200],
        [10, 20, 50, 120, 200],
        [10, 20, 50, 100, 200],
    ]

    # 각 심볼 및 세트에 대해 백테스트 실행 및 결과 저장
    for symbol in symbols:
        backtest_results = []
        output_dir = os.path.join(output_dir_base, symbol)  # 각 심볼에 대해 별도의 디렉토리 생성

        for periods in periods_sets:
            print(f"Running backtest for {symbol} with periods: {periods}")
            file_path = f'data/binance/daily_candles_{symbol}.csv'
            result = run_backtest(file_path, periods, initial_capital)
            backtest_results.append(result)

            # 거래 기록 저장
            save_trade_records(result['Trade Records'], output_dir, symbol, periods)

        # 백테스트 결과 DataFrame으로 변환 및 출력
        results_df = pd.DataFrame(backtest_results)
        print(f"\nBacktest Summary Results for {symbol}:")
        print(results_df.drop(columns=['Trade Records']).to_string(index=False))

        # 백테스트 요약 결과 저장
        summary_file_path = os.path.join(output_dir, f'ma_average_backtest_{symbol}.csv')
        results_df.drop(columns=['Trade Records']).to_csv(summary_file_path, index=False)
        print(f"Backtest summary saved to {summary_file_path}")

if __name__ == "__main__":
    ma_average_backtest()
