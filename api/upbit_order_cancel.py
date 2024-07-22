import json
import os
import sys
import requests
from urllib.parse import urlencode, unquote
import hashlib

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from api.constants import UPBIT_SERVER_URL
from upbit_token import generate_jwt_token


def cancel_order(params):
    query_params = {}

    if 'uuid' in params and 'identifier' in params:
        print("Error: 'uuid'와 'identifier' 필드는 동시에 사용할 수 없습니다.")
        return None
    elif 'uuid' in params:
        query_params['uuid'] = params.get('uuid')
    elif 'identifier' in params:
        query_params['identifier'] = params.get('identifier')
    else:
        print("Error: 'uuid' 또는 'identifier' 필드 중 하나는 반드시 포함되어야 합니다.")
        return None

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

    url = f"{UPBIT_SERVER_URL}/v1/order"

    response = requests.delete(url, headers=headers, params=query_params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"API 요청 실패. 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        return None

# 테스트 코드
if __name__ == "__main__":
    params = {
        'uuid' : ""
    }
    cancel_result = cancel_order(params)
    print(json.dumps(cancel_result, indent=4))
