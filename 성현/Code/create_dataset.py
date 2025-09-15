# csv 데이터셋으로 10,000개의 예제를 만드는 코드

import pandas as pd
import random
import re
import json

def create_training_data():
    """
    eng_word.csv 파일을 읽어 LLM 파인튜닝을 위한
    10,000개의 학습 데이터셋(JSONL 형식)을 생성합니다.
    """
    try:
        df = pd.read_csv('eng_word_fixed.csv', delimiter='|')
    except FileNotFoundError:
        print("오류: 'eng_word.csv' 파일을 찾을 수 없습니다.")
        print("스크립트와 동일한 폴더에 파일이 있는지 확인해주세요.")
        return

    # 단어 목록 전처리
    processed_terms = []
    for _, row in df.iterrows():
        eng_word = str(row.get('영단어', '')).strip()
        kor_word = str(row.get('한국단어', '')).strip()
        description = str(row.get('설명', '')).strip()

        if not eng_word or not kor_word or eng_word.lower() == 'nan' or kor_word.lower() == 'nan':
            continue

        clean_desc = ""
        if description.upper() != 'NULL' and description.lower() != 'nan':
            clean_desc = f": {description}"

        terms_to_add = []
        # 괄호 처리: e.g., "NPSH(Net Positive Suction Head)" -> "NPSH", "Net Positive Suction Head"
        match = re.match(r'(.+?)\((.+?)\)(.*)', eng_word)
        if match:
            part1 = (match.group(1) + match.group(3)).strip()
            part2 = (match.group(2) + match.group(3)).strip()
            terms_to_add.append({'eng': part1, 'kor': kor_word, 'desc': clean_desc})
            terms_to_add.append({'eng': part2, 'kor': kor_word, 'desc': clean_desc})
        else:
            terms_to_add.append({'eng': eng_word, 'kor': kor_word, 'desc': clean_desc})
        
        processed_terms.extend(terms_to_add)

    unique_terms = [dict(t) for t in {tuple(d.items()) for d in processed_terms}]

    # 문장 템플릿
    sentence_templates = [
        "이번 프로젝트에서는 {terms} 개념을 이해하는 것이 중요합니다.",
        "선박 설계 시 {terms}의 기준을 반드시 준수해야 합니다.",
        "현장 작업자들은 {terms}에 대한 안전 교육을 받았습니다.",
        "보고서에 따르면, {terms} 부분에서 문제가 발생했습니다.",
        "우리는 {terms} 기술을 도입하여 효율성을 높였습니다.",
        "새로 건조된 선박에는 최신 {terms} 시스템이 장착되어 있습니다.",
        "회의의 주요 안건은 {terms}의 비용 절감 방안이었습니다.",
        "{terms}의 정확한 의미를 아는 사람 있나요?",
        "매뉴얼에 {terms} 관련 내용이 어디에 있는지 찾아봐 주세요.",
        "이 부품은 {terms} 역할을 수행합니다."

        '''
        추가 형식들 -> 실제 test시 활용
        ,
        "{terms}에 대해 더 자세히 설명해주실 수 있나요?",
        "이 문맥에서 {terms}가 의미하는 바는 무엇인가요?",
        "{terms}를 설치하는 표준 절차는 어떻게 되나요?",
        "혹시 {terms}의 대체 부품이 있는지 아시나요?",
        "{terms} 관련 최신 기술 동향을 알려주세요.",
        "설계도에는 {terms}를 사용하도록 명시되어 있습니다.",
        "이번 모델에서는 {terms}의 효율성을 개선하는 데 중점을 두었습니다.",
        "해당 시스템은 {terms}와 유기적으로 연동되어야 합니다.",
        "구조 강도 계산 시 {terms}의 영향을 반드시 고려해야 합니다.",
        "이 다이어그램은 {terms}와 주 기관 사이의 관계를 보여줍니다.",
        "출항 전 {terms}의 상태를 반드시 점검해 주십시오.",
        "정기 검사 중에 {terms}에서 경미한 결함이 발견되었습니다.",
        "안전 규정에 따라 {terms}는 주기적으로 교체해야 합니다.",
        "작업 일지에 {terms}의 오작동이 기록되어 있습니다.",
        "비상 상황 발생 시 {terms}를 수동으로 조작하는 방법을 숙지하세요.",
        "{terms}에서 알 수 없는 경고음이 발생하고 있습니다.",
        "시스템 고장의 주요 원인은 {terms}의 노후화였습니다.",
        "공급업체로부터 {terms} 부품의 리콜 통지를 받았습니다.",
        "악천후로 인해 {terms}에 손상이 발생할 가능성이 있습니다.",
        "현재 {terms}의 재고가 부족하여 작업이 지연되고 있습니다."
        '''
    ]

    # 10,000개 데이터 생성
    with open("training_data_10000.jsonl", "w", encoding="utf-8") as f:
        count = 0
        while count < 10000:
            num_terms = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1], k=1)[0]
            if len(unique_terms) < num_terms: continue
            
            selected_terms = random.sample(unique_terms, num_terms)
            
            question_parts = []
            answers_list = []
            
            for term_data in selected_terms:
                eng = term_data['eng']
                kor = term_data['kor']
                desc = term_data['desc']
                
                if random.choice([True, False]): # 영단어 질문
                    case_choice = random.choice(['lower', 'upper', 'original'])
                    display_term = eng
                    if case_choice == 'lower': display_term = eng.lower()
                    elif case_choice == 'upper': display_term = eng.upper()
                    
                    # 쉼표가 포함된 단어 처리
                    display_term = ', '.join([p.strip() for p in display_term.split(',')])
                    
                    question_parts.append(display_term)
                    answers_list.append({
                        "term": display_term,
                        "definition": f"{kor}{desc}"
                    })
                else: # 한글 단어 질문
                    question_parts.append(kor)
                    answers_list.append({
                        "term": kor,
                        "definition": f"{eng}{desc}"
                    })

            terms_str = "와(과) ".join(question_parts)
            sentence = random.choice(sentence_templates).format(terms=terms_str)
            
            json_line = json.dumps({
                "question": sentence,
                "answers": answers_list
            }, ensure_ascii=False)
            
            f.write(json_line + "\n")
            count += 1
            
    print("성공: 10,000개의 학습 데이터가 'training_data_10000.jsonl' 파일로 저장되었습니다.")

if __name__ == '__main__':
    create_training_data()