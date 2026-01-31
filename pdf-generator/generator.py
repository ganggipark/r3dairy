"""
PDF Generator for R³ Diary System
Uses WeasyPrint and Jinja2 to convert HTML templates to PDF
"""
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import markdown
import re


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

        # Markdown parser 설정
        self.md = markdown.Markdown(extensions=['extra', 'nl2br'])

    def _parse_markdown_to_dict(self, md_content: str) -> Dict[str, Any]:
        """
        Parse Markdown content to dictionary format matching DAILY_CONTENT_SCHEMA

        Args:
            md_content: Markdown formatted daily content

        Returns:
            Dictionary with parsed content
        """
        lines = md_content.split('\n')
        content = {
            'date': '',
            'summary': '',
            'keywords': [],
            'rhythm_description': '',
            'focus_caution': {'focus': [], 'caution': []},
            'action_guide': {'do': [], 'avoid': []},
            'time_direction': {
                'good_time': '',
                'avoid_time': '',
                'good_direction': '',
                'avoid_direction': ''
            },
            'state_trigger': {'gesture': '', 'phrase': '', 'how_to': ''},
            'meaning_shift': '',
            'rhythm_question': ''
        }

        current_section = None
        current_subsection = None
        buffer = []

        for line in lines:
            line = line.strip()

            # Skip separators
            if line == '---':
                continue

            # H2 headers (main sections)
            if line.startswith('## '):
                # Save previous buffer
                if current_section and buffer:
                    self._save_buffer(content, current_section, current_subsection, buffer)
                    buffer = []

                section_title = line[3:].strip()
                current_section = section_title
                current_subsection = None
                continue

            # H3 headers (subsections)
            if line.startswith('### '):
                # Save previous buffer
                if buffer:
                    self._save_buffer(content, current_section, current_subsection, buffer)
                    buffer = []

                subsection_title = line[4:].strip()
                current_subsection = subsection_title
                continue

            # Add content to buffer
            if line:
                buffer.append(line)

        # Save final buffer
        if current_section and buffer:
            self._save_buffer(content, current_section, current_subsection, buffer)

        return content

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text"""
        # Remove bold **text**
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        # Remove italic *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        # Remove H1 #
        text = re.sub(r'^#\s+', '', text, flags=re.MULTILINE)
        return text.strip()

    def _save_buffer(self, content: Dict, section: str, subsection: Optional[str], buffer: list):
        """Save buffered lines to appropriate content section"""
        text = '\n'.join(buffer).strip()

        if section == '요약':
            content['summary'] = self._clean_markdown(text)

        elif section == '키워드':
            # Parse keywords: - 휴식 • 집중 • 학습
            keywords_line = text.replace('- ', '').replace('•', ' ')
            content['keywords'] = [kw.strip() for kw in keywords_line.split() if kw.strip()]

        elif section == '리듬 해설':
            content['rhythm_description'] = self._clean_markdown(text)

        elif section == '집중/주의 포인트':
            if subsection == '집중':
                content['focus_caution']['focus'] = self._parse_bullet_list(buffer)
            elif subsection == '주의':
                content['focus_caution']['caution'] = self._parse_bullet_list(buffer)

        elif section == '행동 가이드':
            if subsection == '권장':
                content['action_guide']['do'] = self._parse_bullet_list(buffer)
            elif subsection == '지양':
                content['action_guide']['avoid'] = self._parse_bullet_list(buffer)

        elif section == '시간/방향':
            # Handle subsections with colons (좋은 시간:, 피할 시간:, etc.)
            if subsection:
                subsection_clean = subsection.rstrip(':')
                bullet_items = self._parse_bullet_list(buffer)
                combined_text = ', '.join(bullet_items) if bullet_items else ''

                if '좋은 시간' in subsection_clean:
                    content['time_direction']['good_time'] = combined_text
                elif '피할 시간' in subsection_clean:
                    content['time_direction']['avoid_time'] = combined_text
                elif '좋은 방향' in subsection_clean:
                    content['time_direction']['good_direction'] = combined_text
                elif '피할 방향' in subsection_clean:
                    content['time_direction']['avoid_direction'] = combined_text

        elif section == '상태 전환 트리거':
            # Handle subsections with colons (제스처:, 문구:, 방법:)
            if subsection:
                subsection_clean = subsection.rstrip(':')
                bullet_items = self._parse_bullet_list(buffer)
                combined_text = ', '.join(bullet_items) if bullet_items else ''

                if '제스처' in subsection_clean:
                    content['state_trigger']['gesture'] = combined_text
                elif '문구' in subsection_clean:
                    content['state_trigger']['phrase'] = combined_text
                elif '방법' in subsection_clean:
                    content['state_trigger']['how_to'] = combined_text

        elif section == '의미 전환':
            content['meaning_shift'] = self._clean_markdown(text)

        elif section == '리듬 질문':
            # Remove leading "- " if present
            content['rhythm_question'] = self._clean_markdown(text.lstrip('- '))

    def _parse_bullet_list(self, lines: list) -> list:
        """Parse markdown bullet list into array"""
        items = []
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                # Remove bullet and clean markdown
                item = line[2:].strip()
                # Remove markdown bold (**text**)
                item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)
                items.append(item)
        return items

    def generate_daily_pdf(
        self,
        content: Dict[str, Any],
        output_path: str,
        role: Optional[str] = None,
        is_markdown: bool = False
    ) -> str:
        """
        Generate daily page PDF from DailyContent

        Args:
            content: DailyContent 딕셔너리 (DAILY_CONTENT_SCHEMA 준수) 또는 Markdown 문자열
            output_path: PDF 저장 경로
            role: 역할 (student, office_worker, freelancer)
            is_markdown: True if content is Markdown string, False if dict

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
        # If content is Markdown string, parse it first
        if is_markdown:
            if isinstance(content, str):
                content = self._parse_markdown_to_dict(content)
            else:
                raise ValueError("When is_markdown=True, content must be a string")

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
