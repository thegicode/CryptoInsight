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

def fetch_order_uuids(params):
    query_params = {}

    if 'uuids' in params and 'identifiers' in params:
        print("Error: 'uuids'와 'identifiers' 필드는 동시에 사용할 수 없습니다.")
        return None
    elif 'uuids' in params:
        query_params['uuids[]'] = params.get('uuids')
    elif 'identifiers' in params:
        query_params['identifiers[]'] = params.get('identifiers')
    else:
        print("Error: 'uuids' 또는 'identifiers' 필드 중 하나는 반드시 포함되어야 합니다.")
        return None

    if 'market' in params:
        query_params['market'] = params.get('market')

    if 'order_by' in params:
        query_params['order_by'] = params.get('order_by')
        # desc : 내림차순 (default), asc : 오름차순


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

    url = UPBIT_SERVER_URL + '/v1/orders/uuids'

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
        'uuids' : ["", ""],
    }
    order_uuids = fetch_order_uuids(params)
    print(json.dumps(order_uuids, indent=4))

