# Web Companion 배포 가이드 (Vercel)

전제: Vercel CLI 설치됨 (`vercel --version`으로 확인).

## 1회 셋업

```powershell
vercel login        # 로그인 (이메일 매직 링크)
cd D:\project\diary-PJ\web-deploy
vercel link         # 프로젝트 연결 (project name: saju-diary)
```

## 신규 고객 배포

```powershell
# 1. 콘텐츠 생성
cd D:\project\diary-PJ\diary
.venv\Scripts\Activate.ps1
$env:DEEPINFRA_API_KEY = "실제 키"

diary --year 1971 --month 11 --day 17 --hour 4 --gender male `
      --customer-name "박준수" --start 2026-05-15 --days 7 `
      -o output\park_junsoo.pdf `
      --web-output ..\web-deploy\public\d

# 2. customer_id 확인
$cust = (Get-ChildItem ..\web-deploy\public\d -Directory | Select -First 1).Name
Write-Host "customer_id: $cust"

# 3. 배포
cd ..\web-deploy
vercel deploy --prod
# → https://saju-diary.vercel.app/d/<cust>/
```

## URL 구조

- `/` → 랜딩 (공개)
- `/privacy` / `/recovery` → 공개 정보
- `/d/<token_20>/` → 고객 다이어리 (noindex, 검색 차단)

## 보안

- `X-Robots-Tag: noindex, nofollow` 헤더 (Vercel 적용)
- HTTPS 자동 (Vercel 기본)
- 외부 트래커 없음 (Pretendard CDN만)
