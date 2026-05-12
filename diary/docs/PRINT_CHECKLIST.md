# Print Checklist

인쇄소 출고 전 PDF 검증 절차. 대량 생산 전 1부 인쇄 테스트 필수.

## 1. PDF 기본 검증 (1분)

- [ ] PDF가 정상 열림 (Adobe Reader / SumatraPDF / 브라우저)
- [ ] 첫 페이지 = 표지 (`--no-cover` 안 썼다면)
- [ ] 페이지 수 = 예상값:
  - 표지 2p + (월구분 N × 2p) + (일별 D × 2p)
  - 7일 × 1개월: 2 + 2 + 14 = **18p**
  - 30일 × 1개월: 2 + 2 + 60 = **64p**
  - 365일 × 12개월: 2 + 24 + 730 = **756p**
- [ ] 파일 크기 sanity:
  - 7일: 90~250 KB
  - 30일: 300~700 KB
  - 365일: 8~20 MB
  - 10KB 미만 시 콘텐츠 누락 의심

## 2. 폰트 임베드 검증

Adobe Reader: `파일 → 속성 → 글꼴` 탭

- [ ] Pretendard (또는 Pretendard-Regular)
- [ ] Pretendard-SemiBold (또는 Pretendard with weight 600)
- [ ] Pretendard-Bold
- [ ] 모두 **임베드된 하위 집합** (Embedded Subset)
- [ ] Malgun Gothic — 가능하면 없어야 하지만 일부 fallback 발생은 정상

또는 CLI:
```powershell
.venv\Scripts\python -c "from pypdf import PdfReader; r=PdfReader('output\\diary.pdf'); print([p['/Resources']['/Font'] for p in r.pages[:3]])"
```

## 3. 콘텐츠 자연성 (랜덤 샘플 3페이지)

PDF에서 임의 일별 페이지 3개 펴서 확인:

- [ ] 사주 내부 용어 노출 ❌ ("庚午", "正官", "신살", "三合", "용신")
- [ ] 점쟁이 톤 아닌 일상 안내 언어
- [ ] daily_summary 100~250자 내외
- [ ] lucky_color / lucky_direction / lucky_time이 본문과 어울림
- [ ] mindfulness 80~300자, 명상·수용 안내 톤
- [ ] right_page_hint 8~60자, 격려 톤
- [ ] recommended_actions 2~5개
- [ ] things_to_avoid 1~3개

## 4. 레이아웃 검증

**표지 (2페이지)**:
- [ ] 앞면: 제목 / 부제 / 기간 / 고객명 위치 정렬
- [ ] 뒷면: 사용법 안내문

**월 구분 (월 시작 시 2페이지)**:
- [ ] 좌: 큰 월 번호 + 연도
- [ ] 우: "이번 달의 다짐" 제목 + 18줄

**일별 (2페이지)**:
- [ ] 좌: 날짜 헤더 / 요약 / lucky-box (색 swatch 보임) / 집중 / 주의 / 추천 / 피할 / 마음챙김 (이탤릭)
- [ ] 우: 작은 날짜 / 격려문 / 28줄 / 하단 코너 색·방향·시간

## 5. 인쇄소 사양

| 항목 | 값 |
|---|---|
| 페이지 크기 | A5 (148 × 210mm) portrait |
| 여백 (T/R/B/L) | 14 / 13 / 16 / 13 mm |
| 색상 | 회색조 + lucky swatch만 컬러 |
| 페이지 번호 | 하단 중앙 (표지/월구분 제외) |
| 제본 | 좌측 책등 (left-binding) |
| 페이지 매칭 | 일별 좌측 = 짝수페이지, 우측 = 홀수페이지 |

## 6. 샘플 인쇄 테스트 (대량 출고 전 필수)

1부 시범 인쇄 후:

- [ ] 좌우 펼침이 자연스러움 (좌 가이드 / 우 작성)
- [ ] 한글 글자 깨짐 ❌
- [ ] 색상 swatch 식별 가능 (인쇄 색감 ≠ 화면)
- [ ] 페이지 번호가 잘리지 않음
- [ ] 글쓰기 줄 굵기 적절 (너무 진하지 않아 필기 방해 ❌)
- [ ] 마음챙김 이탤릭이 가독성 OK
- [ ] 표지 두께/재질 확인

## 출고 결정

위 모든 체크 ✓ → 인쇄소 전송.
하나라도 ✗ → 원인 파악 → 콘텐츠/스타일 조정 → 재생성 → 재검증.

## 자주 발생하는 이슈

| 증상 | 원인 | 해결 |
|---|---|---|
| 한글 일부 깨짐 | Pretendard 미포함 글리프 → Malgun fallback → 인쇄소에 Malgun 없음 | Noto Sans KR 추가 임베드 |
| 페이지 매칭 어긋남 | 일별 1페이지짜리 day가 섞임 (불가능하지만 cover/divider count 오류) | render.py + 템플릿 검증 |
| 인쇄 시 색상 다름 | RGB → CMYK 변환 손실 | 인쇄소와 색상 프로파일 협의 |
| 페이지 번호가 인쇄 절단선에 걸림 | 여백 부족 | styles.css 의 `@page margin` 조정 |
