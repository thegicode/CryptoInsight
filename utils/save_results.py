import os
import shutil
import pandas as pd
from datetime import datetime

def save_market_backtest_result(market, df, count, name, check_ma=False, check_volume=False):
    """
    시장 백테스트 결과를 CSV 파일로 저장하는 함수.

    :param market: 가상화폐 시장 코드
    :param df: 데이터프레임 (백테스트 결과)
    :param count: 데이터 수
    :param name: 백테스트 이름
    :param check_ma: 이동 평균 확인 여부
    :param check_volume: 거래량 평균 확인 여부
    """

    output_dir = f'results/backtest/{name}_{"checkMA_" if check_ma else ""}{"checkVolume_" if check_volume else ""}backtest'

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{name}_{market}_{count}.csv')
    df.to_csv(output_file, index=True)

def save_backtest_results(results, count, name):
    """
    백테스트 결과를 저장하는 함수

    :param results: 백테스트 결과 리스트
    :param count: 데이터 개수
    :param name: 결과 파일 이름에 사용할 문자열
    :return: 저장된 결과의 데이터프레임
    """
    # 결과 리스트를 데이터프레임으로 변환
    results_df = pd.DataFrame(results)

    # Win Rate (%) 기준으로 정렬
    if 'Win Rate (%)' in results_df.columns:
        results_df = results_df.sort_values(by="Win Rate (%)", ascending=False)

    # 결과를 저장할 디렉터리 생성
    output_dir = os.path.join('results', 'backtest')
    os.makedirs(output_dir, exist_ok=True)

    # 날짜 문자열 추가
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 결과 파일 경로 설정
    output_file = os.path.join(output_dir, f'{name}_backtest_{count}.csv')

    # 기존 파일이 있는 경우 백업
    if os.path.exists(output_file):
        backup_file = os.path.join(output_dir, f'{name}_backtest_{count}_backup_{date_str}.csv')
        shutil.move(output_file, backup_file)
        print(f"Existing file backed up to '{backup_file}'.")

    # 데이터프레임을 CSV 파일로 저장
    results_df.to_csv(output_file, index=False)
    print(f"Backtest results saved to '{output_file}'.")

    # 저장된 CSV 파일을 다시 읽어 데이터프레임으로 반환
    saved_results_df = pd.read_csv(output_file)
    return saved_results_df

