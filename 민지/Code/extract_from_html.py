from bs4 import BeautifulSoup
from pathlib import Path
import argparse
import sys
import re

def is_english(text: str) -> bool:
    # 알파벳 비율이 절반 이상이면 영어로 간주
    letters = re.findall(r'[A-Za-z]', text)
    return len(letters) > len(text) / 2

def clean_text(s: str) -> str:
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_terms_by_rule(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for p in soup.select("body > div > p"):
        bs = p.find_all("b")
        if len(bs) >= 2:
            t1 = clean_text(bs[0].get_text(separator=' ', strip=True))
            t2 = clean_text(bs[1].get_text(separator=' ', strip=True))
            if not t1 or not t2:
                continue
            # 영어/한글 순서 판별 후 맞춰주기
            if is_english(t1) and not is_english(t2):
                eng, kor = t1, t2
            elif is_english(t2) and not is_english(t1):
                eng, kor = t2, t1
            else:
                # 둘 다 영어 or 둘 다 한글 → 그냥 원래 순서
                eng, kor = t1, t2
            results.append((eng, kor))
    return results

def extract_terms_by_rule(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    # print(soup)
    for p in soup.select("body > div > p"):
        bs = p.find_all("b")
        if len(bs) >= 4:  # b:nth-child(2), b:nth-child(4) 최소 필요
            eng = bs[0].get_text(separator=' ', strip=True)
            kor = bs[1].get_text(separator=' ', strip=True)
            # 아래 두 줄이 포인트
            eng = eng.replace('\n', ' ').strip()
            kor = kor.replace('\n', ' ').strip()
            results.append((eng, kor))
    return results

# 사용 예시

files = []
ap = argparse.ArgumentParser(description="Extract 'English||한국어||설명' from MS-Word-like HTML files")
ap.add_argument("input", help="Input path (file or directory). If directory, all *.htm(l) files will be processed.")
args = ap.parse_args()
in_path = Path(args.input)
if in_path.is_dir():
    files = sorted(list(in_path.glob("*.htm")) + list(in_path.glob("*.html")))
elif in_path.is_file():
    files = [in_path]
else:
    print(f"Input not found: {args.input}", file=sys.stderr)
    sys.exit(1)

with open("Data/from_html.txt", "w", encoding="utf-8") as out:
    for f in files:
        html = f.read_text(encoding="euc-kr", errors="ignore")
        rows = extract_terms_by_rule(html)
        for eng, kor in rows:
            out.write(f"{eng}||{kor}\n")

    
