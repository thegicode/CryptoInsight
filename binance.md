# Binance

## 실행

-   일캔들 받기 : api/binance/binance_daily_candles.py
-   이동평균 백테스트 : backtest/bianace/daily_average_backtest.py
-   골든크로스 백테스트 : backtest/bianace/golden_cross_backtest.py

## 메모

5, 20일 이동평균선으로
골든 크로스 매수
데드 크로스 매도

매수 신호시 자금 100% 투입
매도 신호시 100% 매도

파일 경로, 초기값
file_path = 'data/binance/daily_candles_BTCUSDT.csv'
initial_capital = 10000

결과 출력
Window,Total Trades,Total Return (%),Win Rate (%),Max Drawdown (%)

'results/binance/trades/golden_cross/5_20.csv'
