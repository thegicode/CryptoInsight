from scripts.daily_average_signals import calculate_moving_average, generate_signals, check_signals

import sys
import os
import pytest
import pandas as pd
import numpy as np

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def test_calculate_moving_average():
    data = {'close': [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)
    df = calculate_moving_average(df, window=5)

    expected_moving_avg = [10.0, 15.0, 20.0, 25.0, 30.0]
    assert df['moving_avg'].tolist() == expected_moving_avg


def test_generate_signals():
    data = {'close': [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)
    df = calculate_moving_average(df, window=5)
    df = generate_signals(df)

    expected_signals = [0, 1, 1, 1, 1]
    expected_positions = [np.nan, 1.0, 0.0, 0.0, 0.0]

    assert df['signal'].tolist() == expected_signals
    np.testing.assert_array_equal(df['positions'].tolist(), expected_positions)


@pytest.mark.asyncio
async def test_check_signals():
    market = 'KRW-BTC'
    count = 10
    window = 5

    message = await check_signals(market, count, window)

    assert market in message
    assert 'signal' in message

if __name__ == "__main__":
    pytest.main(['-s'])
