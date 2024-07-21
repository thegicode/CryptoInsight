import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from dotenv import load_dotenv
import uuid
import requests
import jwt
import json
from api.constants import UPBIT_SERVER_URL

# .env 파일 로드
load_dotenv()

# Upbit API 키 설정
access_key = os.getenv('UPBIT_ACCESS_KEY')
secret_key = os.getenv('UPBIT_SECRET_KEY')

def get_upbit_balance():
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")

    authorize_token = f'Bearer {jwt_token}'
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
    balances = get_upbit_balance()
    print(json.dumps(balances, indent=2))