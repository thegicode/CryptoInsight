from utils.backtest_metrics import calculate_cumulative_return, calculate_mdd, calculate_win_rate
import sys
import os
import pytest
import pandas as pd
import numpy as np

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


def test_calculate_cumulative_return():
    data = {'total': [10000, 10500, 11000, 11500, 12000]}
    df = pd.DataFrame(data)
    initial_capital = 10000

    result = calculate_cumulative_return(df, initial_capital)
    expected_result = 20.0  # ((12000 / 10000) - 1) * 100

    # print(f"Cumulative Return: {result}%")  # 중간 결과 출력

    # 오차 범위를 1e-6으로 설정
    assert np.isclose(result, expected_result, atol=1e-6)


def test_calculate_mdd():
    data = {'total': [10000, 9500, 10500, 9000, 11000]}
    df = pd.DataFrame(data)

    result = calculate_mdd(df)
    expected_result = -14.285714285714286  # ((9000 / 10500) - 1) * 100
    # 실제 최저점은 9000이므로, 피크인 10500과 비교해야 함

    print(f"Max Drawdown : {result}%")  # 중간 결과 출력

    # 오차 범위를 1e-6으로 설정
    assert np.isclose(result, expected_result, atol=1e-6)


def test_calculate_win_rate():
    data = {
        'positions': [0, 1, 0, -1, 0, 1, 0, -1],
        'total': [10000, 10500, 10500, 11000, 11000, 11500, 11500, 12000]
    }
    df = pd.DataFrame(data)

    result = calculate_win_rate(df)
    expected_result = 100.0  # All trades are winning trades in this example

    print(f"Win Rate: {result}%")  # 중간 결과 출력

    # 오차 범위를 1e-6으로 설정
    assert np.isclose(result, expected_result, atol=1e-6)


if __name__ == "__main__":
    pytest.main(['-s'])
