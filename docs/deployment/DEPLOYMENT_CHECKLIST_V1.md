# 배포 체크리스트 - R³ Diary System

**버전**: v1.0.0
**날짜**: 2026-01-31

## 사전 준비 완료 상태

### 코드 품질
- [x] 모든 테스트 통과 (Content 7/7, Translation 13/13, API 19/19)
- [x] 콘텐츠 생성 시스템 완성 (2213자 달성)
- [x] 역할 번역 시스템 완성 (학생/직장인/프리랜서)
- [x] Git 커밋 정리 완료 (16개 논리적 커밋)
- [x] 문서화 완료

### 환경 설정
- [x] Frontend 빌드 디렉토리 확인
- [x] Backend API 서버 정상 작동
- [x] 포트 5000/8000 통일 완료

## 배포 전 필수 확인사항

### 1. Supabase 설정
- [ ] 프로젝트 생성 완료
- [ ] 데이터베이스 스키마 실행
- [ ] RLS 정책 설정
- [ ] API Keys 발급

### 2. Backend 배포 (Render/Railway)
- [ ] 환경 변수 설정 (SUPABASE_URL, SECRET_KEY 등)
- [ ] Aptfile 포함 확인
- [ ] runtime.txt 설정
- [ ] Build 성공 확인

### 3. Frontend 배포 (Vercel)
- [ ] 환경 변수 설정 (API_URL, SUPABASE_URL)
- [ ] Build 성공 확인
- [ ] 프리뷰 배포 테스트

### 4. PDF 생성 검증
- [ ] Linux 환경에서 WeasyPrint 테스트
- [ ] 한글 폰트 렌더링 확인

참고: PDF_LINUX_VALIDATION.md

---

**작성일**: 2026-01-31
**상태**: 배포 준비 완료 (PDF Linux 검증 제외)
