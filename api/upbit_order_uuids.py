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

def fetch_order_uuids(market):
    params = {
        'uuids[]': uuids
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

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

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"API 요청 실패. 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        return None

# 테스트 코드
if __name__ == "__main__":
    uuids = [""]
    order_uuids = fetch_order_uuids(uuids)
    print(json.dumps(order_uuids, indent=4))

