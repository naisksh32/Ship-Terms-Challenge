import csv, re, sys, time
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36"),
    "Accept-Language": "ko,ko-KR;q=0.9,en;q=0.8",
    "Referer": "https://blog.naver.com/",
}

INPUT_URL = "https://blog.naver.com/k5808151/50150791450"  # ← 대상 URL

def fetch(url, retry=3, backoff=1.5):
    last = None
    for i in range(retry):
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r
        except Exception as e:
            last = e
            time.sleep(backoff * (i + 1))
    raise RuntimeError(f"요청 실패: {last}")

def get_iframe_src_from_desktop(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    iframe = soup.select_one("iframe#mainFrame")
    if iframe and iframe.has_attr("src"):
        return urljoin(base_url, iframe["src"])
    return None

def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    return s

def text_len(el: Tag) -> int:
    return len(clean_text(el.get_text(" ", strip=True)))

def find_content_container(soup: BeautifulSoup):
    """
    구형/신형 에디터 모두 포괄: div/td/section 등 다양한 후보를 모은 뒤
    '텍스트 길이'가 가장 큰 요소를 본문으로 간주.
    """
    candidate_selectors = [
        # 흔한 컨테이너 id/class
        "#postViewArea", "#post-area", "#printPost1", "#viewType",
        "div.se-main-container", "div.se_component_wrap",
        "div#post-view", "div[id^=post-view]",

        # 구형: table/td 기반
        "td#postViewArea", "td#viewType", "td#printContents",
        "div#content", "div#contentArea",

        # 기타 범용
        "article", "section", "div#content-area", "div#article"
    ]
    candidates = []
    for sel in candidate_selectors:
        for el in soup.select(sel):
            if el not in candidates:
                candidates.append(el)

    # 후보가 없으면 body 하위의 큰 블록 요소들을 후보로
    if not candidates:
        for el in soup.select("body div, body section, body article, body td"):
            candidates.append(el)

    if not candidates:
        return None

    best = max(candidates, key=text_len, default=None)
    # 너무 빈약하면 body 자체를 사용
    if not best or text_len(best) < 50:
        return soup.body or best
    return best

def iter_text_blocks(container: Tag):
    """
    <p>, <li>, <span>, <br> 등을 기준으로 사람이 읽는 순서대로 텍스트를 수집.
    """
    blocks = []

    def flush(buf):
        t = clean_text(" ".join(buf))
        if t:
            blocks.append(t)
        buf.clear()

    buf = []

    # 너비가 큰 표도 본문인 경우가 있어 tr/td를 함께 순회
    for el in container.descendants:
        if isinstance(el, NavigableString):
            txt = clean_text(str(el))
            if txt:
                buf.append(txt)
            continue

        if not isinstance(el, Tag):
            continue

        name = el.name.lower()

        # 줄바꿈 역할 요소
        if name in ("p", "li", "tr"):
            # p/li/tr 시작할 때 기존 버퍼를 줄로 확정
            flush(buf)

        if name == "br":
            flush(buf)

    flush(buf)
    # 빈 라인 제거
    blocks = [b for b in blocks if b]
    return blocks

def write_csv(path, values):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["idx", "text"])
        for i, v in enumerate(values, start=1):
            w.writerow([i, v])

def main():
    # 1) 바깥 프레임셋 문서
    outer = fetch(INPUT_URL)
    iframe_src = get_iframe_src_from_desktop(outer.text, INPUT_URL)
    if not iframe_src:
        # 일부는 바로 본문이 있을 수도 있으니 그 경우 처리
        soup = BeautifulSoup(outer.text, "html.parser")
        container = find_content_container(soup)
        if not container:
            with open("debug_outer.html", "w", encoding="utf-8") as f:
                f.write(outer.text)
            print("❌ iframe도 없고 본문 후보도 못 찾았습니다. debug_outer.html 저장됨.")
            sys.exit(1)
        values = iter_text_blocks(container)
        if not values:
            print("❌ 본문 후보는 찾았으나 텍스트가 비었습니다.")
            sys.exit(1)
        write_csv("naver_outer_parsed.csv", values)
        print(f"✅ 바깥 문서에서 직접 추출: {len(values)}개 → naver_outer_parsed.csv")
        return

    # 2) iframe 실제 본문 문서
    inner = fetch(iframe_src)
    with open("debug_iframe_raw.html", "w", encoding="utf-8") as f:
        f.write(inner.text)  # 구조 확인용

    i_soup = BeautifulSoup(inner.text, "html.parser")
    container = find_content_container(i_soup)
    if not container:
        print("ℹ️ 컨테이너 후보 탐색 실패 → body 전체에서 추출 시도")
        container = i_soup.body

    if not container:
        print("❌ iframe 문서에서 body가 없습니다.")
        sys.exit(1)

    values = iter_text_blocks(container)
    if not values:
        print("❌ iframe 본문에서 텍스트가 비었습니다. debug_iframe_raw.html을 확인하세요.")
        sys.exit(1)

    out = "naver_iframe_parsed.csv"
    write_csv(out, values)
    print(f"✅ iframe 본문 추출 성공: {len(values)}개 → {out}")

if __name__ == "__main__":
    main()
