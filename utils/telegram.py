
import time
import os
import requests

from dotenv import load_dotenv


# .env 파일 로드
load_dotenv()


# 텔레그램 봇 토큰과 채팅 ID 설정
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# HTTP 요청 타임아웃 설정
REQUEST_TIMEOUT = 60  # 초 단위로 설정 (예: 60초)


def send_telegram_message(message, chat_id = CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, data=data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}. Retrying...")
        time.sleep(5)
        send_telegram_message(message)


def get_chat_ids():
    URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    response = requests.get(URL)
    if response.status_code == 200:
        data = response.json()
        chat_ids = set()
        for result in data['result']:
            message = result.get('message', {})
            chat = message.get('chat', {})
            chat_id = chat.get('id')
            if chat_id:
                chat_ids.add(chat_id)
                print(f"Chat ID: {chat_id}")
        return chat_ids
    else:
        print(f"Failed to get updates. Status code: {response.status_code}")
        return None