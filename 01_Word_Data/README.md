# LLM 파인튜닝을 위한 해양 용어 데이터 및 처리

이 저장소는 대규모 언어 모델(LLM) 파인튜닝을 위한 해양 용어 데이터를 수집, 처리 및 준비하는 것을 목표로 합니다. 원시 데이터 소스, 중간 처리 데이터, 최종 학습/테스트 데이터셋 및 이러한 변환에 사용된 스크립트가 포함되어 있습니다.

## 폴더 구조

```
C:\Users\SSAFY\Desktop\GitHub\Ship\Word_Data\
├───.gitignore
├───README.md
├───requirements.txt
├───01_Raw_Data\
│   ├───2020년 국제해사기구 전문용어집_페이지 편집본.pdf
│   ├───조선표준용어-ks.xls
│   ├───eshine_table.csv
│   ├───IMO_word.csv
│   ├───kosic.csv
│   └───naver_iframe_parsed.csv
├───02_Processed_Data\
│   ├───eng_word_fixed.csv
│   └───only_eng_kor_word.csv
├───03_Train_Test_Set\
│   ├───test_data.jsonl
│   └───train_data.jsonl
└───04_Processing_Code\
    ├───01_Extraction\
    │   ├───enshine_scrape.py
    │   ├───extract_from_html.py
    │   ├───kosic_selenium.py
    │   ├───naver_scrape.py
    │   └───preprocessing_pdf.ipynb
    ├───02_Cleaning\
    │   ├───change_parser.ipynb
    │   ├───check_char_parser.py
    │   ├───concat.ipynb
    │   ├───find_single_ko_from_html.py
    │   └───only_eng_kor_word.ipynb
    └───03_Application\
        ├───create_train_test_dataset.py
        └───prepare_dataset.py
```

## 데이터 설명 및 사용법

### `01_Raw_Data`
이 디렉토리에는 해양 용어에 대한 초기, 처리되지 않은 데이터 소스가 포함되어 있습니다.

### `02_Processed_Data`
이 폴더에는 원시 데이터에서 파생된, 정제되고 표준화된 영한 단어 쌍이 저장되어 있습니다.

### `03_Train_Test_Set`
이 디렉토리에는 대규모 언어 모델 파인튜닝을 위해 준비된 최종 데이터셋이 들어 있습니다.

### `04_Processing_Code`
이 폴더에는 데이터 처리 파이프라인을 구성하는 모든 스크립트가 포함되어 있으며, 기능에 따라 하위 폴더로 정리되어 있습니다.

- **`01_Extraction (추출)`**: PDF, 웹사이트 등 다양한 소스에서 원시 데이터를 수집하는 스크립트입니다.
- **`02_Cleaning (정제)`**: 추출된 데이터의 형식을 표준화하고, 오류를 수정하며, 여러 데이터셋을 병합하는 스크립트입니다.
- **`03_Application (활용)`**: 정제된 데이터를 바탕으로 LLM 학습 및 평가를 위한 최종 데이터셋을 생성하는 스크립트입니다.
