import pandas as pd
import os

# 전략 설명
"""
이 전략은 비트코인 가격을 대상으로 40일 이동평균선을 기준으로 매수 및 매도를 결정하며,
추가 매수는 현재 남은 자본금의 1%로 설정합니다. 다음은 이 전략의 상세 내용입니다:

1. 초기 자본금: 100만원
   - 초기 자본금으로 모든 거래를 시작합니다.

2. 매수 조건:
   - 가격이 40일 이동평균선을 상향 돌파하면, 잔액 전액을 매수합니다.
   - 추가 매수는 상승장에서 가격과 거래량이 모두 증가하는 경우,
     현재 남은 자본금의 1%로 추가 매수를 합니다.

3. 매도 조건:
   - 가격이 40일 이동평균선을 하향 돌파하면, 보유한 모든 자산을 매도합니다.

4. 거래 시간:
   - 주로 높은 유동성과 변동성을 활용하기 위해 UTC 12:00 ~ 20:00 (한국 시간 21:00 ~ 05:00)
     사이에 거래를 집중합니다.
   - 이 시간대는 북미와 유럽 시장이 겹치며, 암호화폐 거래량이 높은 시기입니다.

5. 수수료:
   - 모든 거래에는 0.1%의 수수료가 부과되어 실질적인 거래 비용을 반영합니다.

6. 목표:
   - 이 전략은 상승 추세를 따라가며 하락 위험을 최소화하여 자본을 성장시키는 것을 목표로 합니다.
   - 지속적인 상승장에서의 수익 극대화를 위해 자본금의 일정 비율로 추가 매수를 진행합니다.
"""

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
def simulate_moving_average_trading(df, window, initial_capital=1000000, fee_rate=0.001):
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
def save_trades_to_file(trades, result_dir, symbol):
    if not trades:
        return

    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, f'daily_enhanced_trade_{symbol}.csv')  # 파일명에 심볼 추가

    # Create DataFrame from trades
    trades_df = pd.DataFrame(trades, columns=['Action', 'Time', 'Price', 'Capital', 'Investment', 'Profit', 'Rate of Return (%)', '40_MA'])

    # Save to CSV
    trades_df.to_csv(file_path, index=False)
    print(f"Trades for {symbol} saved to {file_path}")

# 성과 결과 저장
def save_performance_to_file(performance_df, result_dir, symbol):
    # Ensure the result directory exists
    os.makedirs(result_dir, exist_ok=True)
    file_path = os.path.join(result_dir, f'daily_enhanced_{symbol}.csv')  # 파일명에 심볼 추가

    # Save to CSV
    performance_df.to_csv(file_path, index=False)
    print(f"Performance summary for {symbol} saved to {file_path}")

# 백테스트 실행
def run_backtest(symbols_with_windows, initial_capital):
    results = []
    for symbol, window in symbols_with_windows:
        file_path = f'data/binance/daily_candles_{symbol}.csv'
        df = load_data(file_path)
        result_dir = f'results/binance/trades/daily_enhanced_{symbol}/'

        # 사용자 지정 이동평균선 계산
        calculate_moving_average(df, window)

        # 매매 전략 실행
        trades = simulate_moving_average_trading(df, window, initial_capital)
        performance = calculate_performance(trades, initial_capital)

        # 데이터셋의 첫 번째 및 마지막 날짜
        first_date = df['Open Time'].iloc[0].strftime('%Y-%m-%d')
        last_date = df['Open Time'].iloc[-1].strftime('%Y-%m-%d')

        performance['First Date'] = first_date
        performance['Last Date'] = last_date
        performance['Symbol'] = symbol
        results.append(performance)

        # 거래 결과 저장
        save_trades_to_file(trades, result_dir, symbol)

        # 성과 결과 저장
        performance_df = pd.DataFrame([performance])
        save_performance_to_file(performance_df, result_dir, symbol)

    return results

# 백테스트 실행 예시
symbols_with_windows = [('BTCUSDT', 40), ('SOLUSDT', 40), ('ETHUSDT', 5), ('XRPUSDT', 30), ('SHIBUSDT', 30)]
backtest_results = run_backtest(symbols_with_windows, 1000000)
results_df = pd.DataFrame(backtest_results)

# 심볼별로 출력 구분
for symbol, _ in symbols_with_windows:
    symbol_results = results_df[results_df['Symbol'] == symbol]
    print(f"\nMarket: {symbol}")
    print(symbol_results.drop(columns=['Symbol']).to_string(index=False))
