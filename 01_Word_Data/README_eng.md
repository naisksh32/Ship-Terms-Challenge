# Maritime Terminology Data and Processing for LLM Fine-tuning

This repository is dedicated to collecting, processing, and preparing maritime terminology data for fine-tuning Large Language Models (LLMs). It includes raw data sources, intermediate processed data, final training/testing datasets, and the scripts used for these transformations.

## Folder Structure

```
C:\Users\SSAFY\Desktop\GitHub\Ship\Word_Data\
├───.gitignore
├───README.md
├───README.ko.md
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

## Data Description and Usage

### `01_Raw_Data`
This directory contains the initial, unprocessed data sources for maritime terminology.

### `02_Processed_Data`
This folder stores cleaned and standardized English-Korean word pairs derived from the raw data.

### `03_Train_Test_Set`
This directory holds the final datasets prepared for fine-tuning Large Language Models, formatted in JSONL.

### `04_Processing_Code`
This folder contains all the scripts that make up the data processing pipeline, organized into subfolders by function.

- **`01_Extraction`**: Scripts for collecting raw data from various sources like PDFs and websites.
- **`02_Cleaning`**: Scripts for standardizing formats, fixing errors, and merging datasets.
- **`03_Application`**: Scripts for generating the final datasets for LLM training and evaluation from the cleaned data.