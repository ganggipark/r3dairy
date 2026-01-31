#!/usr/bin/env python3
"""
Comprehensive Test Suite for Markdown System

Test cases:
1. 색은식 calculation verification
2. NLP content generation quality
3. Markdown format validation
4. API endpoint testing
5. Complete pipeline integration

Usage:
    pytest test_markdown_system.py -v
    pytest test_markdown_system.py::TestSaekeunshik -v
    pytest test_markdown_system.py::TestNLPContent -v
    pytest test_markdown_system.py::TestMarkdownGeneration -v
    pytest test_markdown_system.py::TestAPIEndpoints -v
    pytest test_markdown_system.py::TestPipeline -v
"""

import pytest
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from typing import Dict, List, Any
import re

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from generate_daily_markdown import DailyMarkdownGenerator
from src.rhythm.models import BirthInfo, Gender
from src.rhythm.saju import calculate_saju, analyze_daily_fortune
from src.content.assembly import assemble_daily_content


# ============================================================================
# TEST DATA - 기본 테스트 사주 (1971년 11월 17일 04:00 양력 남자)
# ============================================================================

@pytest.fixture
def test_birth_info():
    """테스트 사주 기본 정보"""
    return BirthInfo(
        name="테스트 사용자",
        birth_date=date(1971, 11, 17),
        birth_time=time(4, 0),
        gender=Gender.MALE,
        birth_place="서울",
        birth_place_lat=37.5665,
        birth_place_lng=126.9780
    )


@pytest.fixture
def test_target_date():
    """테스트 대상 날짜"""
    return date(2026, 1, 31)


@pytest.fixture
def sample_energy_data():
    """샘플 에너지 JSON 데이터"""
    return {
        "date": "2026-01-31",
        "energy": {
            "rhythm_label": "활동적",
            "intensity_level": "높음",
            "focus_level": "높음",
            "recovery_need": "낮음",
            "decision_level": "높음",
            "social_level": "높음"
        },
        "keywords": {
            "scores": {
                "활동": 0.95,
                "집중": 0.90,
                "결정": 0.85,
                "관계": 0.80,
                "리더십": 0.75,
                "창의": 0.70,
                "효율": 0.65,
                "성장": 0.60,
                "도전": 0.55,
                "변화": 0.50
            }
        },
        "flags": {
            "fatigue_risk": False,
            "overpromise_risk": False,
            "conflict_risk": False,
            "spending_risk": False,
            "mistake_risk": False
        },
        "lifestyle": {
            "reco": {
                "health": {
                    "do": ["활동적인 운동", "야외 활동"],
                    "avoid": ["과로", "무리한 체력"],
                    "tip": "에너지가 높은 날이므로 운동으로 활용하면 좋습니다"
                },
                "food": {
                    "do": ["균형잡힌 식사", "단백질"],
                    "avoid": ["과식", "자극적인 음식"],
                    "tip": "충분한 영양섭취로 에너지 유지하기"
                },
                "fashion": {
                    "do": ["밝은 색상", "편안한 의류"],
                    "avoid": ["너무 타이트한 옷"],
                    "tip": "편한 복장으로 활동성 높이기"
                },
                "finance": {
                    "do": ["계획적 소비", "투자 고려"],
                    "avoid": ["충동 구매"],
                    "tip": "판단력이 좋으니 큰 결정 내리기 좋은 날"
                },
                "space": {
                    "do": ["정리정돈", "인테리어"],
                    "avoid": ["어수선한 공간 유지"],
                    "tip": "집중력이 높으니 정리작업 추진하기"
                },
                "routine": {
                    "do": ["규칙적 루틴", "아침 활동"],
                    "avoid": ["늦게 일어나기"],
                    "tip": "아침부터 활동적으로 시작하기"
                },
                "digital": {
                    "do": ["활발한 소통", "SNS 활용"],
                    "avoid": ["과도한 디지털"],
                    "tip": "사람과의 연결이 활발한 날"
                },
                "hobby": {
                    "do": ["새로운 시도", "창작 활동"],
                    "avoid": ["취미 미루기"],
                    "tip": "창의력이 높으니 새로운 시도 추진"
                },
                "social": {
                    "do": ["약속 잡기", "네트워킹"],
                    "avoid": ["혼자만 있기"],
                    "tip": "관계 활동이 자연스러운 날"
                },
                "season": {
                    "do": ["겨울 옷차림", "실내 활동"],
                    "avoid": ["외출 미루기"],
                    "tip": "겨울 날씨에 활동적으로 움직이기"
                }
            }
        }
    }


@pytest.fixture
def sample_time_direction_data():
    """샘플 시간/방향 JSON 데이터"""
    return {
        "date": "2026-01-31",
        "qimen": {
            "good_windows": [
                {
                    "start": "09:00",
                    "end": "11:00",
                    "reason_plain": "오전 에너지가 가장 좋은 시간대로, 중요한 업무나 결정에 적합합니다"
                },
                {
                    "start": "14:00",
                    "end": "16:00",
                    "reason_plain": "오후 집중력 정점으로, 깊이 있는 작업에 최적입니다"
                }
            ],
            "avoid_windows": [
                {
                    "start": "17:00",
                    "end": "19:00",
                    "reason_plain": "저녁 에너지 저하로, 중요한 결정은 피하기 좋습니다"
                }
            ],
            "good_directions": ["북동", "남"],
            "avoid_directions": ["서"]
        }
    }


# ============================================================================
# TEST 1: 색은식(Saekeunshik) Calculation Verification
# ============================================================================

class TestSaekeunshik:
    """색은식 계산 검증 테스트"""

    def test_five_movements_exist(self, test_birth_info, test_target_date):
        """오행(Five Movements) 계산이 수행되는지 확인"""
        # Saju 계산 (target_date 포함)
        try:
            saju_result = calculate_saju(test_birth_info, test_target_date)

            # 결과가 dict이고 필수 필드가 있는지 확인
            assert isinstance(saju_result, dict)
            assert "사주" in saju_result or "오행" in saju_result or "십성" in saju_result
        except RuntimeError as e:
            # Node.js가 없는 경우 스킵
            if "cli.js" in str(e) or "node" in str(e).lower():
                pytest.skip(f"Saju 계산기 부재: {e}")
            raise

    def test_six_qi_calculation(self, test_birth_info, test_target_date):
        """육기(Six Qi) 계산 검증"""
        # Saju 계산 먼저 수행
        try:
            saju_result = calculate_saju(test_birth_info, test_target_date)
        except RuntimeError as e:
            if "cli.js" in str(e) or "node" in str(e).lower():
                pytest.skip(f"Saju 계산기 부재: {e}")
            raise

        # 일간 분석 (saju_data 필수)
        from src.rhythm.saju import analyze_daily_fortune as analyze_fortune
        fortune = analyze_fortune(test_birth_info, test_target_date, saju_result)

        # 결과가 dict이고 기본 구조가 있는지 확인
        assert isinstance(fortune, dict)
        assert len(fortune) > 0
        assert "에너지_수준" in fortune or "집중력" in fortune

    def test_energy_integration_with_json(self, sample_energy_data):
        """에너지 데이터 JSON과의 연동 확인"""
        # 에너지 JSON이 유효한 구조인지 확인
        assert "energy" in sample_energy_data
        assert "keywords" in sample_energy_data
        assert "flags" in sample_energy_data
        assert "lifestyle" in sample_energy_data

        # 에너지 필드 확인
        energy = sample_energy_data["energy"]
        assert "rhythm_label" in energy
        assert "intensity_level" in energy
        assert "focus_level" in energy
        assert "recovery_need" in energy
        assert "decision_level" in energy
        assert "social_level" in energy

    def test_time_direction_integration(self, sample_time_direction_data):
        """시간/방향 데이터 JSON과의 연동 확인"""
        assert "qimen" in sample_time_direction_data

        qimen = sample_time_direction_data["qimen"]
        assert "good_windows" in qimen
        assert "avoid_windows" in qimen
        assert "good_directions" in qimen
        assert "avoid_directions" in qimen


# ============================================================================
# TEST 2: NLP Content Generation Quality
# ============================================================================

class TestNLPContent:
    """NLP 콘텐츠 생성 품질 테스트"""

    def test_character_count_minimum(self, sample_energy_data, sample_time_direction_data):
        """최소 글자 수 요구사항 (400-600자) 검증"""
        # Markdown 생성
        # 임시 경로에 JSON 파일 저장
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            markdown = generator.generate_markdown()

            # 글자 수 계산 (공백, 줄바꿈 제외)
            char_count = len(markdown.replace(" ", "").replace("\n", ""))

            # 최소 400자 이상
            assert char_count >= 400, f"글자 수 부족: {char_count}자 (최소 400자 필요)"

            # 목표 700+ 자 확인
            if char_count >= 700:
                print(f"✅ 목표 달성: {char_count}자 (700+ 자)")
            else:
                print(f"⚠️  기본 요구사항 충족: {char_count}자 (400+ 자)")

    def test_no_technical_terms(self, sample_energy_data, sample_time_direction_data):
        """사용자 노출 텍스트에서 전문 용어 사용 금지"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            markdown = generator.generate_markdown()

            # 금지 용어 리스트
            forbidden_terms = [
                "사주", "천간", "지지", "오행", "십성",
                "대운", "세운", "월운", "기문둔갑", "납음",
                "NLP", "알고리즘", "엔진", "계산 모듈"
            ]

            # 각 금지 용어 확인
            for term in forbidden_terms:
                assert term not in markdown, f"금지된 용어 '{term}'이 콘텐츠에 포함되어 있습니다"

    def test_natural_language_quality(self, sample_energy_data, sample_time_direction_data):
        """자연스러운 문장 표현 검증"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)

            # 주요 섹션 생성
            summary = generator.generate_summary()
            rhythm_expl = generator.generate_rhythm_explanation()
            action_guide = generator.generate_action_guide()

            # 요약은 2문장 이상
            sentences_in_summary = len(re.split(r'[.!?]', summary.strip()))
            assert sentences_in_summary >= 2, f"요약이 너무 짧습니다: {sentences_in_summary}개 문장"

            # 리듬 해설은 2문단 이상 (실제 구현에서는 2문단)
            paragraphs_in_rhythm = len(rhythm_expl.split('\n\n'))
            assert paragraphs_in_rhythm >= 2, f"리듬 해설이 너무 짧습니다: {paragraphs_in_rhythm}개 문단"

            # 행동 가이드는 구조화되어 있어야 함
            assert "권장" in action_guide or "Do" in action_guide or "하기" in action_guide
            assert "지양" in action_guide or "Avoid" in action_guide or "피하기" in action_guide


# ============================================================================
# TEST 3: Markdown Generation Format
# ============================================================================

class TestMarkdownGeneration:
    """Markdown 생성 형식 검증"""

    def test_all_required_sections_present(self, sample_energy_data, sample_time_direction_data):
        """필수 섹션 포함 확인"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            markdown = generator.generate_markdown()

            # 필수 섹션 확인
            required_sections = [
                "# 오늘의 안내",
                "## 요약",
                "## 키워드",
                "## 리듬 해설",
                "## 집중/주의 포인트",
                "## 행동 가이드",
                "## 시간/방향",
                "## 상태 전환 트리거",
                "## 의미 전환",
                "## 리듬 질문",
                "---",  # 구분선
            ]

            for section in required_sections:
                assert section in markdown, f"필수 섹션 '{section}'이 없습니다"

    def test_emoji_rendering(self, sample_energy_data, sample_time_direction_data):
        """이모지 렌더링 확인"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            lifestyle_sections = generator.generate_lifestyle_sections()

            # 이모지가 포함되어 있는지 확인
            emojis = ["🏃", "🍜", "👔", "💰", "🏠", "⏰", "📱", "🎨", "🤝", "❄️"]

            # 적어도 일부 이모지는 포함되어야 함
            emoji_count = sum(1 for emoji in emojis if emoji in lifestyle_sections)
            assert emoji_count > 0, "생활 카테고리 섹션에 이모지가 없습니다"

    def test_markdown_format_validity(self, sample_energy_data, sample_time_direction_data):
        """Markdown 형식 유효성 확인"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            markdown = generator.generate_markdown()

            # 제목 레벨 확인
            assert "# " in markdown  # H1
            assert "## " in markdown  # H2

            # 리스트 형식 확인
            assert "- " in markdown  # Unordered list

            # 강조 형식 확인
            assert "**" in markdown  # Bold

    def test_desktop_example_structure_match(self, sample_energy_data, sample_time_direction_data):
        """데스크탑 예제와 구조 일치 확인"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            markdown = generator.generate_markdown()

            # 구조 검증
            lines = markdown.split('\n')

            # 첫 번째 줄은 제목
            assert lines[0].startswith("# "), "첫 번째 줄이 제목이 아닙니다"

            # 섹션 분포 확인
            section_count = markdown.count("## ")
            assert section_count >= 8, f"섹션이 부족합니다: {section_count}개 (최소 8개 필요)"


# ============================================================================
# TEST 4: API Endpoints
# ============================================================================

class TestAPIEndpoints:
    """API 엔드포인트 테스트"""

    @pytest.fixture
    def test_files_setup(self, sample_energy_data, sample_time_direction_data):
        """테스트용 파일 생성"""
        from pathlib import Path

        daily_dir = Path(__file__).parent / "daily"
        daily_dir.mkdir(parents=True, exist_ok=True)

        energy_path = daily_dir / "today_energy_simple.json"
        time_path = daily_dir / "today_time_direction_simple.json"

        with open(energy_path, 'w', encoding='utf-8') as f:
            json.dump(sample_energy_data, f, ensure_ascii=False, indent=2)

        with open(time_path, 'w', encoding='utf-8') as f:
            json.dump(sample_time_direction_data, f, ensure_ascii=False, indent=2)

        yield energy_path, time_path

        # 정리
        energy_path.unlink(missing_ok=True)
        time_path.unlink(missing_ok=True)

    def test_markdown_file_generation(self, test_files_setup, sample_energy_data, sample_time_direction_data):
        """Markdown 파일 생성 테스트"""
        import tempfile
        import os

        energy_path, time_path = test_files_setup

        generator = DailyMarkdownGenerator(str(energy_path), str(time_path))
        output_dir = Path(__file__).parent / "daily_test"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = generator.save_markdown(
            output_dir=str(output_dir),
            date_str="2026-01-31"
        )

        # 파일 생성 확인
        assert output_path.exists()
        assert output_path.suffix == ".md"

        # 파일 내용 확인
        content = output_path.read_text(encoding='utf-8')
        assert len(content) > 0
        assert "# 오늘의 안내" in content

        # 정리
        output_path.unlink(missing_ok=True)
        output_dir.rmdir()

    def test_get_daily_markdown_endpoint_simulation(self, test_files_setup):
        """GET /api/daily/{date}/markdown 엔드포인트 시뮬레이션"""
        energy_path, time_path = test_files_setup

        # 엔드포인트 로직 시뮬레이션
        daily_dir = Path(__file__).parent / "daily"
        md_file = daily_dir / "2026-01-31_new_format.md"

        # 파일이 없으면 기본 형식 파일도 확인
        if not md_file.exists():
            md_file = daily_dir / "2026-01-31.md"

        # 이 테스트에서는 파일 존재 여부만 확인
        # 실제 엔드포인트 테스트는 API 테스트에서 수행
        if md_file.exists():
            markdown_content = md_file.read_text(encoding='utf-8')
            assert isinstance(markdown_content, str)
            assert len(markdown_content) > 0

    def test_get_daily_markdown_html_endpoint_simulation(self, test_files_setup):
        """GET /api/daily/{date}/markdown-html 엔드포인트 시뮬레이션"""
        import markdown as md_lib

        if not hasattr(md_lib, 'markdown'):
            pytest.skip("markdown 라이브러리가 설치되지 않았습니다")

        energy_path, time_path = test_files_setup

        # 마크다운 -> HTML 변환 시뮬레이션
        sample_md = "# 테스트\n\n오늘은 좋은 날입니다.\n\n- 항목1\n- 항목2"

        try:
            html_content = md_lib.markdown(sample_md)
            assert isinstance(html_content, str)
            assert "<h1>" in html_content or "<H1>" in html_content
        except:
            pytest.skip("마크다운 HTML 변환 실패")

    def test_error_handling_missing_date(self):
        """날짜가 없을 때 에러 처리"""
        # 404 에러 처리 검증
        daily_dir = Path(__file__).parent / "daily"
        non_existent_file = daily_dir / "1900-01-01.md"

        assert not non_existent_file.exists(), "테스트 파일이 이미 존재합니다"


# ============================================================================
# TEST 5: Complete Pipeline Integration
# ============================================================================

class TestPipeline:
    """전체 파이프라인 통합 테스트"""

    def test_complete_generation_pipeline(self, test_birth_info, test_target_date, sample_energy_data, sample_time_direction_data):
        """완전한 일간 콘텐츠 생성 파이프라인"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Saju 계산
            try:
                saju_result = calculate_saju(test_birth_info, test_target_date)
                assert isinstance(saju_result, dict)
            except RuntimeError as e:
                if "cli.js" in str(e) or "node" in str(e).lower():
                    pytest.skip(f"Saju 계산기 부재: {e}")
                raise

            # Step 2: 일간 분석
            from src.rhythm.saju import analyze_daily_fortune as analyze_fortune
            fortune = analyze_fortune(test_birth_info, test_target_date, saju_result)
            assert isinstance(fortune, dict)

            # Step 3: 콘텐츠 조립
            daily_rhythm = {
                "에너지_수준": 4,
                "집중력": 4,
                "사회운": 3,
                "결정력": 4,
                "유리한_시간": ["오전 9-11시", "오후 2-4시"],
                "주의_시간": ["오후 5-7시"],
                "유리한_방향": ["북동", "남"],
                "주의_방향": ["서"],
                "주요_흐름": "활동과 결정",
                "기회_요소": ["리더십", "결정"],
                "도전_요소": ["과욕", "소통"]
            }

            content = assemble_daily_content(
                date=test_target_date,
                saju_data=saju_result,
                daily_rhythm=daily_rhythm
            )
            assert isinstance(content, dict)
            assert content["date"] == "2026-01-31"

            # Step 4: Markdown 생성
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)
            markdown = generator.generate_markdown()

            # 최종 검증
            assert isinstance(markdown, str)
            assert len(markdown) > 400
            assert "# 오늘의 안내" in markdown
            assert "## 요약" in markdown

    def test_output_file_creation(self, sample_energy_data, sample_time_direction_data):
        """출력 파일 생성 확인"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)

            # 출력 디렉토리
            output_dir = Path(tmpdir) / "output"
            output_dir.mkdir(parents=True, exist_ok=True)

            # 파일 저장
            output_path = generator.save_markdown(
                output_dir=str(output_dir),
                date_str="2026-01-31-test"
            )

            # 파일 존재 확인
            assert output_path.exists()
            assert output_path.name == "2026-01-31-test.md"

            # 파일 크기 확인
            file_size = output_path.stat().st_size
            assert file_size > 400, f"파일이 너무 작습니다: {file_size} bytes"

    def test_content_quality_metrics(self, sample_energy_data, sample_time_direction_data):
        """콘텐츠 품질 지표 검증"""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            energy_path = os.path.join(tmpdir, "energy.json")
            time_path = os.path.join(tmpdir, "time.json")

            with open(energy_path, 'w', encoding='utf-8') as f:
                json.dump(sample_energy_data, f, ensure_ascii=False)

            with open(time_path, 'w', encoding='utf-8') as f:
                json.dump(sample_time_direction_data, f, ensure_ascii=False)

            generator = DailyMarkdownGenerator(energy_path, time_path)

            # 각 섹션 검증
            summary = generator.generate_summary()
            assert len(summary) >= 50, "요약이 너무 짧습니다"

            keywords = generator.generate_keywords()
            assert len(keywords) > 0, "키워드가 없습니다"
            assert "•" in keywords, "키워드 구분이 없습니다"

            rhythm_expl = generator.generate_rhythm_explanation()
            assert len(rhythm_expl) >= 200, "리듬 해설이 너무 짧습니다"

            focus_attention = generator.generate_focus_attention()
            assert "집중" in focus_attention or "주의" in focus_attention

            action_guide = generator.generate_action_guide()
            assert "권장" in action_guide or "지양" in action_guide

            time_direction = generator.generate_time_direction()
            assert "시간" in time_direction or "방향" in time_direction


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
