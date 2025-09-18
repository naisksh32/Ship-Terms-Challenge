# Ship Terms Scraping Project

This project scrapes and processes ship-related terms from various online and offline sources.

## Data Sources

- **조선해양약어집 (2006)**: A CHM file containing a dictionary of ship and oceanography acronyms.
- **Enshine**: Website for ship-related information.
- **KOSIC**: Korean Shipping Information Center.
- **Naver**: Naver's online dictionary and resources.

## Setup

1.  **Install Dependencies**:
    Before running the scripts, install the necessary Python packages using pip:
    ```shell
    pip install -r Code/requirements.txt
    ```

2.  **Decompile CHM File**:
    The `조선해양약어집_2006.CHM.chm` file needs to be decompiled into HTML files.

    -   **For Windows**:
        Use the built-in `hh.exe` to decompile the CHM file into the `Data/html` directory.
        ```shell
        hh.exe -decompile Data\html "Data\조선해양약어집_2006.CHM.chm"
        ```

    -   **For Linux or macOS**:
        You can use a tool like `extract_chmLib`.
        ```shell
        extract_chmLib "Data/조선해양약어집_2006.CHM.chm" Data/html
        ```

## Usage

The following scripts are used to scrape and process the data.

### 1. Extract from HTML (from CHM)

This script extracts data from the HTML files that were decompiled from the CHM file.

```shell
python Code/extract_from_html.py --input=Data/html
```
This will generate `Data/from_html.txt`.

### 2. Find Single Korean Characters (Optional)

This script is used to find lines with only a single Korean character in the `from_html.txt` file. This is useful for identifying potential parsing errors that may require manual correction.

```shell
python Code/find_single_ko_from_html.py Data/from_html.txt
```

### 3. Scrape from Web Sources

These scripts scrape data from various websites.

-   **Enshine**:
    ```shell
    python Code/enshine_scrape.py
    ```
    This creates `Data/eshine_table.csv`.

-   **KOSIC**:
    ```shell
    python Code/kosic_selenium.py
    ```
    This creates `Data/kosic.csv`.

-   **Naver**:
    ```shell
    python Code/naver_scrape.py
    ```
    This creates `Data/naver_iframe_parsed.csv`.

# Gemma-3 LoRA Fine-Tuning

## 1. Prepare Dataset

Splits the original dataset, such as `training_data_10000.jsonl`, into training and evaluation sets for LoRA fine-tuning.

-   `--infile`: Path to the original JSONL file.
-   `--train_out`: Path for the generated training data file.
-   `--eval_out`: Path for the generated evaluation data file.
-   `--eval_ratio`: The ratio to split for evaluation data (default: 0.05).

```shell
python Code/src/prepare_dataset.py \
  --infile Code/data/training_data_10000.jsonl \
  --train_out Code/data/train.jsonl \
  --eval_out Code/data/eval.jsonl
```

## 2. Run LoRA Fine-Tuning

Fine-tunes the `gemma-3-1b-it` model using the prepared dataset with LoRA.

-   `--train_path`: Path to the training data file.
-   `--eval_path`: Path to the evaluation data file.
-   `--base_model`: The base Gemma-3 model to use.
-   `--out_dir`: Directory where the LoRA adapter will be saved.
-   `--max_len`: Maximum input length.
-   `--epochs`: Number of training epochs.
-   `--lr`: Learning rate.
-   `--batch_size`: Batch size.
-   `--grad_accum`: Gradient accumulation steps.

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