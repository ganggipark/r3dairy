# 포트 3000 서버 실행 완료

## ✅ 서버 상태

### Frontend (Next.js)
- **URL**: http://localhost:3000
- **포트**: 3000
- **상태**: 🟢 시작 중 (브라우저에서 확인)

### Backend (FastAPI)
- **API URL**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **포트**: 8000
- **상태**: ✅ 정상 작동

## 📝 변경 사항

### 1. Frontend 포트 변경
**파일**: `frontend/package.json`
```json
"dev": "next dev -p 3000"
```
5000 → 3000으로 변경

### 2. Backend CORS 설정 변경
**파일**: `backend/src/main.py`
```python
allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]
```
5000 → 3000으로 변경

## 🌐 브라우저 접속

브라우저가 자동으로 열렸습니다:
1. Frontend: http://localhost:3000
2. Backend API Docs: http://localhost:8000/docs

## 📱 테스트 페이지

- **홈**: http://localhost:3000
- **로그인**: http://localhost:3000/login
- **프로필**: http://localhost:3000/profile
- **오늘**: http://localhost:3000/today

## ⚙️ 서버 재시작 방법

### Frontend
```bash
cd frontend
npm run dev
```
자동으로 포트 3000에서 시작됩니다.

### Backend
```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

## 🔧 수동 시작 (필요시)

새 터미널 창에서:

**Terminal 1 - Backend:**
```bash
cd E:\project\diary-PJ\backend
python -m uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd E:\project\diary-PJ\frontend
npm run dev
```

## ✅ 확인사항

- [x] 포트 3000으로 변경 완료
- [x] CORS 설정 업데이트
- [x] Backend 정상 작동 (8000)
- [ ] Frontend 시작 완료 확인 (브라우저에서)

---

**작성일**: 2026-01-31
**포트**: Frontend 3000, Backend 8000
**상태**: 설정 완료, Frontend 시작 중

브라우저에서 http://localhost:3000 이 열리면 정상입니다!
