

from daily_average_enhanced_backtest import daily_average_enhanced
from daily_average_backtest import daily_average_backtest
from golden_cross_backtest import golden_cross_backtest
from ma_average_backtest import ma_average_backtest
from macd_backtest import macd_backtest


# backtest
symbols = ['BTCUSDT', 'SOLUSDT', 'ETHUSDT', 'XRPUSDT', 'SHIBUSDT', 'BNBUSDT', 'DOGEUSDT']
initial_capital = 10000
symbols_with_windows = [('BTCUSDT', 40), ('SOLUSDT', 40), ('ETHUSDT', 5), ('XRPUSDT', 30), ('SHIBUSDT', 30), ('BNBUSDT', 100), ('DOGEUSDT', 40)]

# daily_average_backtest(symbols,initial_capital )
daily_average_enhanced(symbols_with_windows, initial_capital)
# golden_cross_backtest(symbols, initial_capital)
# ma_average_backtest(symbols, initial_capital)
# macd_backtest(symbols, initial_capital)