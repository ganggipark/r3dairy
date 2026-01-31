# n8n 상세 설문 템플릿 - 완전 개인화 다이어리 시스템

## 📋 설문 개요

**총 50+ 질문**으로 구성된 초개인화 설문지입니다.
- 기본 정보부터 일상 패턴, 선호 시간대, 에너지 타입까지 상세하게 파악
- 사주/기문둥갑 계산 + 개인 성향 + 생활 패턴을 모두 결합
- **당신만을 위한 유일무이한 다이어리** 생성

---

# PART 1: 기본 정보 (필수)

## 섹션 A: 신원 정보

### Q1. 이름 (실명)
- **Field Name**: `name`
- **Type**: Text
- **Required**: Yes
- **Example**: 김철수
- **용도**: 개인화된 인사말, PDF 다이어리 표지

### Q2. 이메일 주소
- **Field Name**: `email`
- **Type**: Email
- **Required**: Yes
- **Example**: chulsoo.kim@example.com
- **용도**: 계정 생성, PDF 발송

### Q3. 휴대폰 번호 (선택)
- **Field Name**: `phone`
- **Type**: Text
- **Required**: No
- **Format**: 010-1234-5678
- **용도**: 중요 알림 (선택 시)

---

## 섹션 B: 사주 계산 정보 (매우 중요!)

### Q4. 생년월일
- **Field Name**: `birth_date`
- **Type**: Date
- **Required**: Yes
- **Format**: YYYY-MM-DD
- **Example**: 1995-05-15
- **설명**: 사주 팔자의 기본이 되는 정보입니다

### Q5. 출생 시간 (정확한 시간)
- **Field Name**: `birth_time`
- **Type**: Time
- **Required**: No (하지만 강력 권장)
- **Format**: HH:MM (24시간)
- **Example**: 14:30
- **설명**:
  - 시주(時柱)를 포함한 정확한 사주 계산
  - 모르시면 "출생 증명서" 또는 "부모님께 확인"
  - 정말 모르시면 비워두세요 (날짜만으로도 70% 정확도)

### Q6. 출생 지역 (시간대 보정용)
- **Field Name**: `birth_location`
- **Type**: Text
- **Required**: No
- **Example**: 서울, 부산, 제주
- **설명**: 진태양시 계산에 사용 (더 정확한 시주 계산)

### Q7. 성별
- **Field Name**: `gender`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 남성
  - 여성
- **용도**: 대운(大運) 계산 방향

### Q8. 양력/음력 여부
- **Field Name**: `calendar_type`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 양력
  - 음력 (평달)
  - 음력 (윤달)
- **설명**: 생년월일이 양력인지 음력인지 선택

---

# PART 2: 역할 및 상황 (필수)

## 섹션 C: 주요 역할

### Q9. 현재 주요 역할은 무엇인가요?
- **Field Name**: `primary_role`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - `student` - 학생 (초/중/고/대학생, 대학원생)
  - `office_worker` - 직장인 (회사원, 공무원)
  - `freelancer` - 자영업자/프리랜서
  - `parent` - 주부/육아
  - `job_seeker` - 구직자/취업준비생
  - `retired` - 은퇴자/휴식기

### Q10. 부가 역할 (있다면 선택, 다중)
- **Field Name**: `secondary_roles`
- **Type**: Checkbox
- **Required**: No
- **Options**:
  - 학생 + 아르바이트
  - 직장인 + 사이드 프로젝트
  - 부모 + 재택근무
  - 창작자/블로거
  - 운동선수/트레이너
  - 종교인/봉사자

---

## 섹션 D: 직업 상세 (조건부)

### Q11. 구체적인 직업/전공은?
- **Field Name**: `occupation_detail`
- **Type**: Text
- **Required**: No
- **Example**: 소프트웨어 개발자, 마케터, 간호사, 건축학과
- **용도**: 더욱 세밀한 조언 커스터마이징

### Q12. 직장/학교 규모
- **Field Name**: `organization_size`
- **Type**: Radio
- **Required**: No
- **Options**:
  - 소규모 (10명 미만)
  - 중소 (10-100명)
  - 중견 (100-500명)
  - 대기업 (500명 이상)
  - 개인 (프리랜서/자영업)

### Q13. 근무/학습 형태
- **Field Name**: `work_style`
- **Type**: Radio
- **Required**: No
- **Options**:
  - 전일 대면 (사무실/학교 출근)
  - 재택/원격
  - 하이브리드 (사무실+재택)
  - 프리랜서 (시간 자율)
  - 시프트 근무

---

# PART 3: 성격 및 심리 특성 (매우 상세)

## 섹션 E: 기본 성격 (1-5 척도)

**각 항목을 1~5점으로 평가해주세요**
- 1 = 전혀 아니다
- 2 = 아니다
- 3 = 보통이다
- 4 = 그렇다
- 5 = 매우 그렇다

### Q14. 외향성: 사람들과 어울리는 것을 좋아한다
- **Field Name**: `p_extroversion`
- **Type**: Scale 1-5
- **Required**: Yes

### Q15. 계획성: 일정을 체계적으로 관리하는 편이다
- **Field Name**: `p_structured`
- **Type**: Scale 1-5
- **Required**: Yes

### Q16. 개방성: 새로운 경험을 추구하는 편이다
- **Field Name**: `p_openness`
- **Type**: Scale 1-5
- **Required**: Yes

### Q17. 공감능력: 다른 사람의 감정을 잘 이해한다
- **Field Name**: `p_empathy`
- **Type**: Scale 1-5
- **Required**: Yes

### Q18. 침착성: 스트레스 상황에서도 침착하다
- **Field Name**: `p_calm`
- **Type**: Scale 1-5
- **Required**: Yes

### Q19. 집중력: 한 가지 일에 오래 집중할 수 있다
- **Field Name**: `p_focus`
- **Type**: Scale 1-5
- **Required**: Yes

### Q20. 창의성: 창의적인 아이디어를 내는 것을 즐긴다
- **Field Name**: `p_creative`
- **Type**: Scale 1-5
- **Required**: Yes

### Q21. 논리성: 논리적으로 분석하고 판단한다
- **Field Name**: `p_logical`
- **Type**: Scale 1-5
- **Required**: Yes

---

## 섹션 F: 행동 패턴 (추가 성격)

### Q22. 완벽주의: 일을 완벽하게 해야 마음이 편하다
- **Field Name**: `p_perfectionism`
- **Type**: Scale 1-5
- **Required**: Yes

### Q23. 리스크 감수: 위험을 감수하고 도전하는 편이다
- **Field Name**: `p_risk_taking`
- **Type**: Scale 1-5
- **Required**: Yes

### Q24. 자기주장: 내 의견을 명확히 표현한다
- **Field Name**: `p_assertiveness`
- **Type**: Scale 1-5
- **Required**: Yes

### Q25. 유연성: 계획이 바뀌어도 빠르게 적응한다
- **Field Name**: `p_flexibility`
- **Type**: Scale 1-5
- **Required**: Yes

### Q26. 낙관성: 긍정적으로 생각하는 편이다
- **Field Name**: `p_optimism`
- **Type**: Scale 1-5
- **Required**: Yes

### Q27. 독립성: 혼자서도 일을 잘 처리한다
- **Field Name**: `p_independence`
- **Type**: Scale 1-5
- **Required**: Yes

---

## 섹션 G: 에너지 타입

### Q28. 당신의 에너지 패턴은?
- **Field Name**: `energy_pattern`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 아침형 인간 (오전에 에너지 최고)
  - 저녁형 인간 (밤에 에너지 최고)
  - 오후형 (점심 이후 활발)
  - 불규칙형 (날마다 다름)

### Q29. 에너지 충전 방식은?
- **Field Name**: `energy_recharge`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 혼자 있을 때 충전 (내향적 충전)
  - 사람들과 있을 때 충전 (외향적 충전)
  - 활동할 때 충전 (운동, 취미)
  - 휴식할 때 충전 (수면, 명상)

### Q30. 스트레스 대처 방식
- **Field Name**: `stress_coping`
- **Type**: Checkbox (다중 선택)
- **Required**: Yes
- **Options**:
  - 운동
  - 수면
  - 친구와 대화
  - 취미 활동
  - 혼자만의 시간
  - 음식/음료
  - 쇼핑
  - 여행/외출

---

# PART 4: 일상 패턴 및 생활 습관

## 섹션 H: 수면 패턴

### Q31. 평일 평균 취침 시간
- **Field Name**: `weekday_bedtime`
- **Type**: Time
- **Required**: Yes
- **Example**: 23:30

### Q32. 평일 평균 기상 시간
- **Field Name**: `weekday_waketime`
- **Type**: Time
- **Required**: Yes
- **Example**: 07:00

### Q33. 주말 평균 취침 시간
- **Field Name**: `weekend_bedtime`
- **Type**: Time
- **Required**: Yes
- **Example**: 01:00

### Q34. 주말 평균 기상 시간
- **Field Name**: `weekend_waketime`
- **Type**: Time
- **Required**: Yes
- **Example**: 09:00

### Q35. 수면 품질
- **Field Name**: `sleep_quality`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 매우 좋음 (숙면)
  - 좋음
  - 보통
  - 나쁨 (자주 깸)
  - 매우 나쁨 (불면증)

---

## 섹션 I: 시간 활용 패턴

### Q36. 하루 중 가장 생산적인 시간대 (다중 선택)
- **Field Name**: `productive_hours`
- **Type**: Checkbox
- **Required**: Yes
- **Options**:
  - 새벽 (05:00-07:00)
  - 오전 (07:00-12:00)
  - 점심 (12:00-14:00)
  - 오후 (14:00-18:00)
  - 저녁 (18:00-22:00)
  - 밤 (22:00-24:00)
  - 심야 (00:00-05:00)

### Q37. 하루 중 가장 창의적인 시간대
- **Field Name**: `creative_hours`
- **Type**: Checkbox
- **Required**: Yes
- **Options**: (Q36과 동일)

### Q38. 평균 업무/공부 시간 (하루)
- **Field Name**: `daily_work_hours`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 2시간 미만
  - 2-4시간
  - 4-6시간
  - 6-8시간
  - 8-10시간
  - 10시간 이상

### Q39. 평균 운동 시간 (주간)
- **Field Name**: `weekly_exercise_hours`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 운동 안함
  - 1-2시간
  - 2-4시간
  - 4-7시간
  - 7시간 이상

### Q40. 평균 사회 활동 시간 (주간)
- **Field Name**: `weekly_social_hours`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 거의 없음
  - 1-3시간
  - 3-6시간
  - 6-10시간
  - 10시간 이상

---

## 섹션 J: 건강 및 웰빙

### Q41. 현재 건강 상태
- **Field Name**: `health_status`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 매우 좋음
  - 좋음
  - 보통
  - 나쁨 (관리 필요)
  - 매우 나쁨 (치료 중)

### Q42. 만성 질환 또는 주의사항 (선택)
- **Field Name**: `health_conditions`
- **Type**: Checkbox
- **Required**: No
- **Options**:
  - 없음
  - 알레르기
  - 소화기 문제
  - 수면 장애
  - 허리/목 통증
  - 정신 건강 (우울/불안)
  - 기타 (자유 입력)

### Q43. 식습관 패턴
- **Field Name**: `eating_pattern`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 규칙적 (3끼 정시)
  - 불규칙적
  - 소식 (자주 조금씩)
  - 과식 경향
  - 다이어트 중
  - 채식/비건

### Q44. 카페인 섭취 (하루)
- **Field Name**: `caffeine_intake`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 안 마심
  - 1잔
  - 2-3잔
  - 4잔 이상
  - 에너지 드링크 포함

---

# PART 5: 관심사 및 목표

## 섹션 K: 주요 관심사

### Q45. 다이어리에서 다루고 싶은 주제 (다중 선택, 최대 5개)
- **Field Name**: `topics`
- **Type**: Checkbox
- **Required**: Yes
- **Options**:
  - 건강 (운동, 식단, 수면)
  - 관계 (연애, 가족, 친구)
  - 학습 (공부, 독서, 자격증)
  - 일/업무 (경력, 성과, 승진)
  - 창작 (글쓰기, 예술, 콘텐츠)
  - 재정 (저축, 투자, 부업)
  - 감정 (심리, 치유, 성장)
  - 자기계발 (습관, 생산성, 목표)
  - 취미 (여행, 게임, 영화)
  - 영성 (명상, 종교, 철학)

### Q46. 각 주제의 우선순위 (1-5점)
- **Field Name**: `topic_priorities`
- **Type**: JSON Object (각 주제별 점수)
- **Example**: `{"건강": 5, "관계": 4, "학습": 3}`

### Q47. 올해의 주요 목표 (3가지)
- **Field Name**: `yearly_goals`
- **Type**: Text (최대 3개, 줄바꿈 구분)
- **Required**: Yes
- **Example**:
  ```
  1. 토익 900점 달성
  2. 매일 30분 운동
  3. 월 50만원 저축
  ```

### Q48. 이번 달의 목표
- **Field Name**: `monthly_goal`
- **Type**: Text
- **Required**: No
- **Example**: 프로젝트 마감 성공적으로 마치기

---

## 섹션 L: 활동 세분화 (역할별)

### 🎓 학생인 경우

#### Q49-1. 주로 하는 학습 활동 (다중 선택)
- **Field Name**: `study_type`
- **Type**: Checkbox
- **Options**:
  - 시험 준비 (중간/기말)
  - 자격증/공인시험 (토익, 한자 등)
  - 프로젝트/과제
  - 독서/자율학습
  - 어학 (영어, 제2외국어)
  - 코딩/프로그래밍
  - 예체능 실기

#### Q49-2. 선호하는 학습 시간대
- **Field Name**: `study_preferred_time`
- **Type**: Checkbox
- **Options**:
  - 새벽 (05-07시)
  - 오전 (07-12시)
  - 오후 (12-18시)
  - 저녁 (18-22시)
  - 밤 (22-02시)

#### Q49-3. 학습 장소 선호
- **Field Name**: `study_location`
- **Type**: Checkbox
- **Options**:
  - 집
  - 도서관
  - 카페
  - 독서실/스터디카페
  - 학교
  - 야외

#### Q49-4. 주로 하는 운동 (다중 선택)
- **Field Name**: `student_exercise_type`
- **Type**: Checkbox
- **Options**:
  - 러닝/조깅
  - 헬스/근력운동
  - 요가/필라테스
  - 수영
  - 구기종목 (축구, 농구 등)
  - 자전거
  - 등산
  - 홈트레이닝
  - 댄스/에어로빅

#### Q49-5. 운동 선호 시간대
- **Field Name**: `student_exercise_time`
- **Type**: Radio
- **Options**:
  - 새벽 (06-08시)
  - 오전 (08-12시)
  - 오후 (12-18시)
  - 저녁 (18-22시)
  - 밤 (22시 이후)

#### Q49-6. 사회 활동 (다중 선택)
- **Field Name**: `student_social_type`
- **Type**: Checkbox
- **Options**:
  - 스터디그룹
  - 동아리 활동
  - 멘토링 (멘토/멘티)
  - 친구 모임
  - 봉사 활동
  - 아르바이트
  - 대외 활동

---

### 💼 직장인인 경우

#### Q50-1. 주로 하는 업무 유형 (다중 선택)
- **Field Name**: `work_type`
- **Type**: Checkbox
- **Options**:
  - 보고서/문서 작성
  - 기획/전략 수립
  - 회의/협업
  - 데이터 분석
  - 고객 응대
  - 프레젠테이션
  - 프로젝트 관리
  - 연구개발
  - 영업/마케팅
  - 디자인/창작

#### Q50-2. 업무 집중 시간대
- **Field Name**: `work_peak_hours`
- **Type**: Checkbox
- **Options**:
  - 오전 (09-12시)
  - 점심 후 (13-15시)
  - 오후 (15-18시)
  - 야근 시간 (18시 이후)

#### Q50-3. 회의 빈도 (주간)
- **Field Name**: `meeting_frequency`
- **Type**: Radio
- **Options**:
  - 거의 없음
  - 1-2회
  - 3-5회
  - 6-10회
  - 매일 2회 이상

#### Q50-4. 주로 하는 운동 (다중 선택)
- **Field Name**: `office_exercise_type`
- **Type**: Checkbox
- **Options**:
  - 러닝/조깅
  - 헬스/PT
  - 요가/필라테스
  - 수영
  - 골프
  - 등산
  - 자전거
  - 홈트레이닝
  - 테니스/라켓 스포츠
  - 구기종목

#### Q50-5. 운동 선호 시간대
- **Field Name**: `office_exercise_time`
- **Type**: Radio
- **Options**:
  - 출근 전 (06-08시)
  - 점심 시간 (12-14시)
  - 퇴근 후 (18-20시)
  - 저녁 (20-22시)
  - 주말

#### Q50-6. 사회 활동 (다중 선택)
- **Field Name**: `office_social_type`
- **Type**: Checkbox
- **Options**:
  - 팀 회식/저녁
  - 팀빌딩/워크샵
  - 네트워킹 행사
  - 세미나/컨퍼런스
  - 사내 동호회
  - 멘토링
  - 스터디/독서모임

#### Q50-7. 퇴근 후 주요 활동
- **Field Name**: `after_work_routine`
- **Type**: Checkbox
- **Options**:
  - 운동
  - 자기계발 (공부, 독서)
  - 취미 활동
  - 가족/친구 만남
  - 휴식/수면
  - 부업/사이드 프로젝트
  - 넷플릭스/게임

---

### 🎨 자영업자/프리랜서인 경우

#### Q51-1. 주요 업무 분야
- **Field Name**: `freelance_field`
- **Type**: Text
- **Required**: Yes
- **Example**: 그래픽 디자인, 글쓰기, 개발, 컨설팅

#### Q51-2. 주로 하는 일의 유형 (다중 선택)
- **Field Name**: `freelance_work_type`
- **Type**: Checkbox
- **Options**:
  - 창작/디자인
  - 글쓰기/번역
  - 개발/코딩
  - 컨설팅/자문
  - 클라이언트 미팅
  - 기획/제안서 작성
  - 마감 작업
  - 자기계발/스킬업
  - 마케팅/홍보

#### Q51-3. 평균 프로젝트 기간
- **Field Name**: `project_duration`
- **Type**: Radio
- **Options**:
  - 1일 (단기)
  - 1주일
  - 1개월
  - 3개월
  - 6개월 이상

#### Q51-4. 주요 작업 시간대
- **Field Name**: `freelance_work_hours`
- **Type**: Checkbox
- **Options**:
  - 오전 (08-12시)
  - 오후 (12-18시)
  - 저녁 (18-22시)
  - 밤 (22-02시)
  - 불규칙 (프로젝트에 따라)

#### Q51-5. 주로 하는 운동
- **Field Name**: `freelance_exercise_type`
- **Type**: Checkbox
- **Options**: (직장인과 동일)

#### Q51-6. 사회 활동
- **Field Name**: `freelance_social_type`
- **Type**: Checkbox
- **Options**:
  - 콜라보레이션
  - 커뮤니티 모임
  - 워크샵/세미나
  - 네트워킹
  - 클라이언트 미팅
  - 온라인 커뮤니티

---

### 👶 주부/육아인 경우

#### Q52-1. 육아 중인 자녀 수
- **Field Name**: `children_count`
- **Type**: Number
- **Required**: Yes
- **Example**: 2

#### Q52-2. 자녀 연령대 (다중 선택)
- **Field Name**: `children_ages`
- **Type**: Checkbox
- **Options**:
  - 영아 (0-2세)
  - 유아 (3-5세)
  - 초등 저학년 (6-8세)
  - 초등 고학년 (9-12세)
  - 중학생 (13-15세)
  - 고등학생 (16-18세)
  - 성인 (19세 이상)

#### Q52-3. 주로 하는 활동 (다중 선택)
- **Field Name**: `parent_activity_type`
- **Type**: Checkbox
- **Options**:
  - 육아 (수유, 놀이, 교육)
  - 가사 (요리, 청소, 정리)
  - 자기계발 (공부, 자격증)
  - 재택 부업
  - 운동/건강 관리
  - 취미 활동
  - 봉사 활동

#### Q52-4. 육아 패턴
- **Field Name**: `parenting_pattern`
- **Type**: Radio
- **Options**:
  - 전일 육아 (도움 없음)
  - 파트타임 도움 (조부모/육아도우미)
  - 공동 육아 (배우자와 분담)
  - 어린이집/유치원 이용

#### Q52-5. 개인 시간 확보 시간대
- **Field Name**: `parent_free_time`
- **Type**: Checkbox
- **Options**:
  - 새벽 (05-07시, 자녀 기상 전)
  - 오전 (등원 후)
  - 낮잠 시간
  - 오후 (어린이집 시간)
  - 저녁 (취침 후)
  - 주말 (배우자 돌봄)

#### Q52-6. 주로 하는 운동
- **Field Name**: `parent_exercise_type`
- **Type**: Checkbox
- **Options**:
  - 걷기/산책 (유모차)
  - 홈트레이닝 (유튜브)
  - 요가/필라테스
  - 수영
  - 자전거
  - 헬스장 (아이 맡기고)
  - 운동 못함

#### Q52-7. 사회 활동
- **Field Name**: `parent_social_type`
- **Type**: Checkbox
- **Options**:
  - 부모 모임
  - 가족 나들이
  - 친구 만남
  - 온라인 커뮤니티
  - 봉사 활동
  - 종교 활동

---

# PART 6: 콘텐츠 맞춤 설정

## 섹션 M: 다이어리 스타일

### Q53. 선호하는 조언 톤
- **Field Name**: `tone_preference`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 친근한 조언자 (편안하고 공감적)
  - 전문 컨설턴트 (논리적이고 분석적)
  - 멘토/코치 (동기부여와 격려)
  - 철학자 (성찰과 깊이)

### Q54. 조언 문체 선호
- **Field Name**: `writing_style`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 반말 (친근함)
  - 존댓말 (격식)
  - 혼합 (상황에 따라)

### Q55. 다이어리 분량 선호
- **Field Name**: `content_length_preference`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 간결하게 (400-600자, 핵심만)
  - 보통 (600-900자)
  - 상세하게 (900-1200자, 설명 충분히)

### Q56. 콘텐츠에 포함하고 싶은 요소 (다중 선택)
- **Field Name**: `content_elements`
- **Type**: Checkbox
- **Required**: Yes
- **Options**:
  - 오늘의 리듬 해설
  - 집중/주의 포인트
  - 행동 가이드 (Do/Avoid)
  - 좋은 시간대/방향
  - 감정 상태 예측
  - 관계 조언
  - 자기성찰 질문
  - 명언/격려 문구

### Q57. 특별히 피하고 싶은 주제 (선택)
- **Field Name**: `avoid_topics`
- **Type**: Checkbox
- **Required**: No
- **Options**:
  - 재정/돈 이야기
  - 연애/관계
  - 건강 경고
  - 종교/영성
  - 정치/사회
  - 없음

---

## 섹션 N: 다이어리 사용 방식

### Q58. 다이어리 주 사용 목적 (다중 선택)
- **Field Name**: `diary_purpose`
- **Type**: Checkbox
- **Required**: Yes
- **Options**:
  - 일정 관리
  - 감정 기록
  - 목표 추적
  - 습관 형성
  - 자기성찰
  - 업무/학습 기록
  - 건강 트래킹

### Q59. 선호하는 사용 방식
- **Field Name**: `diary_preference`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 앱 전용 (웹/모바일 앱)
  - 앱 + 종이 (병행)
  - 종이 전용 (인쇄 다이어리)

### Q60. 기록 주기
- **Field Name**: `diary_frequency`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 매일
  - 주 3-4회
  - 주말만
  - 필요할 때만

### Q61. 선호하는 기록 시간대
- **Field Name**: `diary_writing_time`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 아침 (하루 계획)
  - 오후 (중간 점검)
  - 저녁 (하루 회고)
  - 자기 전 (반성/감사)

### Q62. PDF 다이어리 받고 싶은 주기 (종이 사용자)
- **Field Name**: `pdf_delivery_cycle`
- **Type**: Radio
- **Required**: No
- **Options**:
  - 매일 (오늘의 페이지)
  - 매주 (7일분)
  - 매달 (월간 다이어리)
  - 분기별
  - 연간

---

# PART 7: 개인정보 및 알림 설정

## 섹션 O: 알림 선호

### Q63. 다이어리 알림 받고 싶은 시간
- **Field Name**: `notification_time`
- **Type**: Time
- **Required**: No
- **Example**: 08:00
- **설명**: 매일 이 시간에 오늘의 다이어리 알림

### Q64. 알림 방식 (다중 선택)
- **Field Name**: `notification_method`
- **Type**: Checkbox
- **Required**: No
- **Options**:
  - 이메일
  - 앱 푸시 알림
  - 문자 메시지 (SMS)
  - 알림 받지 않음

### Q65. 주간 리포트 수신
- **Field Name**: `weekly_report`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 예 (매주 월요일 발송)
  - 아니오

### Q66. 월간 리포트 수신
- **Field Name**: `monthly_report`
- **Type**: Radio
- **Required**: Yes
- **Options**:
  - 예 (매월 1일 발송)
  - 아니오

---

## 섹션 P: 개인정보 동의

### Q67. 개인정보 수집 및 이용 동의 (필수)
- **Field Name**: `privacy_consent`
- **Type**: Checkbox
- **Required**: Yes
- **Label**: [필수] 개인정보 수집 및 이용에 동의합니다
- **설명**:
  ```
  수집 항목: 이름, 이메일, 생년월일, 출생시간, 성별, 설문 응답
  이용 목적: 맞춤형 다이어리 콘텐츠 제공
  보유 기간: 회원 탈퇴 시까지
  ```

### Q68. 마케팅 정보 수신 동의 (선택)
- **Field Name**: `marketing_consent`
- **Type**: Checkbox
- **Required**: No
- **Label**: [선택] 이벤트 및 할인 정보 수신에 동의합니다

### Q69. 제3자 정보 제공 동의 (선택)
- **Field Name**: `third_party_consent`
- **Type**: Checkbox
- **Required**: No
- **Label**: [선택] 제휴사 정보 제공에 동의합니다
- **설명**: PDF 인쇄소, 배송업체 등

---

# PART 8: 추가 정보 (선택)

## 섹션 Q: 자유 의견

### Q70. 다이어리에 특별히 포함되길 바라는 내용
- **Field Name**: `special_requests`
- **Type**: Textarea (긴 텍스트)
- **Required**: No
- **Placeholder**: 예: 매일 영어 명언을 넣어주세요, 운동 루틴을 자동 생성해주세요 등

### Q71. 사주/기문에 대한 이해도
- **Field Name**: `divination_knowledge`
- **Type**: Radio
- **Required**: No
- **Options**:
  - 전혀 모름
  - 조금 알고 있음
  - 어느 정도 이해
  - 전문가 수준

### Q72. 참고하고 싶은 다른 시스템 (선택)
- **Field Name**: `reference_systems`
- **Type**: Checkbox
- **Required**: No
- **Options**:
  - MBTI
  - 에니어그램
  - 별자리/타로
  - 사주명리 상세
  - 기문둔갑 상세
  - 숫자 운세
  - 없음 (현재 시스템만)

---

# 설문 완료 후 자동 처리

## 1단계: 데이터 수집
- 총 72개 질문 응답 수집
- n8n webhook으로 전송

## 2단계: 프로필 생성
```javascript
{
  "basic_info": {
    "name": "김철수",
    "birth_date": "1995-05-15",
    "birth_time": "14:30",
    "gender": "남성",
    "calendar_type": "양력"
  },
  "personality": {
    // 14개 성격 특성 (0-100 변환)
    "extroversion": 75,
    "structured": 50,
    // ...
  },
  "lifestyle": {
    "sleep_pattern": {...},
    "energy_pattern": "아침형",
    "productive_hours": ["07-12", "14-18"],
    // ...
  },
  "preferences": {
    "topics": ["건강", "관계", "학습"],
    "tone": "친근한 조언자",
    "content_length": 900,
    // ...
  },
  "goals": {
    "yearly": ["토익 900점", "매일 30분 운동", "월 50만원 저축"],
    "monthly": "프로젝트 마감"
  }
}
```

## 3단계: 사주 계산
```
생년월일: 1995-05-15 14:30 (양력)
→ 사주 팔자 계산
→ 대운 계산 (성별 고려)
→ 오늘의 운세 (2026-01-30 기준)
```

## 4단계: 개인화 콘텐츠 생성
```
사주 계산 결과 + 성격 특성 + 생활 패턴 + 선호도
→ 완전히 개인화된 조언
→ 선호 시간대에 맞춘 일정 제안
→ 목표 기반 행동 가이드
→ 900자 분량 (선호도 반영)
```

## 5단계: 첫 PDF 다이어리 생성
```
GET /api/pdf/customer/{user_id}/daily/2026-01-30
→ 김철수만의 유일무이한 다이어리
```

---

# 📤 n8n Webhook 전송 예시

```json
{
  "survey_id": "survey_detailed_v1",
  "submission_id": "n8n_{{$now}}",
  "response_data": {
    // PART 1: 기본 정보
    "name": "김철수",
    "email": "chulsoo@example.com",
    "phone": "010-1234-5678",
    "birth_date": "1995-05-15",
    "birth_time": "14:30",
    "birth_location": "서울",
    "gender": "남성",
    "calendar_type": "양력",

    // PART 2: 역할
    "primary_role": "student",
    "secondary_roles": ["학생 + 아르바이트"],
    "occupation_detail": "컴퓨터공학과",
    "organization_size": "중견",
    "work_style": "전일 대면",

    // PART 3: 성격 (14개)
    "p_extroversion": 4,
    "p_structured": 3,
    "p_openness": 5,
    "p_empathy": 4,
    "p_calm": 3,
    "p_focus": 4,
    "p_creative": 5,
    "p_logical": 3,
    "p_perfectionism": 4,
    "p_risk_taking": 3,
    "p_assertiveness": 3,
    "p_flexibility": 4,
    "p_optimism": 4,
    "p_independence": 4,

    // PART 4: 생활 패턴
    "energy_pattern": "아침형",
    "energy_recharge": "혼자 있을 때 충전",
    "stress_coping": ["운동", "혼자만의 시간"],
    "weekday_bedtime": "23:30",
    "weekday_waketime": "07:00",
    "weekend_bedtime": "01:00",
    "weekend_waketime": "09:00",
    "sleep_quality": "좋음",
    "productive_hours": ["오전", "오후"],
    "creative_hours": ["저녁"],
    "daily_work_hours": "6-8시간",
    "weekly_exercise_hours": "2-4시간",
    "weekly_social_hours": "3-6시간",
    "health_status": "좋음",
    "health_conditions": ["없음"],
    "eating_pattern": "규칙적",
    "caffeine_intake": "2-3잔",

    // PART 5: 관심사
    "topics": ["건강", "관계", "학습"],
    "topic_priorities": {
      "건강": 5,
      "관계": 4,
      "학습": 5
    },
    "yearly_goals": [
      "토익 900점 달성",
      "매일 30분 운동",
      "월 50만원 저축"
    ],
    "monthly_goal": "알고리즘 공부 매일 1문제",

    // PART 5L: 학생 활동
    "study_type": ["시험 준비", "프로젝트", "코딩"],
    "study_preferred_time": ["오전", "저녁"],
    "study_location": ["도서관", "카페"],
    "student_exercise_type": ["러닝", "헬스"],
    "student_exercise_time": "저녁",
    "student_social_type": ["스터디그룹", "동아리"],

    // PART 6: 콘텐츠 설정
    "tone_preference": "친근한 조언자",
    "writing_style": "반말",
    "content_length_preference": "상세하게",
    "content_elements": [
      "오늘의 리듬 해설",
      "집중/주의 포인트",
      "행동 가이드",
      "좋은 시간대/방향",
      "자기성찰 질문"
    ],
    "avoid_topics": [],

    // PART 6N: 사용 방식
    "diary_purpose": ["일정 관리", "목표 추적", "자기성찰"],
    "diary_preference": "앱 + 종이",
    "diary_frequency": "매일",
    "diary_writing_time": "저녁",
    "pdf_delivery_cycle": "매달",

    // PART 7: 알림
    "notification_time": "08:00",
    "notification_method": ["이메일", "앱 푸시"],
    "weekly_report": "예",
    "monthly_report": "예",

    // PART 7P: 동의
    "privacy_consent": true,
    "marketing_consent": true,
    "third_party_consent": false,

    // PART 8: 추가
    "special_requests": "매일 아침 영어 명언 한 줄 추가해주세요",
    "divination_knowledge": "조금 알고 있음",
    "reference_systems": ["MBTI", "사주명리 상세"]
  },
  "metadata": {
    "n8n_workflow_id": "{{$workflow.id}}",
    "n8n_execution_id": "{{$execution.id}}",
    "submitted_at": "{{$now}}",
    "survey_version": "detailed_v1.0"
  }
}
```

---

# 🎯 이 설문의 강점

## 1. 완전 개인화 (Hyper-Personalization)
- 72개 질문으로 고객의 모든 측면 파악
- 사주 계산 + 성격 + 생활 패턴 + 선호도 통합

## 2. 시간대 최적화
- 수면 패턴, 생산적 시간, 창의적 시간 모두 수집
- 개인의 생체 리듬에 맞춘 일정 제안

## 3. 목표 기반 조언
- 올해/이달 목표를 알고 있음
- 목표 달성을 위한 맞춤 행동 가이드

## 4. 스타일 커스터마이징
- 톤, 문체, 분량까지 선택 가능
- 피하고 싶은 주제 설정 가능

## 5. 활동 세분화
- 역할별 3단계 상세 질문
- "러닝"만 해도 시간대, 빈도까지 파악

---

# 📞 다음 단계

1. **n8n 폼 빌더에서 이 템플릿으로 설문 생성**
2. **조건부 로직 설정** (역할에 따라 다른 질문)
3. **Webhook 노드 연결**
4. **테스트 제출**
5. **완전 개인화된 다이어리 확인!**

---

**이제 진짜 "나만을 위한" 다이어리가 탄생합니다!** 🎊
