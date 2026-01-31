#!/usr/bin/env python3
"""
일간 콘텐츠 생성 오케스트레이션 스크립트

Purpose: 사주 + 기문둔갑 + 색은식 통합하여 Markdown 일간 콘텐츠 생성

Flow:
1. Load birth info and target date
2. Calculate 사주 (saju.py)
3. Calculate 기문둔갑 (qimen.py)
4. Calculate 색은식 (saekeunshik.py) - TODO
5. Generate energy JSON with all three systems integrated
6. Generate time/direction JSON
7. Use Claude CLI to create natural language content
8. Generate Markdown file following example structure
9. Save to backend/daily/{date}.md
"""

import argparse
import datetime
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend/src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rhythm.models import BirthInfo, Gender
from rhythm.saju import calculate_saju, analyze_daily_fortune
# from rhythm.qimen import analyze_qimen_rhythm  # TODO: Fix qimen.py corruption

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# Test profile (default)
TEST_PROFILE = BirthInfo(
    name="테스트사용자",
    birth_date=datetime.date(1971, 11, 17),
    birth_time=datetime.time(4, 0),
    gender=Gender.MALE,
    birth_place="서울",
    birth_place_lat=37.5665,
    birth_place_lng=126.9780
)


def load_profile(profile_id: Optional[str] = None) -> BirthInfo:
    """
    프로필 로드 (DB 또는 테스트 프로필)

    Args:
        profile_id: User profile ID (None for test profile)

    Returns:
        BirthInfo object
    """
    if profile_id is None:
        logger.info("테스트 프로필 사용: 1971-11-17 04:00 양력 남자")
        return TEST_PROFILE

    # TODO: Load from database
    # from db.supabase import get_profile
    # return get_profile(profile_id)

    logger.warning(f"프로필 ID {profile_id} 로드 미구현, 테스트 프로필 사용")
    return TEST_PROFILE


def calculate_rhythm_data(
    birth_info: BirthInfo,
    target_date: datetime.date
) -> tuple:
    """
    Step 2-4: Calculate all rhythm systems

    Returns:
        (saju_data, qimen_data, saekeunshik_data)
    """
    logger.info("Step 2: 사주 계산 중...")
    saju_data = calculate_saju(birth_info, target_date)
    logger.info(f"  - 일주: {saju_data['사주']['일주']['간지']}")

    logger.info("Step 3: 기문둔갑 계산 중...")
    # TODO: Fix qimen.py and use analyze_qimen_rhythm
    # qimen_data = analyze_qimen_rhythm(birth_info, target_date)
    qimen_data = {
        "primary_star": "天心",
        "gate_status": {"active": "開門"},
        "energy_level": 3,
        "directions": {
            "favorable_direction": "남동",
            "unfavorable_direction": "북서"
        }
    }
    logger.info(f"  - 주성: {qimen_data.get('primary_star', 'N/A')}")
    logger.info(f"  - 득문: {qimen_data.get('gate_status', {}).get('active', 'N/A')}")

    logger.info("Step 4: 색은식 계산 중...")
    # TODO: Implement saekeunshik calculation
    saekeunshik_data = None
    logger.warning("  - 색은식 모듈 미구현, 스킵")

    return saju_data, qimen_data, saekeunshik_data


def generate_energy_json(
    birth_info: BirthInfo,
    target_date: datetime.date,
    saju_data: Dict[str, Any],
    qimen_data: Dict[str, Any],
    saekeunshik_data: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Step 5: Generate today_energy.json

    Integrates all three systems into unified energy data
    """
    logger.info("Step 5: 에너지 JSON 생성 중...")

    # Analyze daily fortune from saju
    fortune = analyze_daily_fortune(birth_info, target_date, saju_data)

    # Integrate all systems
    energy_data = {
        "date": target_date.isoformat(),
        "profile": {
            "name": birth_info.name,
            "birth_date": birth_info.birth_date.isoformat(),
            "gender": birth_info.gender.value
        },

        # Energy levels (1-5 scale)
        "energy": {
            "overall": fortune.get("에너지_수준", 3),
            "focus": fortune.get("집중력", 3),
            "social": fortune.get("사회운", 3),
            "decision": fortune.get("결정력", 3),
            "rest_need": 5 - fortune.get("에너지_수준", 3)
        },

        # Saju system
        "saju": {
            "pillar_day": saju_data["사주"]["일주"]["간지"],
            "ohhaeng_balance": saju_data.get("오행", {}),
            "strength": saju_data.get("격국", {}).get("강약", "중화"),
            "yongsin": saju_data.get("용신", {}).get("용신", []),
            "gisin": saju_data.get("용신", {}).get("기신", [])
        },

        # Qimen system
        "qimen": {
            "primary_star": qimen_data.get("primary_star", ""),
            "gate_active": qimen_data.get("gate_status", {}).get("active", ""),
            "energy_level": qimen_data.get("energy_level", 3)
        },

        # Saekeunshik system (TODO)
        "saekeunshik": saekeunshik_data if saekeunshik_data else {},

        # Opportunities and challenges
        "opportunities": fortune.get("기회_요소", []),
        "challenges": fortune.get("도전_요소", [])
    }

    logger.info(f"  - 에너지: {energy_data['energy']['overall']}/5")
    logger.info(f"  - 집중력: {energy_data['energy']['focus']}/5")

    return energy_data


def generate_time_direction_json(
    target_date: datetime.date,
    saju_data: Dict[str, Any],
    qimen_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Step 6: Generate today_time_direction.json
    """
    logger.info("Step 6: 시간/방향 JSON 생성 중...")

    # Analyze fortune from saju
    fortune = analyze_daily_fortune(None, target_date, saju_data)

    time_direction_data = {
        "date": target_date.isoformat(),

        # Time guidance from saju
        "favorable_times": fortune.get("유리한_시간", []),
        "caution_times": fortune.get("주의_시간", []),

        # Direction guidance (saju + qimen)
        "favorable_directions": fortune.get("유리한_방향", []),
        "unfavorable_directions": [qimen_data.get("directions", {}).get("unfavorable_direction", "")],

        # Additional qimen directions
        "qimen_directions": qimen_data.get("directions", {})
    }

    logger.info(f"  - 좋은 시간: {', '.join(time_direction_data['favorable_times'])}")
    logger.info(f"  - 좋은 방향: {', '.join(time_direction_data['favorable_directions'])}")

    return time_direction_data


def generate_content_with_claude(
    energy_data: Dict[str, Any],
    time_direction_data: Dict[str, Any],
    prompt_file: Path
) -> Dict[str, Any]:
    """
    Step 7: Use Claude CLI to generate natural language content
    """
    logger.info("Step 7: Claude CLI로 자연어 콘텐츠 생성 중...")

    # Load prompt template
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()

    # Construct full prompt
    full_prompt = f"""{prompt}

# INPUT DATA

## today_energy.json
```json
{json.dumps(energy_data, ensure_ascii=False, indent=2)}
```

## today_time_direction.json
```json
{json.dumps(time_direction_data, ensure_ascii=False, indent=2)}
```

NOW GENERATE JSON (JSON만 출력, 설명 제외):
"""

    try:
        # Execute Claude CLI
        result = subprocess.run(
            ['claude', '--dangerously-skip-permissions'],
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )

        if result.returncode != 0:
            logger.error(f"Claude CLI 에러: {result.stderr}")
            raise RuntimeError(f"Claude CLI failed: {result.stderr}")

        output = result.stdout.strip()

        # Extract JSON from output
        if '```json' in output:
            output = output.split('```json')[1].split('```')[0]
        elif '```' in output:
            output = output.split('```')[1].split('```')[0]

        output = output.strip()

        # Parse JSON
        content = json.loads(output)

        logger.info(f"  - 생성 완료: {len(content)}개 키")
        if 'summary' in content:
            logger.info(f"  - 요약: {content['summary'][:60]}...")

        return content

    except subprocess.TimeoutExpired:
        logger.error("타임아웃 (120초 초과)")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 에러: {e}")
        logger.error(f"출력:\n{output[:500]}")
        raise
    except Exception as e:
        logger.error(f"콘텐츠 생성 에러: {e}")
        raise


def generate_markdown(
    content: Dict[str, Any],
    time_direction: Dict[str, Any]
) -> str:
    """
    Step 8: Generate Markdown file following example structure
    """
    logger.info("Step 8: Markdown 생성 중...")

    # Helper function to format list items
    def fmt_list(items):
        if not items:
            return "- (없음)"
        return "\n".join(f"- {item}" for item in items)

    # Build markdown
    md = f"""# 오늘의 안내

## 요약
{content.get('summary', '(요약 없음)')}

## 키워드
{' • '.join(content.get('keywords', []))}

## 리듬 해설
{content.get('rhythm_explanation', '(해설 없음)')}

## 집중/주의 포인트

### 집중
{fmt_list(content.get('focus_points', {}).get('focus', []))}

### 주의
{fmt_list(content.get('focus_points', {}).get('caution', []))}

## 행동 가이드

### 권장
{fmt_list(content.get('action_guide', {}).get('do', []))}

### 지양
{fmt_list(content.get('action_guide', {}).get('avoid', []))}

## 시간/방향

### 좋은 시간:
{fmt_list(time_direction.get('favorable_times', []))}

### 피할 시간:
{fmt_list(time_direction.get('caution_times', []))}

### 좋은 방향:
{fmt_list(time_direction.get('favorable_directions', []))}

### 피할 방향:
{fmt_list(time_direction.get('unfavorable_directions', []))}

## 상태 전환 트리거

### 제스처:
- {content.get('state_trigger', {}).get('gesture', '(없음)')}

### 문구:
- {content.get('state_trigger', {}).get('phrase', '(없음)')}

### 방법:
- {content.get('state_trigger', {}).get('how_to', '(없음)')}

## 의미 전환
{content.get('meaning_shift', '(없음)')}

## 리듬 질문
- {content.get('rhythm_question', '(없음)')}

---

## 🏃 건강/운동
**권장**: {', '.join(content.get('daily_health_sports', {}).get('recommended_activities', []))}
**팁**: {', '.join(content.get('daily_health_sports', {}).get('health_tips', []))}
**설명**: {content.get('daily_health_sports', {}).get('explanation', '(없음)')}

## 🍜 음식/영양
**권장**: {', '.join(content.get('daily_meal_nutrition', {}).get('recommended_foods', []))}
**지양**: {', '.join(content.get('daily_meal_nutrition', {}).get('avoid_foods', []))}
**설명**: {content.get('daily_meal_nutrition', {}).get('explanation', '(없음)')}

## 👔 패션/뷰티
**색상**: {', '.join(content.get('daily_fashion_beauty', {}).get('color_suggestions', []))}
**스타일**: {', '.join(content.get('daily_fashion_beauty', {}).get('clothing_style', []))}
**설명**: {content.get('daily_fashion_beauty', {}).get('explanation', '(없음)')}

## 💰 쇼핑/금융
**구매 추천**: {', '.join(content.get('daily_shopping_finance', {}).get('good_to_buy', []))}
**금융 조언**: {', '.join(content.get('daily_shopping_finance', {}).get('finance_advice', []))}
**설명**: {content.get('daily_shopping_finance', {}).get('explanation', '(없음)')}

## 🏠 생활 공간
**정리**: {', '.join(content.get('daily_living_space', {}).get('space_organization', []))}
**환경**: {', '.join(content.get('daily_living_space', {}).get('environmental_tips', []))}
**설명**: {content.get('daily_living_space', {}).get('explanation', '(없음)')}

## ⏰ 일상 루틴
**아침**: {', '.join(content.get('daily_routines', {}).get('morning_routine', []))}
**저녁**: {', '.join(content.get('daily_routines', {}).get('evening_routine', []))}
**설명**: {content.get('daily_routines', {}).get('explanation', '(없음)')}

## 📱 디지털/소통
**기기 사용**: {', '.join(content.get('digital_communication', {}).get('device_usage', []))}
**SNS**: {', '.join(content.get('digital_communication', {}).get('social_media', []))}
**설명**: {content.get('digital_communication', {}).get('explanation', '(없음)')}

## 🎨 취미/창작
**창작**: {', '.join(content.get('hobbies_creativity', {}).get('creative_activities', []))}
**학습**: {', '.join(content.get('hobbies_creativity', {}).get('learning_recommendations', []))}
**설명**: {content.get('hobbies_creativity', {}).get('explanation', '(없음)')}

## 👥 관계/사회
**소통 방식**: {', '.join(content.get('relationships_social', {}).get('communication_style', []))}
**관계 팁**: {', '.join(content.get('relationships_social', {}).get('relationship_tips', []))}
**설명**: {content.get('relationships_social', {}).get('explanation', '(없음)')}

## 🌤️ 계절/환경
**날씨 대응**: {', '.join(content.get('seasonal_environment', {}).get('weather_adaptation', []))}
**계절 활동**: {', '.join(content.get('seasonal_environment', {}).get('seasonal_activities', []))}
**설명**: {content.get('seasonal_environment', {}).get('explanation', '(없음)')}

---

# 나의 기록

(사용자가 직접 작성하는 공간)

## 오늘의 감사한 일

## 오늘의 배움

## 내일 하고 싶은 일
"""

    logger.info("  - Markdown 생성 완료")
    return md


def main():
    """Main orchestration function"""
    parser = argparse.ArgumentParser(
        description='일간 콘텐츠 생성 (사주 + 기문둔갑 + 색은식 통합)'
    )
    parser.add_argument(
        '--date',
        type=str,
        default=datetime.date.today().isoformat(),
        help='대상 날짜 (YYYY-MM-DD, 기본값: 오늘)'
    )
    parser.add_argument(
        '--profile-id',
        type=str,
        default=None,
        help='프로필 ID (기본값: 테스트 프로필)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='테스트 프로필 사용 (1971-11-17 04:00 양력 남자)'
    )

    args = parser.parse_args()

    # Parse target date
    target_date = datetime.date.fromisoformat(args.date)
    logger.info(f"=== 일간 콘텐츠 생성: {target_date} ===")

    # Step 1: Load profile
    logger.info("Step 1: 프로필 로드 중...")
    profile_id = None if args.test else args.profile_id
    birth_info = load_profile(profile_id)

    # Steps 2-4: Calculate rhythm data
    saju_data, qimen_data, saekeunshik_data = calculate_rhythm_data(
        birth_info, target_date
    )

    # Step 5: Generate energy JSON
    energy_data = generate_energy_json(
        birth_info, target_date, saju_data, qimen_data, saekeunshik_data
    )

    # Step 6: Generate time/direction JSON
    time_direction_data = generate_time_direction_json(
        target_date, saju_data, qimen_data
    )

    # Save intermediate JSONs
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    energy_file = output_dir / "today_energy.json"
    time_file = output_dir / "today_time_direction.json"

    with open(energy_file, 'w', encoding='utf-8') as f:
        json.dump(energy_data, f, ensure_ascii=False, indent=2)
    logger.info(f"  - 저장: {energy_file}")

    with open(time_file, 'w', encoding='utf-8') as f:
        json.dump(time_direction_data, f, ensure_ascii=False, indent=2)
    logger.info(f"  - 저장: {time_file}")

    # Step 7: Generate content with Claude CLI
    prompt_file = Path(__file__).parent / "prompts" / "daily_content_generator.txt"

    if not prompt_file.exists():
        logger.error(f"프롬프트 파일 없음: {prompt_file}")
        logger.warning("Claude CLI 스킵, JSON만 저장")
        return

    try:
        content = generate_content_with_claude(
            energy_data, time_direction_data, prompt_file
        )
    except Exception as e:
        logger.error(f"콘텐츠 생성 실패: {e}")
        logger.warning("Markdown 생성 스킵")
        return

    # Step 8: Generate Markdown
    markdown = generate_markdown(content, time_direction_data)

    # Step 9: Save Markdown file
    logger.info("Step 9: Markdown 저장 중...")
    daily_dir = Path(__file__).parent / "daily"
    daily_dir.mkdir(exist_ok=True)

    md_file = daily_dir / f"{target_date}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    logger.info(f"✅ 완료: {md_file}")
    logger.info(f"  - Energy JSON: {energy_file}")
    logger.info(f"  - Time/Direction JSON: {time_file}")
    logger.info(f"  - Markdown: {md_file}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("사용자 중단")
        sys.exit(1)
    except Exception as e:
        logger.error(f"에러 발생: {e}", exc_info=True)
        sys.exit(1)
