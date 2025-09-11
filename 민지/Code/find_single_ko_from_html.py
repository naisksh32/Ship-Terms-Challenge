# find_single_korean.py
import re
import sys

# 한글 범위 (가~힣, 자모 포함)
KOREAN_CHAR = re.compile(r'^[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7A3]$')

def find_single_korean(in_path: str) -> None:
    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    matches = []
    for idx, line in enumerate(lines, 1):
        raw = line.strip()
        if '||' not in raw:
            continue
        left, right = raw.split('||', 1)
        right = right.strip()
        # 오른쪽이 딱 1글자이고 그게 한국어면 매치
        if KOREAN_CHAR.match(right):
            matches.append((idx, left.strip(), right))

    if matches:
        print("한국어가 1글자인 줄:")
        for idx, left, right in matches:
            print(f"{idx}: {left} || {right}")
    else:
        print("해당 조건에 맞는 줄 없음.")

if __name__ == "__main__":
    in_file = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'
    find_single_korean(in_file)
