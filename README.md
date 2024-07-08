# trade

## 거래 실행 순서

```

python3 -m fetchers
python3 backtest.py

python3 analysis/analyze_backtest.py  (확인용)

python3 main.py

python3 analysis/process_strategies_and_signals.py

```

## 설치 및 실행

1. **터미널을 열고 프로젝트 디렉토리로 이동합니다:**

    ```
    cd /Users/deokim/Documents/코딩/project-my/CryptoInsight
    ```

2. 가상 환경을 생성하고 활성화합니다:
   python3 -m venv venv
   source venv/bin/activate

3. 가상 환경 내에서 VSCode를 실행합니다:
   code .

4. VSCode에서 파이썬 인터프리터를 선택합니다 (Python: Select Interpreter).

5. .vscode/settings.json 파일을 설정하여 가상 환경을 명시합니다:

{
"python.pythonPath": "/Users/aaa/Documents/코딩/project-my/CryptoInsight/venv/bin/python"
}

6. 필요한 패키지를 설치합니다:
   pip install pandas matplotlib numpy requests

<br>

### 올바른 파이썬 환경 선택

VSCode나 다른 IDE를 사용 중이라면, 올바른 파이썬 환경(가상 환경)을 선택했는지 확인해야 합니다.

VSCode에서 파이썬 환경 선택

1. 명령 팔레트 열기: Ctrl + Shift + P (Windows/Linux) 또는 Cmd + Shift + P (macOS) 를 눌러 명령 팔레트를 엽니다.
2. Python: Select Interpreter를 검색하여 선택합니다.
3. 가상 환경 선택: 생성한 가상 환경(예: venv)을 선택합니다.

<br>

### PYTHONPATH 설정

가상 환경에서 스크립트를 실행할 때도 PYTHONPATH를 설정해야 할 수 있습니다. 이를 위해 앞서 언급한 명령어를 사용합니다:
export PYTHONPATH="${PYTHONPATH}:/Users/aaa/Documents/코딩/project-my/trade"

<br>

---

<br>

## 테스트

-   pytest {path}
-   print 적용 : 코드 pytest.main(['-s']), 터미널 pytest -s {path}
-   assert는 일반적인 조건 검증에 사용 : 기본값만 비교
    np.testing.assert_array_equal은 주로 배열의 값, 형태, 데이터 타입 등을 비교할 때 사용 : 배열의 데이터 타입, 형상, 값 등을 포괄적으로 비교

<br>

---

<br>

## 각 파일 및 폴더 설명

### data/

-   원시 데이터를 저장하는 폴더입니다. `raw/` 서브 폴더에는 API에서 가져온 원시 데이터를 저장할 수 있습니다.

### api/

-   외부 API와의 통신을 처리하는 모듈입니다.
-   `upbit_api.py`: Upbit API를 사용하여 데이터를 가져오는 기능을 포함합니다.

### utils/

-   자주 사용하는 유틸리티 함수들을 모아둔 폴더입니다.
-   `moving_averages.py`: 이동 평균을 계산하는 함수들.
-   `signals.py`: 트레이딩 신호를 계산하는 함수들 (예: 골든크로스, 데드크로스).

### backtest/

-   백테스트를 위한 모듈입니다.
-   `strategy.py`: 백테스트 전략을 정의하는 모듈입니다.
-   `backtester.py`: 백테스트를 실행하고 결과를 분석하는 모듈입니다.

### notebooks/

-   Jupyter 노트북 파일을 저장하는 폴더입니다. 데이터 분석과 시각화를 위한 노트북 파일을 포함합니다.

### tests/

-   단위 테스트를 위한 모듈입니다.
-   `test_api.py`: API 모듈의 테스트를 위한 파일입니다.
-   `test_utils.py`: 유틸리티 함수의 테스트를 위한 파일입니다.
-   `test_backtest.py`: 백테스트 모듈의 테스트를 위한 파일입니다.

### main.py

-   메인 실행 파일입니다. 여기서 전체 워크플로우를 실행할 수 있습니다.

### requirements.txt

-   프로젝트에 필요한 패키지 목록을 포함합니다. 예를 들어, `pandas`, `numpy`, `matplotlib`, `requests` 등이 포함될 수 있습니다.

### 프로젝트 구조

project/
│
├── data/ # 데이터 저장 폴더
│ └── raw/ # 원시 데이터
│
├── api/ # 외부 API와의 통신을 위한 모듈
│ └── upbit_api.py # Upbit API를 통해 데이터 가져오기
│
├── utils/ # 유틸리티 함수 모음
│ ├── moving_averages.py # 이동 평균 계산 함수
│ └── signals.py # 트레이딩 신호 계산 함수 (골든크로스, 데드크로스 등)
│
├── backtest/ # 백테스트 모듈
│ ├── strategy.py # 백테스트 전략 정의
│ └── backtester.py # 백테스트 실행 및 결과 분석
│
├── notebooks/ # Jupyter 노트북 파일 (데이터 분석 및 시각화)
│ └── analysis.ipynb # 데이터 분석 및 시각화를 위한 노트북
│
├── tests/ # 단위 테스트
│ ├── test_api.py # API 모듈 테스트
│ ├── test_utils.py # 유틸리티 함수 테스트
│ └── test_backtest.py # 백테스트 모듈 테스트
│
├── main.py # 메인 실행 파일
├── requirements.txt # 필요한 패키지 목록
└── README.md # 프로젝트 설명

## requirements.txt

### 패키지 목록 저장:

pip freeze > requirements.txt

## Crontab

crontab -e
"ESC", ":wq"
crontab -l

0 9 \* \* _ /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/deokim/Documents/코딩/project-my/CryptoInsight/results/trade/process_strategies_and_signall
s.txt >> //Users/deokim/Documents/코딩/project-my/CryptoInsight/logs/cron.log 2>&1
0 0 _ \* \* /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/deokim/Documents/코딩/project-my/CryptoInsight/results/trade/process_strategies_and_signall
s.txt >> //Users/deokim/Documents/코딩/project-my/CryptoInsight/logs/cron.log 2>&1
