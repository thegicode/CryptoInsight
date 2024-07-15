from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Selenium 웹드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 웹페이지 로드
url = "https://upbit.com/trends"
driver.get(url)

try:
    # 테이블이 로드될 때까지 대기 (최대 20초)
    table = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.BasicTable.CryptNewsTable.CryptNewsTable--Period"))
    )

    # 페이지 소스 가져오기
    page_source = driver.page_source

    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(page_source, 'html.parser')

    # 테이블 찾기
    table = soup.select_one('table.BasicTable.CryptNewsTable.CryptNewsTable--Period')

    if table:
        # 데이터 추출
        data = []
        rows = table.select('tbody > tr')[:3]
        for row in rows:
            cols = row.select('td')
            if len(cols) >= 3:
                coin_name = cols[0].text.strip()
                symbol = cols[1].text.strip().split('/')[0]
                ticker = f"KRW-{symbol}"
                change_rate = cols[2].text.strip()
                data.append([coin_name, ticker, change_rate])

        # DataFrame 생성 (열 이름 변경)
        df = pd.DataFrame(data, columns=['마켓', 'Ticker', '1주일 등락률'])

        # 결과 출력
        print(df)

        # Ticker 열의 값만 추출
        tickers = df['Ticker'].tolist()
        print("\n추출된 Ticker:")
        print(tickers)


        ## 매수 주문
    else:
        print("테이블을 찾을 수 없습니다.")

except Exception as e:
    print(f"에러 발생: {e}")

finally:
    # 브라우저 종료
    driver.quit()