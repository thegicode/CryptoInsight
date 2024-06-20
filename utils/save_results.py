import os
import pandas as pd


def save_market_backtest_result(market, df, count, name, check_ma=False) :
    """
    시장 백테스트 결과를 CSV 파일로 저장하는 함수.

    :param market: 가상화폐 시장 코드
    :param df: 데이터프레임 (백테스트 결과)
    :param count: 데이터 수
    :param name: 백테스트 이름
    :param check_ma: 이동 평균 확인 여부
    """

    # if (check_ma) :
    #     output_dir = f'results/{name}_checkMA_backtest'
    # else :
    #     output_dir = f'results/{name}_backtest'

    output_dir = f'results/{name}_{"checkMA_" if check_ma else ""}backtest'

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{name}_{market}_{count}.csv')
    df.to_csv(output_file, index=True)


def save_backtest_results(results, count, name):
    """
    백테스트 결과를 저장하는 함수

    :param results: 백테스트 결과 리스트
    :param count: 데이터 개수
    :return: 저장된 결과의 데이터프레임
    """
    results_df = pd.DataFrame(results)

    # MDD 기준으로 정렬
    results_df = results_df.sort_values(by="Max Drawdown (MDD) (%)", ascending=False)

    # 결과를 저장할 디렉터리 생성
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{name}_backtest_{count}.csv')

    # CSV 파일로 저장
    results_df.to_csv(output_file, index=False)
    print(f"Backtest results saved to '{output_file}'.")

    # CSV 파일 읽기
    result_df = pd.read_csv(output_file)
    return result_df
