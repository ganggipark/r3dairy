"""
Content Validator
DAILY_CONTENT_SCHEMA.json 준수 검증 및 품질 체크
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from .models import DailyContent, MonthlyContent, YearlyContent


class ContentValidator:
    """콘텐츠 검증기"""

    def __init__(self, schema_path: str = None):
        """
        Args:
            schema_path: DAILY_CONTENT_SCHEMA.json 경로
        """
        if schema_path is None:
            # 기본 경로: docs/content/DAILY_CONTENT_SCHEMA.json
            project_root = Path(__file__).parent.parent.parent.parent
            schema_path = project_root / "docs" / "content" / "DAILY_CONTENT_SCHEMA.json"

        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """스키마 파일 로드"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_daily_content(self, content: DailyContent) -> Tuple[bool, List[str]]:
        """
        DailyContent 검증

        Args:
            content: 검증할 DailyContent 객체

        Returns:
            (검증 통과 여부, 오류/경고 메시지 리스트)
        """
        errors = []
        warnings = []

        # 1. Pydantic 모델 검증은 이미 통과 (생성 시 자동 검증)

        # 2. 길이 요구사항 검증
        is_valid, total_chars, message = content.validate_length_requirements()
        if not is_valid:
            errors.append(message)
        elif total_chars < 600:  # 목표 미달 시 경고
            warnings.append(message)

        # 3. 키워드 검증
        if len(content.keywords) < 2:
            errors.append("키워드가 2개 미만입니다")
        if len(content.keywords) > 5:
            errors.append("키워드가 5개를 초과합니다")

        # 4. 내부 전문 용어 사용 검증 (사용자 노출 금지)
        forbidden_terms = self._check_forbidden_terms(content)
        if forbidden_terms:
            errors.append(f"내부 전문 용어 사용 감지: {', '.join(forbidden_terms)}")

        # 5. 설명형 문단 존재 여부 (카드 전용 요약 금지)
        if len(content.rhythm_description) < 100:
            errors.append("리듬 해설이 너무 짧습니다 (최소 100자)")

        # 6. 각 블록별 내용 존재 여부
        if not content.focus_caution.focus:
            warnings.append("집중 포인트가 비어있습니다")
        if not content.focus_caution.caution:
            warnings.append("주의 포인트가 비어있습니다")
        if not content.action_guide.do:
            warnings.append("추천 행동이 비어있습니다")
        if not content.action_guide.avoid:
            warnings.append("피할 행동이 비어있습니다")

        # 결과 반환
        all_messages = errors + warnings
        return (len(errors) == 0, all_messages)

    def _check_forbidden_terms(self, content: DailyContent) -> List[str]:
        """
        내부 전문 용어 사용 검증

        금지 용어:
        - 사주명리, 기문둔갑, 천간, 지지, 오행, 십성
        - 대운, 세운, 월운, 일운
        - 천을귀인, 역마, 공망, 도화
        - NLP, 알고리즘, 엔진, 계산, 분석 모듈
        """
        forbidden_terms = [
            "사주명리", "사주", "기문둔갑", "천간", "지지", "오행", "십성",
            "대운", "세운", "월운", "일운",
            "천을귀인", "역마", "공망", "도화",
            "비견", "겁재", "식신", "상관", "편재", "정재", "편관", "정관", "편인", "정인",
            "NLP", "알고리즘", "엔진", "분석 모듈", "계산",
            "甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸",
            "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"
        ]

        # 전체 텍스트 수집
        all_text = " ".join([
            content.summary,
            " ".join(content.keywords),
            content.rhythm_description,
            " ".join(content.focus_caution.focus),
            " ".join(content.focus_caution.caution),
            " ".join(content.action_guide.do),
            " ".join(content.action_guide.avoid),
            content.time_direction.good_time,
            content.time_direction.avoid_time,
            content.time_direction.good_direction,
            content.time_direction.avoid_direction,
            content.time_direction.notes,
            content.state_trigger.gesture,
            content.state_trigger.phrase,
            content.state_trigger.how_to,
            content.meaning_shift,
            content.rhythm_question
        ])

        # 금지 용어 검색
        found_terms = []
        for term in forbidden_terms:
            if term in all_text:
                found_terms.append(term)

        return found_terms

    def validate_length_distribution(self, content: DailyContent) -> Dict[str, Any]:
        """
        콘텐츠 길이 분포 분석

        Returns:
            각 블록별 길이 정보
        """
        return {
            "summary": len(content.summary),
            "keywords_total": sum(len(k) for k in content.keywords),
            "rhythm_description": len(content.rhythm_description),
            "focus_points": sum(len(f) for f in content.focus_caution.focus),
            "caution_points": sum(len(c) for c in content.focus_caution.caution),
            "do_actions": sum(len(d) for d in content.action_guide.do),
            "avoid_actions": sum(len(a) for a in content.action_guide.avoid),
            "time_direction": (
                len(content.time_direction.good_time) +
                len(content.time_direction.avoid_time) +
                len(content.time_direction.good_direction) +
                len(content.time_direction.avoid_direction) +
                len(content.time_direction.notes)
            ),
            "state_trigger": (
                len(content.state_trigger.gesture) +
                len(content.state_trigger.phrase) +
                len(content.state_trigger.how_to)
            ),
            "meaning_shift": len(content.meaning_shift),
            "rhythm_question": len(content.rhythm_question),
            "total": content.get_total_text_length()
        }

    def generate_quality_report(self, content: DailyContent) -> Dict[str, Any]:
        """
        품질 리포트 생성

        Returns:
            검증 결과, 길이 분포, 개선 제안 등
        """
        # 검증 실행
        is_valid, messages = self.validate_daily_content(content)

        # 길이 분포 분석
        length_dist = self.validate_length_distribution(content)

        # 개선 제안
        suggestions = []
        if length_dist["rhythm_description"] < 150:
            suggestions.append("리듬 해설을 더 풍부하게 작성하세요 (현재: {}자, 권장: 150자 이상)".format(
                length_dist["rhythm_description"]
            ))
        if length_dist["meaning_shift"] < 80:
            suggestions.append("의미 전환 문장을 더 상세하게 작성하세요")
        if len(content.focus_caution.focus) < 3:
            suggestions.append("집중 포인트를 3개 이상 추가하세요")

        return {
            "is_valid": is_valid,
            "messages": messages,
            "length_distribution": length_dist,
            "total_chars": length_dist["total"],
            "target_chars": content.length_requirements.left_page_target_chars,
            "min_chars": content.length_requirements.left_page_min_chars,
            "completion_rate": (
                length_dist["total"] / content.length_requirements.left_page_target_chars * 100
            ),
            "suggestions": suggestions
        }


def validate_content(content: DailyContent) -> Tuple[bool, List[str]]:
    """
    편의 함수: DailyContent 검증

    Usage:
        is_valid, messages = validate_content(daily_content)
        if not is_valid:
            print("검증 실패:", messages)
    """
    validator = ContentValidator()
    return validator.validate_daily_content(content)


def get_quality_report(content: DailyContent) -> Dict[str, Any]:
    """
    편의 함수: 품질 리포트 생성

    Usage:
        report = get_quality_report(daily_content)
        print(f"총 글자 수: {report['total_chars']}")
        print(f"완성도: {report['completion_rate']:.1f}%")
    """
    validator = ContentValidator()
    return validator.generate_quality_report(content)
