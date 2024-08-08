import pandas as pd
import numpy as np
import ccxt  # 암호화폐 거래소 API를 위한 라이브러리
from dotenv import load_dotenv
import os

# 환경 변수 로드 함수
def load_environment_variables():
    """환경 변수를 로드합니다."""
    load_dotenv()
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    return api_key, secret_key


# 바이낸스 거래소 객체 생성 함수
def create_exchange():
    api_key, secret_key = load_environment_variables()

    """바이낸스 거래소 객체를 생성합니다."""
    return ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',  # 현물 거래용
        },
    })