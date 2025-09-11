from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

from bs4 import BeautifulSoup
import time, csv, os
from datetime import datetime

# --- Chrome 옵션 (헤드리스) ---
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# --- WebDriver ---
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
except Exception as e:
    print(f"WebDriver 설치 및 실행 오류: {e}")
    exit(1)


# --- 출력 경로/파일 ---
file_name = f'Data/kosic.csv'
fields = ['한글', '영문', '설명']

rows = []

# --- 메인: 페이지 1~478, 항목 1~10 클릭 ---
try:
    url = f"http://kosic.or.kr/kor/view/word/wordList.do?"
        
        
    driver.get(url)
    time.sleep(2)  # 초기 로딩 여유
    for page_num in range(1, 479):
        
        if 'nowPage' not in url:
            url += f'nowPage={page_num}'
        else:
            url = "http://kosic.or.kr/kor/view/word/wordList.do?" + f'nowPage={page_num}'
        print(f"\n### 페이지 {page_num} 크롤링 시작 ###")
        driver.get(url)
        time.sleep(2)

         # 항목 1~10: 버튼 클릭 → 내용 추출
        for i in range(1, 11):
            base_sel = f"#dictionaryAccordian > div:nth-child({i})"
            btn_sel  = base_sel + " > div.accbtn"
            try:
                # 버튼 찾기 (없으면 다음 i)
                more_button = driver.find_element(By.CSS_SELECTOR, btn_sel)
            except Exception:
                # 해당 인덱스 항목이 없으면 남은 항목도 없다고 보고 break
                break

    #             # 클릭 (스크롤 후 클릭, 실패 시 JS 클릭)
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", more_button)
                time.sleep(0.05)
                try:
                    more_button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", more_button)
            except Exception:
                pass
            time.sleep(0.1)  # 펼침 반영 대기

            # 텍스트 추출 (한글/영문/설명)
            kor_sel  = base_sel + " > div.accbtn > div > p:nth-child(1)"
            eng_sel  = base_sel + " > div.accbtn > div > p:nth-child(2)"
            desc_sel = base_sel + " > div.acccont"

    #             kor = eng = desc = ""

            try:
                kor = driver.find_element(By.CSS_SELECTOR, kor_sel).text.strip()
            except Exception:
                pass
            try:
                eng = driver.find_element(By.CSS_SELECTOR, eng_sel).text.strip()
            except Exception:
                pass

    #             # 설명은 가끔 즉시 안 잡힐 수 있어 간단 백업(BS) 사용
            try:
                desc = driver.find_element(By.CSS_SELECTOR, desc_sel).text.strip()
            except Exception:
                try:
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    base_el = soup.select_one(base_sel)
                    if base_el:
                        cont = base_el.select_one("div.acccont")
                        if cont:
                            desc = cont.get_text(" ", strip=True)
                except Exception:
                    pass

            if kor or eng or desc:
                rows.append({
                    '한글': kor,
                    '영문': eng,
                    '설명': desc,
                })

    #         time.sleep(0.3)  # 페이지 간 예의상 대기

except WebDriverException as e:
    print(f"\n❌ WebDriver 오류 발생: {e}")
    print("\n💡 해결 방법:")
    print("1. Google Chrome 브라우저가 최신 버전인지 확인하세요.")
    print("2. 스크립트를 관리자 권한으로 실행해 보세요.")
    print("3. 네트워크 방화벽이 ChromeDriver 다운로드를 차단하지 않는지 확인하세요.")
except TimeoutException as e:
    print(f"\n❌ 페이지 로딩 시간 초과 오류: {e}")
    print("💡 해결 방법:")
    print("1. 인터넷 연결 상태를 확인하거나, 'set_page_load_timeout' 시간을 늘려보세요.")
except Exception as e:
    print(f"\n❌ 예상치 못한 오류 발생: {e}")
finally:
    if driver:
        print("\nWebDriver 종료 중...")
        driver.quit()
        print("WebDriver가 성공적으로 종료되었습니다.")

    # # --- CSV 저장 ---
if rows:
    # 간단 중복 제거(한글+영문+설명 앞 80자)
    seen = set()
    dedup = []
    for r in rows:
        key = (r['한글'], r['영문'], r['설명'][:80])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(r)
    with open(file_name, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(dedup)
    print(f"\n총 {len(dedup)}개 항목을 {file_name} 에 저장했습니다.")
else:
    print("\n수집된 데이터가 없습니다.")
