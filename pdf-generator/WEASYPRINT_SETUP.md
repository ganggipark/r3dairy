# WeasyPrint 설치 가이드

WeasyPrint는 HTML을 PDF로 변환하는 Python 라이브러리입니다. R³ 다이어리 시스템에서 PDF 출력을 위해 사용됩니다.

## 요구사항

WeasyPrint는 다음 시스템 라이브러리에 의존합니다:
- **Cairo** - 2D 그래픽 라이브러리
- **Pango** - 텍스트 레이아웃 및 렌더링
- **GdkPixbuf** - 이미지 로딩

## 설치 방법

### Linux (Ubuntu/Debian)

```bash
# 시스템 라이브러리 설치
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# WeasyPrint 설치
pip install weasyprint
```

### macOS

```bash
# Homebrew로 시스템 라이브러리 설치
brew install cairo pango gdk-pixbuf libffi

# WeasyPrint 설치
pip install weasyprint
```

### Windows

Windows에서 WeasyPrint 설치는 복잡합니다. 다음 옵션 중 하나를 선택하세요:

#### 옵션 1: WSL2 사용 (권장)

1. WSL2 설치 (Windows Subsystem for Linux)
2. Ubuntu 설치
3. Linux 설치 방법을 따름

#### 옵션 2: GTK+ 설치

1. [GTK+ for Windows](https://www.gtk.org/docs/installations/windows/) 다운로드 및 설치
2. 환경 변수에 GTK+ bin 디렉토리 추가
3. `pip install weasyprint`

#### 옵션 3: Docker 사용

프로덕션 배포 시 Docker를 사용하는 것이 가장 안정적입니다:

```dockerfile
FROM python:3.10-slim

# 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드
COPY . /app
WORKDIR /app

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 설치 확인

```python
# test_weasyprint.py
from weasyprint import HTML

html_string = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <h1>WeasyPrint 설치 성공!</h1>
    <p>PDF 생성이 정상적으로 작동합니다.</p>
</body>
</html>
"""

HTML(string=html_string).write_pdf('test.pdf')
print("✅ test.pdf 생성 완료!")
```

```bash
python test_weasyprint.py
```

## 프로덕션 배포

### Railway/Render (Linux 기반 호스팅)

Railway나 Render 같은 PaaS에 배포할 때는 `Aptfile`을 추가하여 시스템 라이브러리를 설치할 수 있습니다:

**Aptfile**:
```
libcairo2
libpango-1.0-0
libpangocairo-1.0-0
libgdk-pixbuf2.0-0
libffi-dev
shared-mime-info
```

### Vercel/Netlify

Vercel이나 Netlify는 Node.js 기반이므로 백엔드를 별도 서비스로 분리해야 합니다.

## 문제 해결

### "cannot load library 'libgobject-2.0-0'" 에러

시스템 라이브러리가 설치되지 않았거나 경로를 찾을 수 없습니다:

- **Linux**: `sudo apt-get install libgobject-2.0-0`
- **macOS**: `brew install glib`
- **Windows**: WSL2 사용 권장

### "OSError: cannot load library" 에러

환경 변수 `LD_LIBRARY_PATH`에 라이브러리 경로가 포함되어 있는지 확인:

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
```

### 한글 폰트 문제

한글이 깨지는 경우 시스템에 한글 폰트를 설치:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-nanum fonts-nanum-coding

# macOS (이미 기본 포함)
# Windows (맑은 고딕 기본 포함)
```

## 참고 자료

- [WeasyPrint 공식 문서](https://doc.courtbouillon.org/weasyprint/)
- [Installation Guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation)
- [Troubleshooting](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting)

## R³ 다이어리에서의 사용

PDF API 엔드포인트:
- `GET /api/pdf/daily/{date}` - 일간 PDF 생성
- `GET /api/pdf/monthly/{year}/{month}` - 월간 PDF 생성

실제 PDF 생성은 프로덕션 환경(Linux 서버)에서 테스트하는 것을 권장합니다.
