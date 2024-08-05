# Binance

## 실행

### Api

-   일캔들 받기 : api/binance/binance_daily_candles.py

### Backtest

-   이동평균 백테스트 : backtest/bianace/daily_average_backtest.py
-   평균 이동평균 백테스트 : backtest/bianace/ma_average_backtest.py
-   골든크로스 백테스트 : backtest/bianace/golden_cross_backtest.py

### Strategy

-   40일 이동평균 매매 : strategies/binance/daily_SMA_startegy.py

---

## 메모

---

### API

https://binance-docs.github.io/apidocs/spot/en/#general-info

periods = [5, 40, 50, 120, 200]
periods = [5, 20, 50, 120, 200]
