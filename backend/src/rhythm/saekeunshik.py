"""
색은식(五運六氣) 계산 모듈

五運六氣 이론은 한의학의 운기학설(運氣學說)로, 천체의 주기적 변화가
인체와 자연에 미치는 영향을 체계화한 이론입니다.

주요 개념:
- 五運(오운): 木運, 火運, 土運, 金運, 水運의 5가지 운(運)
  → 천간(天干)을 기준으로 계산하며, 년/월/일의 에너지 흐름을 나타냄

- 六氣(육기): 風, 熱, 濕, 火, 燥, 寒의 6가지 기(氣)
  → 지지(地支)를 기준으로 계산하며, 절기와 시간대별 기운을 나타냄
  → 사천(司天): 상반기 주기, 재천(在泉): 하반기 주기
  → 주기(主氣): 1년 6단계의 기본 기운

⚠️ 내부 전문 용어 사용 가능 (사용자 노출 시 변환 필수)
"""

import datetime
from typing import Dict, Any, List, Tuple
from datetime import date


# ==================== 천간-오운 매핑 ====================
# 천간 10개를 5운에 배치 (음양 구분)
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

STEM_TO_FIVE_MOVEMENTS = {
    "甲": "土運",  # 갑(甲) → 토운
    "乙": "金運",  # 을(乙) → 금운
    "丙": "水運",  # 병(丙) → 수운
    "丁": "木運",  # 정(丁) → 목운
    "戊": "火運",  # 무(戊) → 화운
    "己": "土運",  # 기(己) → 토운
    "庚": "金運",  # 경(庚) → 금운
    "辛": "水運",  # 신(辛) → 수운
    "壬": "木運",  # 임(壬) → 목운
    "癸": "火運",  # 계(癸) → 화운
}


# ==================== 지지-육기 매핑 ====================
# 지지 12개를 6기에 배치 (2개씩 묶음)
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 사천(司天) - 상반기 주도 기운
BRANCH_TO_SICHEON = {
    "子": "少陰君火",  # 자(子), 오(午) → 소음군화
    "午": "少陰君火",
    "丑": "太陰濕土",  # 축(丑), 미(未) → 태음습토
    "未": "太陰濕土",
    "寅": "少陽相火",  # 인(寅), 신(申) → 소양상화
    "申": "少陽相火",
    "卯": "陽明燥金",  # 묘(卯), 유(酉) → 양명조금
    "酉": "陽明燥金",
    "辰": "太陽寒水",  # 진(辰), 술(戌) → 태양한수
    "戌": "太陽寒水",
    "巳": "厥陰風木",  # 사(巳), 해(亥) → 궐음풍목
    "亥": "厥陰風木",
}

# 재천(在泉) - 하반기 주도 기운 (사천과 상극)
SICHEON_TO_JAECHEON = {
    "少陰君火": "陽明燥金",
    "太陰濕土": "太陽寒水",
    "少陽相火": "厥陰風木",
    "陽明燥金": "少陰君火",
    "太陽寒水": "太陰濕土",
    "厥陰風木": "少陽相火",
}

# 주기(主氣) - 1년 6단계 기본 기운 (절기 기준)
MAIN_QI_BY_SOLAR_TERM = [
    {"period": "입춘~춘분", "qi": "厥陰風木", "months": [2, 3]},
    {"period": "춘분~소만", "qi": "少陰君火", "months": [3, 4]},
    {"period": "소만~대서", "qi": "少陽相火", "months": [5, 6]},
    {"period": "대서~추분", "qi": "太陰濕土", "months": [7, 8]},
    {"period": "추분~소설", "qi": "陽明燥金", "months": [9, 10]},
    {"period": "소설~대한", "qi": "太陽寒水", "months": [11, 12, 1]},
]


# ==================== 오운 계산 ====================
def calculate_five_movements(birth_year: int, target_date: date) -> Dict[str, str]:
    """
    오운(五運) 계산: 년/월/일의 천간을 기준으로 5운 결정

    Args:
        birth_year: 출생 년도 (서기)
        target_date: 분석 대상 날짜

    Returns:
        {
            "year_movement": "土運",  # 년운
            "month_movement": "金運",  # 월운
            "day_movement": "水運",    # 일운
            "year_stem": "甲",         # 년 천간
            "month_stem": "乙",        # 월 천간
            "day_stem": "丙"           # 일 천간
        }
    """
    from .saju import calculate_saju
    from .models import BirthInfo, Gender

    # 임시 출생 정보 (천간 계산용)
    temp_birth_info = BirthInfo(
        name="임시",
        birth_date=date(birth_year, 1, 1),
        birth_time=datetime.time(12, 0),
        gender=Gender.MALE,
        birth_place="서울"
    )

    # 사주 계산으로 천간 추출
    saju_data = calculate_saju(temp_birth_info, target_date)

    year_stem = saju_data["사주"]["년주"]["천간"]
    month_stem = saju_data["사주"]["월주"]["천간"]
    day_stem = saju_data["사주"]["일주"]["천간"]

    return {
        "year_movement": STEM_TO_FIVE_MOVEMENTS.get(year_stem, "土運"),
        "month_movement": STEM_TO_FIVE_MOVEMENTS.get(month_stem, "土運"),
        "day_movement": STEM_TO_FIVE_MOVEMENTS.get(day_stem, "土運"),
        "year_stem": year_stem,
        "month_stem": month_stem,
        "day_stem": day_stem,
    }


# ==================== 육기 계산 ====================
def calculate_six_qi(birth_year: int, target_date: date) -> Dict[str, str]:
    """
    육기(六氣) 계산: 년/월의 지지를 기준으로 사천/재천/주기 결정

    Args:
        birth_year: 출생 년도
        target_date: 분석 대상 날짜

    Returns:
        {
            "sicheon": "少陰君火",      # 사천 (상반기 주도 기운)
            "jaecheon": "陽明燥金",     # 재천 (하반기 주도 기운)
            "dominant_qi": "厥陰風木",  # 주기 (현재 월의 기본 기운)
            "year_branch": "子",        # 년 지지
            "month_branch": "寅"        # 월 지지
        }
    """
    from .saju import calculate_saju
    from .models import BirthInfo, Gender

    # 임시 출생 정보 (지지 계산용)
    temp_birth_info = BirthInfo(
        name="임시",
        birth_date=date(birth_year, 1, 1),
        birth_time=datetime.time(12, 0),
        gender=Gender.MALE,
        birth_place="서울"
    )

    # 사주 계산으로 지지 추출
    saju_data = calculate_saju(temp_birth_info, target_date)

    year_branch = saju_data["사주"]["년주"]["지지"]
    month_branch = saju_data["사주"]["월주"]["지지"]

    # 사천 계산 (년지 기준)
    sicheon = BRANCH_TO_SICHEON.get(year_branch, "少陰君火")

    # 재천 계산 (사천의 상극)
    jaecheon = SICHEON_TO_JAECHEON.get(sicheon, "陽明燥金")

    # 주기 계산 (현재 월 기준)
    dominant_qi = get_dominant_qi_by_month(target_date.month)

    return {
        "sicheon": sicheon,
        "jaecheon": jaecheon,
        "dominant_qi": dominant_qi,
        "year_branch": year_branch,
        "month_branch": month_branch,
        "qi_phase": "상반기" if target_date.month <= 6 else "하반기",
    }


def get_dominant_qi_by_month(month: int) -> str:
    """
    월별 주기(主氣) 계산

    주기는 1년을 6단계로 나누어 각 절기에 해당하는 기운을 배정
    """
    for stage in MAIN_QI_BY_SOLAR_TERM:
        if month in stage["months"]:
            return stage["qi"]

    # 기본값 (겨울)
    return "太陽寒水"


# ==================== energy.json 통합 ====================
def integrate_with_energy_json(
    energy_data: Dict[str, Any],
    birth_year: int,
    target_date: date
) -> Dict[str, Any]:
    """
    기존 energy.json에 색은식 데이터 통합

    Args:
        energy_data: 기존 에너지 데이터 (사주/기문 분석 결과)
        birth_year: 출생 년도
        target_date: 분석 대상 날짜

    Returns:
        색은식 데이터가 추가된 energy.json 구조
        {
            ...기존 데이터,
            "saekeunshik": {
                "five_movements": {...},
                "six_qi": {...},
                "health_signals": {...}
            }
        }
    """
    # 오운 계산
    five_movements = calculate_five_movements(birth_year, target_date)

    # 육기 계산
    six_qi = calculate_six_qi(birth_year, target_date)

    # 건강 신호 생성 (오운육기 조합 해석)
    health_signals = generate_health_signals(five_movements, six_qi, target_date)

    # 기존 energy_data에 통합
    energy_data["saekeunshik"] = {
        "five_movements": five_movements,
        "six_qi": six_qi,
        "health_signals": health_signals,
        "calculation_date": target_date.isoformat(),
    }

    return energy_data


# ==================== 건강 신호 생성 ====================
def generate_health_signals(
    five_movements: Dict[str, str],
    six_qi: Dict[str, str],
    target_date: date
) -> Dict[str, Any]:
    """
    오운육기 조합을 바탕으로 건강 신호 생성

    한의학 이론:
    - 오운(五運): 장부(臟腑) 에너지 흐름
    - 육기(六氣): 외부 환경 기운 (기후/계절)
    → 두 요소의 조화/불균형으로 건강 상태 예측

    Returns:
        {
            "energy_balance": "조화" | "과잉" | "부족",
            "vulnerable_organs": ["간", "폐"],
            "favorable_foods": ["채소류", "견과류"],
            "caution_activities": ["과도한 운동", "야식"],
            "recommended_rest_times": ["오후 2-4시"],
        }
    """
    day_movement = five_movements["day_movement"]
    dominant_qi = six_qi["dominant_qi"]
    qi_phase = six_qi["qi_phase"]

    # 오운별 장부 매핑
    movement_to_organs = {
        "木運": ["간", "담"],
        "火運": ["심", "소장"],
        "土運": ["비", "위"],
        "金運": ["폐", "대장"],
        "水運": ["신", "방광"],
    }

    # 육기별 영향 매핑
    qi_to_effects = {
        "厥陰風木": {"nature": "바람", "caution": "외풍 주의", "season": "봄"},
        "少陰君火": {"nature": "군화", "caution": "과열 주의", "season": "초여름"},
        "少陽相火": {"nature": "상화", "caution": "염증 주의", "season": "한여름"},
        "太陰濕土": {"nature": "습기", "caution": "습기 제거", "season": "장마"},
        "陽明燥金": {"nature": "건조", "caution": "보습 필요", "season": "가을"},
        "太陽寒水": {"nature": "한기", "caution": "보온 필요", "season": "겨울"},
    }

    # 에너지 균형 평가
    energy_balance = "조화"  # 기본값
    if qi_phase == "상반기" and day_movement in ["火運", "木運"]:
        energy_balance = "과잉"
    elif qi_phase == "하반기" and day_movement in ["水運", "金運"]:
        energy_balance = "과잉"
    elif (qi_phase == "상반기" and day_movement == "水運") or \
         (qi_phase == "하반기" and day_movement == "火運"):
        energy_balance = "부족"

    # 취약 장부
    vulnerable_organs = movement_to_organs.get(day_movement, ["비", "위"])

    # 기운별 영향
    qi_effect = qi_to_effects.get(dominant_qi, {"nature": "중성", "caution": "균형 유지", "season": "사계절"})

    # 권장 음식 (오운 기반)
    favorable_foods = get_favorable_foods(day_movement, dominant_qi)

    # 주의할 활동
    caution_activities = [
        qi_effect["caution"],
        f"{vulnerable_organs[0]} 부담 활동 자제",
    ]

    # 권장 휴식 시간
    recommended_rest_times = get_rest_times_by_qi(dominant_qi)

    return {
        "energy_balance": energy_balance,
        "vulnerable_organs": vulnerable_organs,
        "favorable_foods": favorable_foods,
        "caution_activities": caution_activities,
        "recommended_rest_times": recommended_rest_times,
        "seasonal_nature": qi_effect["nature"],
        "season_context": qi_effect["season"],
    }


def get_favorable_foods(movement: str, qi: str) -> List[str]:
    """
    오운과 육기에 맞는 권장 음식 목록

    한의학 식이 원칙:
    - 오운에 맞춰 장부 보강
    - 육기에 맞춰 외부 환경 대응
    """
    movement_foods = {
        "木運": ["녹색 채소", "신맛 음식", "새싹류"],
        "火運": ["붉은 과일", "쓴맛 음식", "고구마"],
        "土運": ["곡물", "단맛 음식", "감자"],
        "金運": ["흰색 음식", "매운맛", "무", "도라지"],
        "水運": ["검은콩", "짠맛 음식", "해조류"],
    }

    qi_foods = {
        "厥陰風木": ["따뜻한 차", "생강"],
        "少陰君火": ["수분 보충", "오이"],
        "少陽相火": ["시원한 음식", "수박"],
        "太陰濕土": ["제습 음식", "율무"],
        "陽明燥金": ["보습 음식", "배", "꿀"],
        "太陽寒水": ["보온 음식", "인삼", "대추"],
    }

    foods = movement_foods.get(movement, ["균형 식단"])
    foods.extend(qi_foods.get(qi, []))

    return foods[:4]  # 최대 4개


def get_rest_times_by_qi(qi: str) -> List[str]:
    """
    육기별 권장 휴식 시간대
    """
    qi_to_rest = {
        "厥陰風木": ["오전 9-11시", "오후 3-5시"],
        "少陰君火": ["오후 1-3시 (낮잠)"],
        "少陽相火": ["정오 전후 휴식"],
        "太陰濕土": ["오후 2-4시"],
        "陽明燥金": ["오전 10-12시"],
        "太陽寒水": ["저녁 7-9시 (조기 수면)"],
    }

    return qi_to_rest.get(qi, ["오후 2-4시"])


# ==================== 분석 요약 ====================
def analyze_saekeunshik_summary(
    birth_year: int,
    target_date: date
) -> Dict[str, Any]:
    """
    색은식 종합 분석 요약

    Returns:
        {
            "date": "2026-01-31",
            "five_movements_summary": "목운 (木運) - 성장과 확장의 에너지",
            "six_qi_summary": "궐음풍목 (厥陰風木) - 봄 기운, 바람 주의",
            "health_advice": "간 건강 관리, 외풍 주의, 녹색 채소 섭취",
            "energy_balance": "조화"
        }
    """
    five_movements = calculate_five_movements(birth_year, target_date)
    six_qi = calculate_six_qi(birth_year, target_date)
    health_signals = generate_health_signals(five_movements, six_qi, target_date)

    # 요약 문구 생성
    movement_desc = {
        "木運": "목운 (木運) - 성장과 확장의 에너지",
        "火運": "화운 (火運) - 활동과 열정의 에너지",
        "土運": "토운 (土運) - 안정과 정리의 에너지",
        "金運": "금운 (金運) - 수확과 결단의 에너지",
        "水運": "수운 (水運) - 휴식과 지혜의 에너지",
    }

    qi_desc = {
        "厥陰風木": "궐음풍목 - 봄 기운, 바람 주의",
        "少陰君火": "소음군화 - 초여름 기운, 과열 주의",
        "少陽相火": "소양상화 - 한여름 기운, 염증 주의",
        "太陰濕土": "태음습토 - 장마 기운, 습기 제거",
        "陽明燥金": "양명조금 - 가을 기운, 보습 필요",
        "太陽寒水": "태양한수 - 겨울 기운, 보온 필요",
    }

    # 건강 조언 통합
    health_advice = f"{', '.join(health_signals['vulnerable_organs'])} 건강 관리, " \
                   f"{health_signals['seasonal_nature']} 대응, " \
                   f"{health_signals['favorable_foods'][0]} 등 섭취"

    return {
        "date": target_date.isoformat(),
        "five_movements_summary": movement_desc.get(five_movements["day_movement"], "조화의 에너지"),
        "six_qi_summary": qi_desc.get(six_qi["dominant_qi"], "균형 유지"),
        "health_advice": health_advice,
        "energy_balance": health_signals["energy_balance"],
        "detailed_data": {
            "five_movements": five_movements,
            "six_qi": six_qi,
            "health_signals": health_signals,
        }
    }
