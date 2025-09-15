# 데이터 전처리
# 영단어들 중 ( 문자가 있지만 ) 문자가 없는 경우 마지막에 )를 추가하는 로직
# 한국단어들 중 

import pandas as pd

def fix_parentheses_in_csv(input_file='eng_word.csv', output_file='eng_word_fixed.csv'):
    """
    CSV 파일의 '영단어' 열을 읽어, 여는 괄호'('는 있지만 닫는 괄호')'가 없는 경우
    문자열 끝에 ')'를 추가하여 새로운 파일로 저장합니다.
    """
    try:
        # '|' 구분자로 CSV 파일 읽기
        df = pd.read_csv(input_file, delimiter='|')
        print(f"'{input_file}' 파일을 성공적으로 읽었습니다.")
    except FileNotFoundError:
        print(f"오류: '{input_file}' 파일을 찾을 수 없습니다. 파일이 스크립트와 같은 폴더에 있는지 확인해주세요.")
        return
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return

    # 수정된 횟수를 추적하기 위한 변수
    fix_count = 0

    # '영단어' 열이 있는지 확인
    if '영단어' not in df.columns:
        print("오류: CSV 파일에 '영단어' 열이 없습니다.")
        return

    # 각 행을 한번만 순회하며 두 컬럼을 동시에 확인 및 수정
    for index, row in df.iterrows():
        # --- '영단어' 컬럼 처리 ---
        eng_term = str(row['영단어'])
        if '(' in eng_term and ')' not in eng_term:
            fixed_eng_term = eng_term + ')'
            df.at[index, '영단어'] = fixed_eng_term
            fix_count += 1
            print(f"수정됨 (영단어): '{eng_term}' -> '{fixed_eng_term}'")
        
        # --- '한국단어' 컬럼 처리 ---
        kor_term = str(row['한국단어'])
        if '(' in kor_term and ')' not in kor_term:
            fixed_kor_term = kor_term + ')'
            df.at[index, '한국단어'] = fixed_kor_term
            fix_count += 1
            print(f"수정됨 (한국단어): '{kor_term}' -> '{fixed_kor_term}'")

    # 수정된 데이터프레임을 새로운 CSV 파일로 저장
    try:
        df.to_csv(output_file, sep='|', index=False, encoding='utf-8')
        print("\n" + "="*30)
        print(f"총 {fix_count}개의 항목을 수정했습니다.")
        print(f"수정된 데이터가 '{output_file}' 파일로 성공적으로 저장되었습니다.")
        print("="*30)
    except Exception as e:
        print(f"파일을 저장하는 중 오류가 발생했습니다: {e}")

if __name__ == '__main__':
    fix_parentheses_in_csv()