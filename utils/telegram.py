
import time
from dotenv import load_dotenv
import os
import requests

# .env 파일 로드
load_dotenv()


# 텔레그램 봇 토큰과 채팅 ID 설정
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# HTTP 요청 타임아웃 설정
REQUEST_TIMEOUT = 60  # 초 단위로 설정 (예: 60초)




def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}. Retrying...")
        time.sleep(5)
        send_telegram_message(message)