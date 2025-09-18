# 선박 용어 스크래핑

다양한 온라인·오프라인 출처에서 선박 관련 용어를 스크래핑하고 가공하는 작업을 수행

## 데이터 출처

- **조선해양약어집 (2006)**: 선박 및 해양 관련 약어 사전이 수록된 CHM 파일
- **Enshine**: 선박 관련 정보를 제공하는 웹사이트
- **KOSIC**: 한국해운정보센터
- **Naver**: 네이버 온라인 사전 및 리소스

## 환경 설정

1.  **필수 패키지 설치**
    스크립트를 실행하기 전 `pip`을 사용하여 필요한 파이썬 패키지를 설치
    ```shell
    pip install -r Code/requirements.txt
    ```

2.  **CHM 파일 디컴파일**

    조선해양약어집\_2006.CHM.chm 파일을 HTML 파일로 디컴파일

    -   Windows

        내장 hh.exe를 사용해 CHM 파일을 Data/html 디렉터리로 디컴파일
        ```shell
        hh.exe -decompile Data\html "Data\조선해양약어집_2006.CHM.chm"
        ```
    -   Linux / macOS

        extract\_chmLib 등의 도구를 사용 가능
        ```shell
        extract_chmLib "Data/조선해양약어집_2006.CHM.chm" Data/html
        ```

## 사용 방법

다음 스크립트들을 사용해 데이터를 스크래핑 및 가공

1.  HTML(디컴파일된 CHM)에서 추출

    디컴파일된 CHM HTML 파일에서 데이터를 추출
    ```shell
    python Code/extract_from_html.py --input=Data/html
    ```
    실행 후 Data/from\_html.txt 파일이 생성됨

2.  단일 한글 문자 찾기 (선택)

    from\_html.txt 파일 내에서 한 글자짜리 한글 항목을 찾아 파싱 오류를 식별하는 데 사용
    ```shell
    python Code/find_single_ko_from_html.py Data/from_html.txt
    ```

3.  웹 사이트 스크래핑

    다양한 웹사이트에서 데이터를 스크래핑

    -   Enshine
        ```shell
        python Code/enshine_scrape.py
        ```
        → Data/eshine\_table.csv 생성
    -   KOSIC
        ```shell
        python Code/kosic_selenium.py
        ```
        → Data/kosic.csv 생성
    -   Naver
        ```shell
        python Code/naver_scrape.py
        ```
        → Data/naver\_iframe\_parsed.csv 생성

# Gemma-3 LoRA 미세조정

## 1. 데이터셋 준비

`training_data_10000.jsonl`과 같은 원본 데이터셋을 LoRA 미세조정을 위한 학습 및 평가 데이터로 분할

-   `--infile`: 원본 JSONL 파일 경로
-   `--train_out`: 생성될 학습 데이터 파일 경로
-   `--eval_out`: 생성될 평가 데이터 파일 경로
-   `--eval_ratio`: 평가 데이터 분할 비율 (기본값: 0.05)

```shell
python Code/src/prepare_dataset.py \
  --infile Code/data/training_data_10000.jsonl \
  --train_out Code/data/train.jsonl \
  --eval_out Code/data/eval.jsonl
```

## 2. LoRA 미세조정 실행

준비된 데이터셋을 사용하여 `gemma-3-1b-it` 모델을 LoRA 방식으로 미세조정

-   `--train_path`: 학습 데이터 파일 경로
-   `--eval_path`: 평가 데이터 파일 경로
-   `--base_model`: 기반이 될 Gemma-3 모델
-   `--out_dir`: LoRA 어댑터가 저장될 디렉터리
-   `--max_len`: 최대 입력 길이
-   `--epochs`: 학습 에포크 수
-   `--lr`: 학습률
-   `--batch_size`: 배치 크기
-   `--grad_accum`: 그래디언트 축적 단계

```shell
python Code/src/train_gemma3_lora.py \
  --base_model google/gemma-3-1b-it \
  --train_path Code/data/train.jsonl \
  --eval_path Code/data/eval.jsonl \
  --epochs 2 \
  --lr 2e-4 \
  --batch_size 2 \
  --grad_accum 8 \
  --max_len 1024
```