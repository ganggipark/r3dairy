# n8n 설문 템플릿 - 개인화 다이어리 시스템

## 📋 설문 구조 개요

이 설문은 사주/기문둔갑 계산과 개인 성향을 결합하여 **완전히 개인화된 다이어리**를 만들기 위한 항목입니다.

---

## 1️⃣ 기본 정보 (필수)

### Q1. 이름
- **Field Type**: Text Input (단답형)
- **Field Name**: `name`
- **Required**: Yes
- **Example**: 김철수

### Q2. 이메일
- **Field Type**: Email
- **Field Name**: `email`
- **Required**: Yes
- **Example**: example@email.com

### Q3. 생년월일
- **Field Type**: Date
- **Field Name**: `birth_date`
- **Required**: Yes
- **Format**: YYYY-MM-DD
- **Example**: 1995-05-15
- **설명**: 사주/기문둔갑 계산에 사용됩니다

### Q4. 출생 시간 (선택)
- **Field Type**: Time or Text
- **Field Name**: `birth_time`
- **Required**: No
- **Format**: HH:MM (24시간 형식)
- **Example**: 14:30
- **설명**: 정확한 시간을 모르시면 비워두세요

### Q5. 성별
- **Field Type**: Radio Button (단일 선택)
- **Field Name**: `gender`
- **Required**: Yes
- **Options**:
  - 남성
  - 여성

---

## 2️⃣ 역할 선택 (필수)

### Q6. 당신의 현재 주요 역할은 무엇인가요?
- **Field Type**: Radio Button (단일 선택)
- **Field Name**: `primary_role`
- **Required**: Yes
- **Options**:
  - `student` - 학생 (초/중/고/대학생, 대학원생)
  - `office_worker` - 직장인 (회사원, 공무원)
  - `freelancer` - 자영업자/프리랜서 (개인사업, 프리랜서)
  - `parent` - 주부/육아 (전업주부, 육아 중)

---

## 3️⃣ 성격 특성 (필수)

**각 항목에 대해 1~5점으로 평가해주세요**
- 1 = 전혀 아니다
- 2 = 아니다
- 3 = 보통이다
- 4 = 그렇다
- 5 = 매우 그렇다

### Q7. 외향성: 사람들과 어울리는 것을 좋아한다
- **Field Name**: `p_extroversion`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q8. 계획성: 일정을 체계적으로 관리하는 편이다
- **Field Name**: `p_structured`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q9. 개방성: 새로운 경험을 추구하는 편이다
- **Field Name**: `p_openness`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q10. 공감능력: 다른 사람의 감정을 잘 이해한다
- **Field Name**: `p_empathy`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q11. 침착성: 스트레스 상황에서도 침착하다
- **Field Name**: `p_calm`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q12. 집중력: 한 가지 일에 오래 집중할 수 있다
- **Field Name**: `p_focus`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q13. 창의성: 창의적인 아이디어를 내는 것을 즐긴다
- **Field Name**: `p_creative`
- **Type**: Scale (1-5)
- **Required**: Yes

### Q14. 논리성: 논리적으로 분석하고 판단한다
- **Field Name**: `p_logical`
- **Type**: Scale (1-5)
- **Required**: Yes

---

## 4️⃣ 관심 주제 (필수)

### Q15. 다이어리에서 다루고 싶은 주제를 모두 선택해주세요
- **Field Type**: Checkbox (다중 선택)
- **Field Name**: `topics`
- **Required**: Yes (최소 1개)
- **Options**:
  - 건강
  - 관계
  - 학습
  - 일/업무
  - 창작
  - 재정
  - 감정
  - 자기계발

---

## 5️⃣ 콘텐츠 스타일 선호 (필수)

### Q16. 선호하는 조언 톤은 무엇인가요?
- **Field Type**: Radio Button
- **Field Name**: `tone_preference`
- **Required**: Yes
- **Options**:
  - 친근한 조언자 (편안하고 공감적인 톤)
  - 전문 컨설턴트 (논리적이고 분석적인 톤)
  - 멘토/코치 (동기부여와 격려 중심)

---

## 6️⃣ 활동 세분화 (조건부 - 역할에 따라 다름)

### 🎓 학생인 경우 (Q6에서 `student` 선택 시)

#### Q17-1. 주로 하는 학습 활동을 모두 선택해주세요
- **Field Name**: `study_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 시험 준비
  - 프로젝트
  - 독서
  - 자격증
  - 어학

#### Q17-2. 주로 하는 운동을 모두 선택해주세요
- **Field Name**: `student_exercise_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 러닝
  - 헬스
  - 요가
  - 수영
  - 팀스포츠

#### Q17-3. 주로 하는 사회 활동을 모두 선택해주세요
- **Field Name**: `student_social_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 스터디그룹
  - 동아리
  - 멘토링
  - 친구모임

---

### 💼 직장인인 경우 (Q6에서 `office_worker` 선택 시)

#### Q18-1. 주로 하는 업무 유형을 모두 선택해주세요
- **Field Name**: `work_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 보고서/기획
  - 회의/소통
  - 분석/리서치
  - 프레젠테이션
  - 프로젝트관리

#### Q18-2. 주로 하는 운동을 모두 선택해주세요
- **Field Name**: `office_exercise_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 러닝
  - 헬스
  - 요가
  - 등산
  - 골프

#### Q18-3. 주로 하는 사회 활동을 모두 선택해주세요
- **Field Name**: `office_social_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 팀빌딩
  - 네트워킹
  - 멘토링
  - 회식

---

### 🎨 자영업자/프리랜서인 경우 (Q6에서 `freelancer` 선택 시)

#### Q19-1. 주로 하는 일의 유형을 모두 선택해주세요
- **Field Name**: `freelance_work_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 창작/디자인
  - 클라이언트미팅
  - 기획/제안
  - 마감작업
  - 자기계발

#### Q19-2. 주로 하는 운동을 모두 선택해주세요
- **Field Name**: `freelance_exercise_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 러닝
  - 헬스
  - 요가
  - 수영
  - 자전거

#### Q19-3. 주로 하는 사회 활동을 모두 선택해주세요
- **Field Name**: `freelance_social_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 콜라보
  - 커뮤니티
  - 워크샵
  - 네트워킹

---

### 👶 주부/육아인 경우 (Q6에서 `parent` 선택 시)

#### Q20-1. 주로 하는 활동을 모두 선택해주세요
- **Field Name**: `parent_activity_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 육아
  - 가사
  - 자기계발
  - 운동
  - 취미

#### Q20-2. 주로 하는 운동을 모두 선택해주세요
- **Field Name**: `parent_exercise_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 걷기
  - 요가
  - 필라테스
  - 수영
  - 홈트레이닝

#### Q20-3. 주로 하는 사회 활동을 모두 선택해주세요
- **Field Name**: `parent_social_type`
- **Type**: Checkbox (다중 선택)
- **Options**:
  - 부모모임
  - 가족시간
  - 친구만남
  - 봉사활동

---

## 7️⃣ 다이어리 사용 방식 (필수)

### Q21. 다이어리를 어떻게 사용하실 예정인가요?
- **Field Type**: Radio Button
- **Field Name**: `diary_preference`
- **Required**: Yes
- **Options**:
  - 앱 전용 (웹/모바일 앱으로만 사용)
  - 앱 + 종이 (앱과 인쇄본 병행)
  - 종이 전용 (인쇄본 다이어리만 사용)

---

## 8️⃣ 개인정보 동의 (필수)

### Q22. 개인정보 수집 및 이용 동의
- **Field Type**: Checkbox (단일)
- **Field Name**: `privacy_consent`
- **Required**: Yes
- **Label**: 개인정보 수집 및 이용에 동의합니다
- **설명**: 수집된 정보는 맞춤형 다이어리 제공 목적으로만 사용됩니다

### Q23. 마케팅 정보 수신 동의 (선택)
- **Field Type**: Checkbox (단일)
- **Field Name**: `marketing_consent`
- **Required**: No
- **Label**: 이벤트 및 할인 정보 수신에 동의합니다

---

## 📤 n8n Webhook 전송 형식

설문 완료 후 다음 형식으로 webhook에 전송하세요:

```json
{
  "survey_id": "survey_default_001",
  "submission_id": "n8n_{{$now}}",
  "response_data": {
    "name": "{{name}}",
    "email": "{{email}}",
    "birth_date": "{{birth_date}}",
    "birth_time": "{{birth_time}}",
    "gender": "{{gender}}",
    "primary_role": "{{primary_role}}",
    "p_extroversion": {{p_extroversion}},
    "p_structured": {{p_structured}},
    "p_openness": {{p_openness}},
    "p_empathy": {{p_empathy}},
    "p_calm": {{p_calm}},
    "p_focus": {{p_focus}},
    "p_creative": {{p_creative}},
    "p_logical": {{p_logical}},
    "topics": {{topics}},
    "tone_preference": "{{tone_preference}}",

    // 역할별 활동 (조건부)
    "study_type": {{study_type}},
    "student_exercise_type": {{student_exercise_type}},
    "student_social_type": {{student_social_type}},

    "work_type": {{work_type}},
    "office_exercise_type": {{office_exercise_type}},
    "office_social_type": {{office_social_type}},

    "freelance_work_type": {{freelance_work_type}},
    "freelance_exercise_type": {{freelance_exercise_type}},
    "freelance_social_type": {{freelance_social_type}},

    "parent_activity_type": {{parent_activity_type}},
    "parent_exercise_type": {{parent_exercise_type}},
    "parent_social_type": {{parent_social_type}},

    "diary_preference": "{{diary_preference}}",
    "privacy_consent": {{privacy_consent}},
    "marketing_consent": {{marketing_consent}}
  },
  "metadata": {
    "n8n_workflow_id": "{{$workflow.id}}",
    "n8n_execution_id": "{{$execution.id}}",
    "submitted_at": "{{$now}}"
  }
}
```

---

## 🎯 설문 완료 후 자동 처리

1. **프로필 자동 생성**
   - 생년월일 → 사주/기문둔갑 계산
   - 성격 점수 → Personality Profile (0-100 scale)
   - 활동 선호도 추출

2. **첫 다이어리 페이지 생성**
   - 오늘 날짜 기준 맞춤 콘텐츠
   - 역할별 표현 변환
   - 400-1200자 최적화

3. **환영 이메일 발송** (선택)
   - 프로필 생성 완료 안내
   - 첫 다이어리 PDF 첨부

---

## 💡 설문 작성 팁

### 조건부 로직 (n8n IF 노드 사용)
```
IF primary_role == "student"
  → Q17-1, Q17-2, Q17-3 표시
ELSE IF primary_role == "office_worker"
  → Q18-1, Q18-2, Q18-3 표시
ELSE IF primary_role == "freelancer"
  → Q19-1, Q19-2, Q19-3 표시
ELSE IF primary_role == "parent"
  → Q20-1, Q20-2, Q20-3 표시
```

### 필수 검증
- 이름, 이메일, 생년월일, 성별은 **필수**
- 성격 특성 8개 모두 **필수**
- 관심 주제 최소 1개 **필수**
- 개인정보 동의 **필수**

### 선택 항목
- 출생 시간 (모르면 비워둠 → 날짜만으로 계산)
- 마케팅 동의

---

## 🔗 다음 단계

1. **n8n에서 이 템플릿으로 폼 생성**
2. **Webhook 노드 설정**
   - URL: `http://your-backend:8000/api/webhooks/n8n/survey`
   - Method: POST
   - Body: 위 JSON 형식
3. **테스트 제출**
4. **Supabase에서 프로필 확인**
5. **첫 PDF 다이어리 생성**

---

## 📞 문의

설문 구성이나 webhook 연동에 문제가 있으면 `backend/src/api/WEBHOOK_README.md`를 참고하세요.
