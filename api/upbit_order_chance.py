import json
import os
import sys
import requests

import hashlib
import os
import requests
from urllib.parse import urlencode, unquote

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from dotenv import load_dotenv
from api.constants import UPBIT_SERVER_URL
from upbit_token import get_authorize_token

def get_order_chance(market):

    params = {
        'market': market
    }
    query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    authorize_token = get_authorize_token(payload)
    headers = {"Authorization": authorize_token}

    url = f"{UPBIT_SERVER_URL}/v1/orders/chance"
    params = {"market": market}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"API 요청 실패. 상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text}")
        return None

# 테스트 코드
if __name__ == "__main__":
    market = "KRW-BTC"
    order_chance_info = get_order_chance(market)
    print(json.dumps(order_chance_info, indent=4))
