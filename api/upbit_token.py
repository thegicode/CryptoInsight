import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from dotenv import load_dotenv
import uuid
import jwt

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# .env 파일 로드
load_dotenv()

# Upbit API 키 설정
access_key = os.getenv('UPBIT_ACCESS_KEY')
secret_key = os.getenv('UPBIT_SECRET_KEY')

def default_token():
    return access_key, secret_key

def generate_jwt_token(additional_payload=None):
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
    }

    if additional_payload:
        payload.update(additional_payload)

    jwt_token = jwt.encode(payload, secret_key)
    # jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")
    authorize_token = f'Bearer {jwt_token}'

    return authorize_token


# 테스트 코드
if __name__ == "__main__":
    access_key, secret_key = default_token()
    print("access_key", access_key)
    print("\nsecret_key", secret_key)

    authorize_token = generate_jwt_token()
    print("\nauthorize_token", authorize_token)