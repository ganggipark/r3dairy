# PDF 생성 시스템 Linux 환경 검증 필요

## 현재 상태

**Windows 환경**: WeasyPrint 의존성 문제로 PDF 생성 불가
- `libgobject-2.0-0` 라이브러리 누락
- GTK+ 및 Pango 설치 필요

## 필요 조치

### Linux/Unix 환경에서 검증 필요

1. **Render/Railway 배포 환경**:
   ```bash
   # Aptfile에 이미 포함됨
   libpango-1.0-0
   libpangoft2-1.0-0
   libharfbuzz0b
   libfontconfig1
   ```

2. **로컬 WSL2 Ubuntu 환경**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
     libpango-1.0-0 \
     libpangoft2-1.0-0 \
     libharfbuzz0b \
     libfontconfig1 \
     libgdk-pixbuf2.0-0
   ```

3. **테스트 실행**:
   ```bash
   cd backend
   pytest tests/test_pdf_generation.py -v
   ```

## 검증 체크리스트

- [ ] WeasyPrint 의존성 설치 확인
- [ ] PDF 생성 테스트 통과
- [ ] 한글 폰트 렌더링 확인
- [ ] Markdown → PDF 변환 검증
- [ ] 인쇄 레이아웃 확인

## 대안 (현재)

Windows 개발 환경에서는:
1. ✅ Markdown 생성만 테스트 (정상 작동)
2. ✅ JSON 콘텐츠 생성 검증 (정상 작동)
3. ⏭️ PDF 생성은 Linux 배포 환경에서만 실행

## 배포 시 확인사항

### Render/Railway 환경 변수
```env
PYTHON_VERSION=3.10
```

### runtime.txt
```
python-3.10
```

### Aptfile
```
libpango-1.0-0
libpangoft2-1.0-0
libharfbuzz0b
libfontconfig1
```

## 참고 문서

- `pdf-generator/WEASYPRINT_SETUP.md` - 상세 설치 가이드
- `backend/Aptfile` - Linux 의존성 목록
- `pdf-generator/README_MARKDOWN_SUPPORT.md` - Markdown PDF 변환 가이드

## 다음 단계

1. **즉시**: Linux 환경 (WSL2 또는 Render 배포)에서 PDF 생성 테스트
2. **배포 전**: 프로덕션 환경에서 PDF API 엔드포인트 검증
3. **선택**: Windows 개발 시 Docker 사용 고려

---

**작성일**: 2026-01-31
**상태**: ⚠️ Windows 환경 제한, Linux 검증 대기 중
