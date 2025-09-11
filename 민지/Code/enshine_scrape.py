import csv, sys, time
from pathlib import Path
from typing import List
import requests
from bs4 import BeautifulSoup

URL = "https://eshine.tistory.com/1882726"  # ← 스크랩 대상 페이지
OUT_CSV = "Data/eshine_table.csv"

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36")
}

def fetch_html(url: str, retry: int = 3, backoff: float = 1.5) -> str:
    last_err = None
    for i in range(retry):
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
            # tistory는 UTF-8. 혹시 모를 인코딩 지정
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:
            last_err = e
            time.sleep(backoff * (i + 1))
    raise RuntimeError(f"페이지 요청 실패: {last_err}")

def clean_cell_text(cell) -> str:
    # font/span/span 등의 중첩을 무시하고 공백 정리
    txt = cell.get_text(" ", strip=True)
    # 엑셀 표에서 빈칸/nbsp 처리
    txt = " ".join(txt.split())
    return txt

def find_target_table(soup: BeautifulSoup):
    """
    #article-view 아래의 본문 컨테이너(.contents_style) 안에서
    'table' 요소 하나를 택한다. 표가 여러 개면 '가장 큰(행/열이 많은)' 표 선택.
    """
    root = soup.select_one("#article-view .contents_style")
    if not root:
        # 백업: #article-view 바로 아래에서도 검색
        root = soup.select_one("#article-view")
    if not root:
        return None

    tables = root.select("table")
    if not tables:
        return None

    # 가장 데이터가 커보이는 테이블 선택(행*열 최대)
    best = None
    best_score = -1
    for tb in tables:
        rows = tb.select("tr")
        if not rows:
            continue
        # 첫 몇 행을 봐서 평균 열 수 추정
        cols_counts = [len(r.find_all(["td", "th"])) for r in rows[:10]]
        avg_cols = (sum(cols_counts) / len(cols_counts)) if cols_counts else 0
        score = len(rows) * avg_cols
        if score > best_score:
            best = tb
            best_score = score
    return best

def parse_table_to_rows(table) -> List[List[str]]:
    rows = []
    for tr in table.select("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        vals = [clean_cell_text(td) for td in cells]
        # 완전 공백 행은 스킵
        if any(v for v in vals):
            rows.append(vals)
    return rows

def write_csv(path: str, rows: List[List[str]]):
    if not rows:
        print("추출된 데이터가 없습니다.")
        return
    # CSV 헤더 결정:
    # 1) 첫 행이 전형적인 헤더처럼 보이면 그대로 사용
    # 2) 아니면 col_1, col_2 ... 자동 생성
    first = rows[0]
    looks_like_header = all(len(x) <= 30 for x in first) and len(set(first)) == len(first)
    # (조건은 느슨하게; 필요하면 바꾸세요)

    if looks_like_header:
        headers = first
        data = rows[1:]
    else:
        width = max(len(r) for r in rows)
        headers = [f"col_{i+1}" for i in range(width)]
        # 모든 행을 width에 맞춰 패딩
        data = [r + [""] * (width - len(r)) for r in rows]

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in data:
            # 헤더 쓰고 나면 열수에 맞춰 패딩
            if len(r) < len(headers):
                r = r + [""] * (len(headers) - len(r))
            w.writerow(r)

def main():
    try:
        html = fetch_html(URL)
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        sys.exit(1)

    soup = BeautifulSoup(html, "html.parser")
    table = find_target_table(soup)
    if not table:
        print("❌ 표(table)를 찾지 못했습니다. 셀렉터를 확인하세요.")
        sys.exit(1)

    rows = parse_table_to_rows(table)
    if not rows:
        print("❌ 표에서 데이터를 추출하지 못했습니다.")
        sys.exit(1)

    write_csv(OUT_CSV, rows)
    print(f"✅ 총 {len(rows)}개 행을 '{OUT_CSV}'로 저장했습니다.")

if __name__ == "__main__":
    main()
