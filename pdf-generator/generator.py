"""
PDF Generator for R³ Diary System
Uses WeasyPrint and Jinja2 to convert HTML templates to PDF
"""
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class PDFGenerator:
    """PDF generation engine for diary pages"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.template_dir = self.base_dir / "templates"
        self.styles_path = self.base_dir / "styles.css"

        # Jinja2 환경 설정
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )

        # 역할 한글 매핑
        self.role_display_map = {
            "student": "학생",
            "office_worker": "직장인",
            "freelancer": "프리랜서"
        }

    def generate_daily_pdf(
        self,
        content: Dict[str, Any],
        output_path: str,
        role: Optional[str] = None
    ) -> str:
        """
        Generate daily page PDF from DailyContent

        Args:
            content: DailyContent 딕셔너리 (DAILY_CONTENT_SCHEMA 준수)
            output_path: PDF 저장 경로
            role: 역할 (student, office_worker, freelancer)

        Returns:
            생성된 PDF 파일 경로

        Example:
            generator = PDFGenerator()
            pdf_path = generator.generate_daily_pdf(
                content=daily_content_dict,
                output_path="output/2026-01-20.pdf",
                role="student"
            )
        """
        # 템플릿 로드
        template = self.jinja_env.get_template("daily.html")

        # 템플릿 변수 준비
        template_vars = {
            "content": content,
            "role": role,
            "role_display": self.role_display_map.get(role, ""),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # HTML 렌더링
        html_content = template.render(**template_vars)

        # PDF 생성
        HTML(string=html_content, base_url=str(self.base_dir)).write_pdf(
            output_path,
            stylesheets=[CSS(filename=str(self.styles_path))]
        )

        return output_path

    def generate_monthly_pdf(
        self,
        content: Dict[str, Any],
        output_path: str,
        role: Optional[str] = None
    ) -> str:
        """
        Generate monthly page PDF

        Args:
            content: MonthlyContent 딕셔너리
            output_path: PDF 저장 경로
            role: 역할 (student, office_worker, freelancer)

        Returns:
            생성된 PDF 파일 경로

        Example:
            generator = PDFGenerator()
            pdf_path = generator.generate_monthly_pdf(
                content=monthly_content_dict,
                output_path="output/2026-01.pdf",
                role="student"
            )
        """
        # 템플릿 로드
        template = self.jinja_env.get_template("monthly.html")

        # 템플릿 변수 준비
        template_vars = {
            "content": content,
            "role": role,
            "role_display": self.role_display_map.get(role, ""),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # HTML 렌더링
        html_content = template.render(**template_vars)

        # PDF 생성
        HTML(string=html_content, base_url=str(self.base_dir)).write_pdf(
            output_path,
            stylesheets=[CSS(filename=str(self.styles_path))]
        )

        return output_path

    def generate_from_content_model(
        self,
        content_type: str,
        content_obj: Any,
        output_path: str,
        role: Optional[str] = None
    ) -> str:
        """
        Generate PDF from Pydantic content model

        Args:
            content_type: "daily" or "monthly"
            content_obj: DailyContent or MonthlyContent Pydantic model
            output_path: PDF 저장 경로
            role: 역할

        Returns:
            생성된 PDF 파일 경로
        """
        # Pydantic 모델을 딕셔너리로 변환
        content_dict = content_obj.model_dump()

        if content_type == "daily":
            return self.generate_daily_pdf(content_dict, output_path, role)
        elif content_type == "monthly":
            return self.generate_monthly_pdf(content_dict, output_path, role)
        else:
            raise ValueError(f"Unknown content_type: {content_type}")


def main():
    """Example usage"""
    generator = PDFGenerator()

    # 샘플 일간 콘텐츠 (DAILY_CONTENT_SCHEMA 준수)
    sample_daily_content = {
        "date": "2026-01-20",
        "summary": "오늘은 집중과 정리가 필요한 날입니다. 새로운 시작보다는 기존 작업을 완료하는 것이 좋습니다.",
        "keywords": ["집중", "정리", "완료", "안정"],
        "rhythm_description": """
오늘의 리듬은 안정적이고 차분한 흐름을 보입니다.
새로운 도전이나 변화를 시도하기보다는 이미 진행 중인 일들을 정리하고 마무리하는 데
에너지를 집중하면 좋습니다. 특히 오전 시간대에 중요한 결정이나 회의를 진행하면
좋은 결과를 얻을 수 있습니다.
        """.strip(),
        "focus_caution": {
            "focus": [
                "현재 진행 중인 프로젝트 완료",
                "중요한 서류나 자료 정리",
                "기존 관계 유지 및 강화"
            ],
            "caution": [
                "갑작스러운 결정이나 변화",
                "새로운 프로젝트 시작",
                "불필요한 논쟁이나 충돌"
            ]
        },
        "action_guide": {
            "do": [
                "오전에 집중력이 필요한 일 처리",
                "미뤄둔 일 정리하기",
                "주변 사람들과 소통 강화"
            ],
            "avoid": [
                "충동적인 구매나 결정",
                "과도한 일정 잡기",
                "스트레스 받는 상황 피하기"
            ]
        },
        "time_direction": {
            "good_time": "오전 9시 ~ 오전 11시",
            "avoid_time": "오후 3시 ~ 오후 5시",
            "good_direction": "북쪽, 동쪽",
            "avoid_direction": "남서쪽",
            "notes": "오전 시간대의 에너지가 강하므로 중요한 일은 오전에 집중하세요."
        },
        "state_trigger": {
            "gesture": "양손을 가슴 앞에서 모으고 심호흡하기",
            "phrase": "나는 오늘 하루를 차분하게 정리할 수 있다",
            "how_to": "불안하거나 산만할 때 조용한 공간에서 3회 반복"
        },
        "meaning_shift": """
오늘 느끼는 불안함은 '부족함'이 아니라 '준비 과정'입니다.
완벽하게 준비되지 않은 것처럼 느껴지는 순간이야말로 성장의 신호입니다.
미루고 싶은 마음이 들 때, 그것이 바로 지금 시작해야 할 신호임을 기억하세요.
        """.strip(),
        "rhythm_question": "오늘 가장 완료하고 싶은 한 가지 일은 무엇인가요? 그것을 완료한 나는 어떤 기분일까요?"
    }

    # 일간 PDF 생성
    output_path = "test_daily_full.pdf"
    result = generator.generate_daily_pdf(
        content=sample_daily_content,
        output_path=output_path,
        role="student"
    )
    print(f"✅ Daily PDF generated: {result}")


if __name__ == "__main__":
    main()
