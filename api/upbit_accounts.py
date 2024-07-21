import os
from dotenv import load_dotenv
import uuid
import requests
import jwt
import json

# .env 파일 로드
load_dotenv()

# Upbit API 키 설정
access_key = os.getenv('UPBIT_ACCESS_KEY')
secret_key = os.getenv('UPBIT_SECRET_KEY')

def upbit_accounts():
    server_url = 'https://api.upbit.com'
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")

    authorize_token = f'Bearer {jwt_token}'
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/accounts", headers=headers)

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
    balances = upbit_accounts()
    print(json.dumps(balances, indent=2))


# currency	화폐를 의미하는 영문 대문자 코드	String
# balance	주문가능 금액/수량	NumberString
# locked	주문 중 묶여있는 금액/수량	NumberString
# avg_buy_price	매수평균가	NumberString
# avg_buy_price_modified	매수평균가 수정 여부	Boolean
# unit_currency	평단가 기준 화폐	String
