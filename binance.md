# Binance

## 실행

### Api

-   일캔들 받기 : api/binance/binance_daily_candles.py
-   분캔들 받기 : api/binance/binance_minutes_candles.py

-   내 계좌 잔고 : api/binance/binance_account.py
-   거래 내역 : api/binance/binance_my_trades.py
-   미체결 주문 : api/binance/binance_open_orders.py

-   주문 : api/binance/binance_buy_order.py
-   주문 취소 : api/binance/binance_cancel_order.py
-   주문 정보 : api/binance/binance_fetch_oder.py

-   hepers: api/binance/binance_api_helpers.py

### Backtest

-   이동평균 백테스트 : backtest/bianace/daily_average_backtest.py
-   평균 이동평균 백테스트 : backtest/bianace/ma_average_backtest.py
-   골든크로스 백테스트 : backtest/bianace/golden_cross_backtest.py
-   이동평균 강화 백테스트 : backtest/bianace/daily_enhanced.py

### Strategy

-   40일 이동평균 매매 : strategies/binance/daily_SMA_startegy.py

---

## 메모

-   backtest 자동으로 개선
-   듀얼모멘텀 완성

---

## 미완성

-   backtest/bianace/bollinger_band_backtest.py
-   strategies/binance/bollinger_strategy.py

---

### API

https://binance-docs.github.io/apidocs/spot/en/#general-info

periods = [5, 40, 50, 120, 200]
periods = [5, 20, 50, 120, 200]
