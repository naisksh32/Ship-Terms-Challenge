# csv 데이터셋으로 10,000개의 예제를 만드는 코드

import pandas as pd
import random
import re
import json

def is_hanja(text):
    """
    주어진 문자열이 공백을 제외하고 한자(CJK Unified Ideographs)로만 
    구성되어 있는지 확인하는 함수.
    """
    # 비어있는 문자열은 한자가 아님
    if not text:
        return False
    
    for char in text:
        # 공백은 무시
        if char.isspace():
            continue
        # CJK 한자 유니코드 범위 (U+4E00 ~ U+9FFF)에 속하는지 확인
        if not ('\u4e00' <= char <= '\u9fff'):
            return False # 한자가 아닌 문자가 하나라도 있으면 False
            
    return True # 모든 문자가 한자 범위에 속하면 True

def create_training_data():
    """
    eng_word.csv 파일을 읽어 LLM 파인튜닝을 위한
    10,000개의 학습 데이터셋(JSONL 형식)을 생성합니다.
    """
    # 파일 불러오기
    try:
        df = pd.read_csv('eng_word_fixed.csv', delimiter='|')
    except FileNotFoundError:
        print("오류: 'eng_word_fixed.csv' 파일을 찾을 수 없습니다.")
        print("스크립트와 동일한 폴더에 파일이 있는지 확인해주세요.")
        return

    # 두 종류의 테스트 셋을 담을 리스트 초기화
    test_set_forQ = []  # Q: 영단어 (괄호 제외), A: 한국단어
    test_set_forA = []  # Q: 한국단어, A: 영단어 (괄호 포함 원본)


    # 단어 목록 전처리
    # 사전 DF 파일을 한행 한행 반복하며
    for _, row in df.iterrows():
        # -------------------- 유효성 검사 영역 -------------------------
        # 영단어, 한국단어, 설명 분리 (해당 문자가 없으면 ''불러옴) // .strip() 단어간 공백 제거
        eng_word = str(row.get('영단어', '')).strip()
        kor_word = str(row.get('한국단어', '')).strip()
        # description = str(row.get('설명', '')).strip()

        # 영단어나, 한국단어가 'nan' 혹은 없으면 해당 행은 PASS
        if not eng_word or not kor_word or eng_word.lower() == 'nan' or kor_word.lower() == 'nan':
            continue
        # ----------------------------------------------------------------
        # # ------------------- 설명 데이터 정제 ---------------------------
        # clean_desc = ""
        # # 만약 설명 내용이 NULL이거나 null이 아니면 그대로 설명
        # if description.upper() != 'NULL' and description.lower() != 'nan':
        #     clean_desc = f": {description}"
        # # ----------------------------------------------------------------

        # ---------------------------- 데이터 증강(괄호 처리) ------------------------------
        # 이상한 특수 기호가 들어가면 re모듈 정규화 방식 진행
        # 괄호 처리: e.g., "NPSH(Net Positive Suction Head)" -> "NPSH", "Net Positive Suction Head"
        match1 = re.match(r'(.+?)\((.+?)\)(.*)', eng_word)
        match2 = re.match(r'(.+?)\((.+?)\)(.*)', kor_word)

        # 괄호 패턴 유무와 상관없이 사용할 변수 미리 정의
        eng_a = eng_word # 기본값은 원본 영단어
        kor_q = kor_word # 기본값은 원본 한국단어

        # 영단어 처리
        if match1:
            # 1. 괄호 밖 텍스트
            part_outside = (match1.group(1) + match1.group(3)).strip()
            # 2. 괄호 안 텍스트
            part_inside = match1.group(2).strip()
            
            # 두 가지 버전을 모두 test_set_forQ에 추가
            test_set_forQ.append({'question': part_outside, 'answer': kor_word})
            test_set_forQ.append({'question': part_inside, 'answer': kor_word})
    
        # 영단어에 괄호가 없는 경우 -> 원본 그대로 추가
        else:
            test_set_forQ.append({'question': eng_word, 'answer': kor_word})


        # 한국단어 한자 처리
        if match2:
            # 괄호 안의 순수한 내용을 추출
            content_inside = match2.group(2).strip()
    
            # 괄호 안 내용이 한자인지 판별
            if is_hanja(content_inside):
                # 한자이면 괄호와 내용을 제거
                kor_q = (match2.group(1) + match2.group(3)).strip()
            # else: 한자가 아니면 아무것도 하지 않음 (kor_q는 원본 kor_word 값을 유지)

        # 테스트 셋 2 생성
        test_set_forA.append({'question': kor_q, 'answer': eng_a})
    # -----------------------------------------------------------------------------------

    # # --- 결과 확인 ---
    # print("--- 테스트 셋 1 (Q: 영어 약어 -> A: 한국어) ---")
    # for item in test_set_forQ[:5]: # 처음 5개만 출력
    #     print(item)

    # print("\n" + "="*50 + "\n")

    # print("--- 테스트 셋 2 (Q: 한국어 -> A: 영어 원본) ---")
    # for item in test_set_forA[:5]: # 처음 5개만 출력
    #     print(item)

    # -------------------------- 데이터 추출 --------------------------------------------
    # 1. 한글-영어 문장 템플릿 쌍을 정의합니다. (한글, 영어 순서)
    #    두 문장은 서로 번역 관계여야 합니다.
    # 기존 sentence_templates (성현) 주석 처리
    # sentence_templates = [
    #     ("매뉴얼에 {term} 관련 내용이 어디에 있는지 찾아봐 주세요.", "Please look for information about {term} in the manual."),
    #     ("이번 프로젝트에서는 {term} 개념을 이해하는 것이 중요합니다.", "It is important to understand the concept of {term} in this project."),
    #     ("보고서에 따르면, {term} 부분에서 문제가 발생했습니다.", "According to the report, a problem occurred in the {term} section."),
    #     ("선박 설계 시 {term}의 기준을 반드시 준수해야 합니다.", "The standards for {term} must be strictly followed when designing a ship."),
    #     ("회의의 주요 안건은 {term}의 비용 절감 방안이었습니다.", "The main agenda of the meeting was how to reduce the cost of the {term}."),
    #     ("새로 건조된 선박에는 최신 {term} 시스템이 장착되어 있습니다.", "The newly built ship is equipped with the latest {term} system."),
    #     ("출항 전 {term}의 상태를 반드시 점검해 주십시오.", "Please be sure to check the status of the {term} before departure."),
    #     ("해당 시스템은 {term}와 유기적으로 연동되어야 합니다.", "The system must be organically linked with the {term}."),
    # ]

    sentence_templates = [
    ("오늘 용접은 {term}에 지정된 전류값을 그대로 적용해 주세요.", "Apply the welding current exactly as specified in the {term} today."),
    ("도장 두께는 {term} 기준에 맞춰 다시 측정해 주세요.", "Re-measure the coating thickness to meet the {term} standard."),
    ("부식 방지를 위해 {term} 출력 전류 기록을 남겨 주세요.", "Record the output current for the {term} to prevent corrosion."),
    ("관통부 시공은 {term} 규격에 맞춰 체결해 주세요.", "Tighten the penetration assembly according to the {term} specification."),
    ("항해 전 {term} 업데이트 상태를 확인해 주세요.", "Check the update status of the {term} before sailing."),
    ("운항 데이터는 {term}에 정상 기록되는지 점검해 주세요.", "Verify that the voyage data is being recorded correctly on the {term}."),
    ("무선 설비는 {term} 점검표에 따라 확인해 주세요.", "Inspect the radio equipment according to the {term} checklist."),
    ("부하 증설 전 {term} 여유 용량을 검토해 주세요.", "Review spare capacity on the {term} before adding new loads."),
    ("구동 전 {term} 내부 단자 체결 상태를 확인해 주세요.", "Check terminal tightness inside the {term} before operation."),
    ("격리 작업은 {term} 절차에 따라 표지 부착까지 완료해 주세요.", "Complete isolation work under the {term} procedure including tagging."),
    ("부두 시운전은 {term} 항목 순서대로 진행해 주세요.", "Carry out quay commissioning in the order of the {term} items."),
    ("해상 시운전은 {term} 계획표대로 시작해 주세요.", "Start sea trials according to the {term} schedule."),
    ("공급업체 입고 시 {term} 성적서를 함께 제출해 주세요.", "Submit the {term} report upon vendor delivery."),
    ("프로펠러 피칭은 {term} 제어 신호 범위 내에서 시험해 주세요.", "Test propeller pitch within the control range of the {term}."),
    ("복원성 검토에서 {term} 값 계산을 다시 확인해 주세요.", "Recheck the {term} value in the stability assessment."),
    ("무게중심 변경 시 {term} 데이터 시트를 갱신해 주세요.", "Update the {term} datasheet when the center of gravity changes."),
    ("판재 두께는 {term} 결과표를 기준으로 판단해 주세요.", "Judge plating thickness based on the {term} results sheet."),
    ("밸러스트 처리는 {term} 운전 지침을 준수해 주세요.", "Follow the {term} operating instructions for ballast treatment."),
    ("배출 규정은 {term} 요구사항에 맞춰 이행해 주세요.", "Implement emissions control in accordance with {term} requirements."),
    ("안전 설비는 {term} 점검 항목대로 확인해 주세요.", "Check safety equipment according to {term} inspection items."),
    ("도면 코멘트는 {term} 지적사항을 우선 반영해 주세요.", "Address {term} comments on the drawings as a priority."),
    ("검사 대응은 {term} 요구 문서 양식으로 제출해 주세요.", "Submit inspection responses using the {term} document format."),
    ("승인 자료는 {term} 양식에 맞춰 정리해 주세요.", "Prepare approval documents in the {term} format."),
    ("연비 평가는 {term} 계산서를 근거로 보고해 주세요.", "Report energy efficiency based on the {term} calculation sheet."),
    ("운항 지표는 {term} 연간 목표치와 비교해 주세요.", "Compare operating metrics with the annual {term} target."),
    ("비상정지는 {term} 로직에 따라 단계별로 검증해 주세요.", "Verify emergency shutdown step-by-step under the {term} logic."),
    ("압력 시험은 {term} 조건을 준수해 수행해 주세요.", "Perform the pressure test in accordance with the {term} conditions."),
    ("비파괴 검사는 {term} 작업 지침서에 따라 진행해 주세요.", "Carry out non-destructive testing in line with the {term} work instruction."),
    ("두께 검사는 {term} 장비 교정 후 측정해 주세요.", "Measure thickness using the {term} device after calibration."),
    ("용접부 검사는 {term} 결과가 나오면 즉시 공유해 주세요.", "Share the results as soon as the {term} on the welds is available."),
    ("자분 검사는 {term} 기준 합격치에 따라 판정해 주세요.", "Evaluate the magnetic particle test using the {term} acceptance criteria."),
    ("표면 처리는 {term} 등급 달성 여부만 확인해 주세요.", "Check only whether the surface preparation meets the {term} grade."),
    ("도막 두께는 {term} 목표값을 넘어가지 않도록 관리해 주세요.", "Control coating so the {term} target is not exceeded."),
    ("방폭 구역은 {term} 표기와 동일하게 시공해 주세요.", "Construct hazardous areas in accordance with the {term} marking."),
    ("엔클로저는 {term} 보호 등급을 만족해야 합니다.", "Ensure the enclosure meets the {term} protection rating."),
    ("관통부 보강은 {term} 요구 조건에 맞춰 시공해 주세요.", "Build the penetration reinforcement to meet the {term} requirement."),
    ("퍼지 공정은 {term} 유량과 시간 조건을 지켜 주세요.", "Maintain the specified flow and duration for the {term} purging process."),
    ("전자해도는 {term} 갱신 로그를 확인해 주세요.", "Check the update log for the {term}."),
    ("센서 보정은 {term} 기준값에 맞춰 조정해 주세요.", "Adjust sensor calibration to the {term} reference value."),
    ("선급 대응은 {term} 서식으로 작성해 주세요.", "Prepare class responses using the {term} form."),
]



    # --- 유형 1: 한글 문장(Q) -> 영문 문장(A) ---
    test_data_type_KtoE = []
    # test_set_forA (Q:한글, A:영문)를 순회
    for item in test_set_forA:
        kor_term = item['question']
        eng_term = item['answer']
        
        # 랜덤으로 한/영 템플릿 쌍을 선택
        kor_template, eng_template = random.choice(sentence_templates)
        
        # 템플릿에 단어를 삽입하여 Q와 A를 생성
        question = kor_template.format(term=kor_term)
        answer = eng_template.format(term=eng_term)
        
        test_data_type_KtoE.append({'question': question, 'answer': answer})


    # --- 유형 2: 영문 단어(Q) -> 한글 문장(A) ---
    test_data_type_EtoK = []
    # test_set_forQ (Q:영문, A:한글)를 순회
    for item in test_set_forQ:
        eng_term = item['question']
        kor_term = item['answer']
        
        # 랜덤으로 한글 템플릿만 선택
        kor_template, eng_template = random.choice(sentence_templates)
        
        # Q는 영문 단어 그대로, A는 템플릿에 한글 단어를 삽입하여 생성
        question = eng_template.format(term=eng_term)
        answer = kor_template.format(term=kor_term)
        
        test_data_type_EtoK.append({'question': question, 'answer': answer})


    # 최종 데이터 합본 및 저장
    total_test_data = test_data_type_KtoE + test_data_type_EtoK
    random.shuffle(total_test_data)

    # ▶ 여기서 무작위 1,000~2,000개만 추출
    n_min, n_max = 1000, 2000
    upper = min(n_max, len(total_test_data))
    lower = min(n_min, upper)           # 데이터가 1,000 미만이면 가능한 최대치로
    n_pick = random.randint(lower, upper) if upper > 0 else 0

    subset = total_test_data[:n_pick]    # 이미 셔플됨 → 앞에서 n개 슬라이스

    with open("test_data.jsonl", "w", encoding="utf-8") as f:
        for item in subset:
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + '\n')
    print('jsonl 파일로 저장 완료')


    # # 문장 템플릿
    # sentence_templates = [
    #     "이번 프로젝트에서는 {terms} 개념을 이해하는 것이 중요합니다.",
    #     "선박 설계 시 {terms}의 기준을 반드시 준수해야 합니다.",
    #     "현장 작업자들은 {terms}에 대한 안전 교육을 받았습니다.",
    #     "보고서에 따르면, {terms} 부분에서 문제가 발생했습니다.",
    #     "우리는 {terms} 기술을 도입하여 효율성을 높였습니다.",
    #     "새로 건조된 선박에는 최신 {terms} 시스템이 장착되어 있습니다.",
    #     "회의의 주요 안건은 {terms}의 비용 절감 방안이었습니다.",
    #     "{terms}의 정확한 의미를 아는 사람 있나요?",
    #     "매뉴얼에 {terms} 관련 내용이 어디에 있는지 찾아봐 주세요.",
    #     "이 부품은 {terms} 역할을 수행합니다."

    #     '''
    #     추가 형식들 -> 실제 test시 활용
    #     ,
    #     "{terms}에 대해 더 자세히 설명해주실 수 있나요?",
    #     "이 문맥에서 {terms}가 의미하는 바는 무엇인가요?",
    #     "{terms}를 설치하는 표준 절차는 어떻게 되나요?",
    #     "혹시 {terms}의 대체 부품이 있는지 아시나요?",
    #     "{terms} 관련 최신 기술 동향을 알려주세요.",
    #     "설계도에는 {terms}를 사용하도록 명시되어 있습니다.",
    #     "이번 모델에서는 {terms}의 효율성을 개선하는 데 중점을 두었습니다.",
    #     "해당 시스템은 {terms}와 유기적으로 연동되어야 합니다.",
    #     "구조 강도 계산 시 {terms}의 영향을 반드시 고려해야 합니다.",
    #     "이 다이어그램은 {terms}와 주 기관 사이의 관계를 보여줍니다.",
    #     "출항 전 {terms}의 상태를 반드시 점검해 주십시오.",
    #     "정기 검사 중에 {terms}에서 경미한 결함이 발견되었습니다.",
    #     "안전 규정에 따라 {terms}는 주기적으로 교체해야 합니다.",
    #     "작업 일지에 {terms}의 오작동이 기록되어 있습니다.",
    #     "비상 상황 발생 시 {terms}를 수동으로 조작하는 방법을 숙지하세요.",
    #     "{terms}에서 알 수 없는 경고음이 발생하고 있습니다.",
    #     "시스템 고장의 주요 원인은 {terms}의 노후화였습니다.",
    #     "공급업체로부터 {terms} 부품의 리콜 통지를 받았습니다.",
    #     "악천후로 인해 {terms}에 손상이 발생할 가능성이 있습니다.",
    #     "현재 {terms}의 재고가 부족하여 작업이 지연되고 있습니다."
    #     '''
    # ]

    # # 10,000개 데이터 생성
    

if __name__ == '__main__':
    create_training_data()