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