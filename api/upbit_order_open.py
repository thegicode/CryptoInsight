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

def fetch_order_open(params=None):
    query_params = {}

    if (params):
        # 선택적 매개변수를 조건부로 추가
        if 'market' in params:
            query_params['market'] = params.get('market')
            # String

        if 'state' in params:
            query_params['state'] = params.get('state')
            # String

        if 'states' in params:
            query_params['states[]'] = params.get('states')
            # Array[String]  wait(default), watch

        if 'page' in params:
            query_params['page'] = params.get('page')
            # Number, 페이지 수, default: 1

        if 'limit' in params:
            query_params['limit'] = params.get('limit')
            # Number, 요청 개수, default: 100, max: 100

        if 'order_by' in params:
            query_params['order_by'] = params.get('order_by')
            # String, desc : 내림차순 (default), asc : 오름차순


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

    url = UPBIT_SERVER_URL + '/v1/orders/open'

    response = requests.get(url, params=query_params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"API 요청 실패. 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        return None

# 테스트 코드
if __name__ == "__main__":
    params = {
        # 'market':'KRW-SHIB'
    }
    order_open_info = fetch_order_open(params)
    print(json.dumps(order_open_info, indent=4))

