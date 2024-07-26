import json
import hashlib
import os
import sys
import requests
from urllib.parse import urlencode, unquote

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from api.constants import UPBIT_SERVER_URL
from upbit_token import generate_jwt_token

def fetch_orders(params=None):
    # params가 사전인지 확인
    if params is None:
        params = {}

    query_params = {
        'market': params.get('market'),
        'side': params.get('side'),  # bid : 매수, ask : 매도
        'volume': params.get('volume'),  # 주문량 (지정가, 시장가 매도 시 필수)
        'price': params.get('price'),  # 주문 가격. (지정가, 시장가 매수 시 필수)
        'ord_type': params.get('ord_type'),
    }

    # 선택적 매개변수를 조건부로 추가
    if 'identifier' in params:
        query_params['identifier'] = params.get('identifier')

    if 'time_in_force' in params:
        query_params['time_in_force'] = params.get('time_in_force')

    # query_params에서 None 값을 제거
    query_params = {k: v for k, v in query_params.items() if v is not None}

    query_string = unquote(urlencode(query_params, doseq=True)).encode("utf-8")
    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    authorize_token = generate_jwt_token(payload)
    headers = {"Authorization": authorize_token}

    url = UPBIT_SERVER_URL + '/v1/orders'

    try:
        response = requests.post(url, json=query_params, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        else:
            print(f"API 요청 실패. 상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"요청 중 예외가 발생했습니다: {e}")
        return None

# 테스트 코드
if __name__ == "__main__":
    params = {
        'market': 'KRW-BTC',
        'side': 'bid',
        'volume': '0.00011764',  # 1만원을 8500만원에 매수할 때의 비트코인 수량
        'price': '85000000',  # 8500만원
        'ord_type': 'limit',  # 지정가 주문
    }
    order_response = fetch_orders(params)
    if order_response:
        print(json.dumps(order_response, indent=4))
    else:
        print("주문 요청에 실패했습니다.")
