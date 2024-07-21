import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import requests
import json
from api.constants import UPBIT_SERVER_URL
from api.upbit_token import generate_jwt_token


def fetch_upbit_accounts():

    authorize_token = generate_jwt_token()
    headers = {"Authorization": authorize_token}

    res = requests.get(f"{UPBIT_SERVER_URL}/v1/accounts", headers=headers)

    # 응답이 성공적인지 확인
    if res.status_code != 200:
        print(f"API 요청 실패. 상태 코드: {res.status_code}")
        print(f"응답 내용: {res.text}")
        return []

    try:
        # JSON 응답을 파이썬 객체로 변환
        balances = res.json()

        # 응답이 리스트인지 확인
        if not isinstance(balances, list):
            print(f"예상치 못한 응답 형식. 응답 내용: {balances}")
            return []

        return balances
    except json.JSONDecodeError:
        print(f"JSON 디코딩 실패. 응답 내용: {res.text}")
        return []

# 테스트 코드
if __name__ == "__main__":
    upbit_accounts = fetch_upbit_accounts()
    print(json.dumps(upbit_accounts, indent=4))


# https://docs.upbit.com/reference/전체-계좌-조회