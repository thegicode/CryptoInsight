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

def fetch_order_closed(params):
    query_params = {
        'market': params.get('market')
    }

    # 선택적 매개변수를 조건부로 추가
    if 'states' in params:
        query_params['states[]'] = params.get('states')
        # default: ['done', 'cancel']

    if 'start_time' in params:
        query_params['start_time'] = params.get('start_time')
        # '2021-01-01T00:00:00+09:00'
        # start_time, end_time이 둘 다 정의되지 않은 경우 현재 시각으로부터 최대 1시간 전까지
        # start_time만 정의한 경우 start_time으로부터 최대 1시간 후까지
        # end_time만 정의한 경우 end_time으로부터 최대 1시간 전까지
        # start_time과 end_time을 둘 다 정의할 경우 최대 1시간 범위까지의 주문만 조회
    if 'end_time' in params:
        query_params['end_time'] = params.get('end_time')

    if 'limit' in params:
        query_params['limit'] = params.get('limit')
        # default: 100, max: 1000

    if 'order_by' in params:
        query_params['order_by'] = params.get('order_by')
        # desc : 내림차순 (default), asc : 오름차순

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

    url = UPBIT_SERVER_URL + '/v1/orders/closed'

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
        "market" : "KRW-BTC",
        "start_time": '2024-07-20T00:00:00+09:00'
    }
    order_closed = fetch_order_closed(params)
    print(json.dumps(order_closed, indent=4))

