# utils/moving_averages.py

def calculate_short_long_moving_averages(df, short_window=50, long_window=200):
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    return df
