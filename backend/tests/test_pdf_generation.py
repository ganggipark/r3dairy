"""
PDF 생성 테스트
PDF Generator 품질 및 출력 검증
"""
import pytest
import sys
from pathlib import Path
from datetime import date
import tempfile
import os

# PDF Generator import
sys.path.append(str(Path(__file__).parent.parent.parent / "pdf-generator"))

try:
    from generator import PDFGenerator
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    pytest.skip("WeasyPrint가 설치되지 않았습니다", allow_module_level=True)


@pytest.mark.pdf
@pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint required")
class TestPDFGenerator:
    """PDFGenerator 클래스 테스트"""

    @pytest.fixture
    def generator(self):
        """PDFGenerator 인스턴스"""
        return PDFGenerator()

    @pytest.fixture
    def sample_daily_content_dict(self, sample_daily_content):
        """샘플 일간 콘텐츠 (딕셔너리)"""
        return sample_daily_content.model_dump()

    def test_pdf_generator_initialization(self, generator):
        """PDFGenerator 초기화 테스트"""
        assert generator is not None
        assert generator.template_dir.exists()
        assert generator.styles_path.exists()

    def test_generate_daily_pdf_basic(self, generator, sample_daily_content_dict):
        """기본 일간 PDF 생성 테스트"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            output_path = tmp_file.name

        try:
            result_path = generator.generate_daily_pdf(
                content=sample_daily_content_dict,
                output_path=output_path
            )

            # 파일 생성 확인
            assert os.path.exists(result_path)
            assert os.path.getsize(result_path) > 0  # 파일이 비어있지 않음

        finally:
            # 클린업
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_generate_daily_pdf_with_role(self, generator, sample_daily_content_dict):
        """역할별 일간 PDF 생성 테스트"""
        roles = ["student", "office_worker", "freelancer"]

        for role in roles:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                output_path = tmp_file.name

            try:
                result_path = generator.generate_daily_pdf(
                    content=sample_daily_content_dict,
                    output_path=output_path,
                    role=role
                )

                # 파일 생성 확인
                assert os.path.exists(result_path)
                assert os.path.getsize(result_path) > 0

            finally:
                if os.path.exists(output_path):
                    os.remove(output_path)

    def test_pdf_file_size_reasonable(self, generator, sample_daily_content_dict):
        """PDF 파일 크기가 적절한지 확인"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            output_path = tmp_file.name

        try:
            generator.generate_daily_pdf(
                content=sample_daily_content_dict,
                output_path=output_path
            )

            file_size = os.path.getsize(output_path)

            # 파일 크기 검증 (5KB ~ 5MB)
            assert 5 * 1024 < file_size < 5 * 1024 * 1024, \
                f"PDF 파일 크기가 비정상적입니다: {file_size} bytes"

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


@pytest.mark.pdf
@pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint required")
class TestPDFContent:
    """PDF 콘텐츠 품질 테스트"""

    @pytest.fixture
    def generator(self):
        return PDFGenerator()

    def test_all_10_blocks_present(self, generator, sample_daily_content_dict):
        """10개 블록이 모두 포함되는지 테스트"""
        # HTML 렌더링 테스트
        template = generator.jinja_env.get_template("daily.html")

        html_content = template.render(
            content=sample_daily_content_dict,
            role="student",
            role_display="학생",
            generated_at="2026-01-20 10:00"
        )

        # 10개 블록 키워드 확인
        required_sections = [
            "summary",  # 1. 요약
            "keywords",  # 2. 키워드
            "rhythm_description",  # 3. 리듬 해설
            "focus_caution",  # 4. 집중/주의
            "action_guide",  # 5. Do/Avoid
            "time_direction",  # 6. 시간/방향
            "state_trigger",  # 7. 트리거
            "meaning_shift",  # 8. 의미 전환
            "rhythm_question"  # 9. 질문
        ]

        for section in required_sections:
            assert section in html_content or \
                   sample_daily_content_dict[section] in html_content, \
                   f"블록 '{section}'이 HTML에 포함되지 않았습니다"

    def test_role_display_in_pdf(self, generator, sample_daily_content_dict):
        """역할 표시가 PDF에 포함되는지 테스트"""
        template = generator.jinja_env.get_template("daily.html")

        html_content = template.render(
            content=sample_daily_content_dict,
            role="student",
            role_display="학생",
            generated_at="2026-01-20 10:00"
        )

        assert "학생" in html_content

    def test_date_formatting(self, generator, sample_daily_content_dict):
        """날짜 형식이 올바른지 테스트"""
        template = generator.jinja_env.get_template("daily.html")

        html_content = template.render(
            content=sample_daily_content_dict,
            role=None,
            role_display="",
            generated_at="2026-01-20 10:00"
        )

        # 날짜가 HTML에 포함되어 있는지 확인
        assert "2026-01-20" in html_content or "2026" in html_content


@pytest.mark.pdf
@pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint required")
class TestPDFLayout:
    """PDF 레이아웃 테스트"""

    @pytest.fixture
    def generator(self):
        return PDFGenerator()

    def test_css_file_loaded(self, generator):
        """CSS 파일이 로드되는지 테스트"""
        assert generator.styles_path.exists()

        # CSS 파일 내용 확인
        css_content = generator.styles_path.read_text(encoding="utf-8")

        # 주요 스타일 클래스 존재 확인
        required_classes = [
            ".header",
            ".summary-card",
            ".content-block",
            ".two-column",
            ".focus-section",
            ".caution-section"
        ]

        for css_class in required_classes:
            assert css_class in css_content, \
                f"필수 CSS 클래스 '{css_class}'가 없습니다"

    def test_print_media_settings(self, generator):
        """인쇄 미디어 설정 확인"""
        css_content = generator.styles_path.read_text(encoding="utf-8")

        # @page 규칙 확인
        assert "@page" in css_content

        # A4 페이지 설정 확인
        assert "A4" in css_content or "210mm" in css_content

    def test_page_break_control(self, generator):
        """페이지 브레이크 제어 확인"""
        css_content = generator.styles_path.read_text(encoding="utf-8")

        # page-break-inside: avoid 확인
        assert "page-break-inside" in css_content or "break-inside" in css_content


@pytest.mark.pdf
@pytest.mark.slow
@pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint required")
class TestPDFPerformance:
    """PDF 생성 성능 테스트"""

    @pytest.fixture
    def generator(self):
        return PDFGenerator()

    def test_pdf_generation_speed(self, generator, sample_daily_content_dict):
        """PDF 생성 속도 테스트 (5초 이내)"""
        import time

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            output_path = tmp_file.name

        try:
            start_time = time.time()

            generator.generate_daily_pdf(
                content=sample_daily_content_dict,
                output_path=output_path
            )

            elapsed_time = time.time() - start_time

            # 5초 이내 생성 확인
            assert elapsed_time < 5.0, \
                f"PDF 생성이 너무 느립니다: {elapsed_time:.2f}초"

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


@pytest.mark.pdf
class TestMonthlyPDFPlaceholder:
    """월간 PDF 플레이스홀더 테스트"""

    @pytest.fixture
    def generator(self):
        if not WEASYPRINT_AVAILABLE:
            pytest.skip("WeasyPrint required")
        return PDFGenerator()

    def test_monthly_template_exists(self, generator):
        """월간 템플릿 파일 존재 확인"""
        monthly_template_path = generator.template_dir / "monthly.html"
        assert monthly_template_path.exists()

    def test_monthly_template_has_placeholder(self, generator):
        """월간 템플릿에 플레이스홀더가 있는지 확인"""
        template = generator.jinja_env.get_template("monthly.html")

        html_content = template.render(
            year=2026,
            month=1,
            role="student",
            role_display="학생",
            generated_at="2026-01-20 10:00"
        )

        # 플레이스홀더 메시지 확인
        assert "Phase 3" in html_content or "MonthlyContent" in html_content


# ============================================================================
# 실행 가이드
# ============================================================================
"""
테스트 실행 방법:

1. 전체 PDF 테스트:
   pytest tests/test_pdf_generation.py -v

2. 빠른 테스트만:
   pytest tests/test_pdf_generation.py -v -m "pdf and not slow"

3. 성능 테스트 포함:
   pytest tests/test_pdf_generation.py -v -m slow

4. 커버리지:
   pytest tests/test_pdf_generation.py --cov=pdf-generator --cov-report=html

주의사항:
- WeasyPrint 설치 필요: pip install weasyprint
- 시스템 의존성 필요 (GTK+ on Windows, cairo on macOS/Linux)
"""
