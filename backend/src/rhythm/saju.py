"""
사주명리 계산 모듈

TypeScript로 작성된 사주 계산기를 Node.js subprocess로 실행하여 결과를 반환합니다.

내부 전문 용어 사용 가능:
- 천간(天干), 지지(地支), 오행(五行), 십성(十星)
- 대운(大運), 세운(歲運), 월운(月運), 일운(日運)
- 천을귀인, 역마, 공망 등

⚠️ 이 계산 결과는 사용자에게 직접 노출하지 않습니다!
Content Assembly Engine에서 일반 언어로 변환됩니다.
"""
import datetime
import json
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import date as date_type
from .models import BirthInfo, RhythmSignal

# 사주 원국 계산 캐시 (같은 출생 정보는 동일한 원국 반환)
_saju_cache: Dict[str, Any] = {}
_SAJU_CACHE_MAX = 200  # 최대 200개 사용자 캐시


def calculate_saju(birth_info: BirthInfo, target_date: datetime.date) -> Dict[str, Any]:
    """
    사주명리 계산 (Node.js subprocess 실행)

    Args:
        birth_info: 출생 정보
        target_date: 분석 대상 날짜

    Returns:
        사주명리 계산 결과 (내부 전문 용어 사용)

    Raises:
        RuntimeError: Node.js 실행 실패 또는 계산 오류
    """
    # Node.js CLI 경로 (saju-calculator 사용)
    current_dir = Path(__file__).parent.parent.parent  # backend/
    cli_path = current_dir / "saju-calculator" / "cli.js"

    if not cli_path.exists():
        raise RuntimeError(f"사주 계산기 CLI를 찾을 수 없습니다: {cli_path}")

    # 캐시 키: 출생 정보 기반 (target_date 제외 - 원국은 불변)
    cache_key = f"{birth_info.birth_date}_{birth_info.birth_time}_{birth_info.gender.value}_{birth_info.birth_place}"
    if cache_key in _saju_cache:
        cached_base = _saju_cache[cache_key]
        # 세운 정보만 target_date에 맞게 재매핑
        saju_data = dict(cached_base)
        target_year_sewoon = None
        if "원본데이터" in saju_data:
            raw = saju_data["원본데이터"]
            if raw.get("currentYearSewoon", {}).get("year") == target_date.year:
                target_year_sewoon = raw["currentYearSewoon"]
            elif raw.get("nextYearSewoon", {}).get("year") == target_date.year:
                target_year_sewoon = raw["nextYearSewoon"]
        saju_data["세운"] = target_year_sewoon
        return saju_data

    # 입력 데이터 준비
    input_data = {
        "year": birth_info.birth_date.year,
        "month": birth_info.birth_date.month,
        "day": birth_info.birth_date.day,
        "hour": birth_info.birth_time.hour,
        "minute": birth_info.birth_time.minute,
        "gender": birth_info.gender.value,
        "isLunar": False,  # 양력 기준
        "birthPlace": birth_info.birth_place or "서울",
    }

    try:
        # Node.js CLI 실행
        result = subprocess.run(
            ["node", str(cli_path)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            encoding='utf-8',  # UTF-8 인코딩 명시
            timeout=10,  # 10초 타임아웃
        )

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error"
            raise RuntimeError(f"사주 계산 실패: {error_msg}")

        # 결과 파싱
        saju_data = json.loads(result.stdout)

        # 대상 날짜의 일진 정보 추가 (세운 계산)
        target_year_sewoon = None
        if "currentYearSewoon" in saju_data:
            target_year = target_date.year
            current_year_sewoon = saju_data["currentYearSewoon"]
            if current_year_sewoon.get("year") == target_year:
                target_year_sewoon = current_year_sewoon
            elif saju_data.get("nextYearSewoon", {}).get("year") == target_year:
                target_year_sewoon = saju_data["nextYearSewoon"]

        # 결과 구조화
        result_data = {
            "사주": {
                "년주": {
                    "천간": saju_data["fourPillars"]["year"]["gan"],
                    "지지": saju_data["fourPillars"]["year"]["ji"],
                    "간지": saju_data["fourPillars"]["year"]["ganJi"],
                },
                "월주": {
                    "천간": saju_data["fourPillars"]["month"]["gan"],
                    "지지": saju_data["fourPillars"]["month"]["ji"],
                    "간지": saju_data["fourPillars"]["month"]["ganJi"],
                },
                "일주": {
                    "천간": saju_data["fourPillars"]["day"]["gan"],
                    "지지": saju_data["fourPillars"]["day"]["ji"],
                    "간지": saju_data["fourPillars"]["day"]["ganJi"],
                },
                "시주": {
                    "천간": saju_data["fourPillars"]["time"]["gan"],
                    "지지": saju_data["fourPillars"]["time"]["ji"],
                    "간지": saju_data["fourPillars"]["time"]["ganJi"],
                },
            },
            "오행": saju_data["ohHaeng"]["balance"],
            "십성": saju_data["sipSung"]["detail"],
            "격국": {
                "일간": saju_data["gyeokGuk"]["dayMaster"],
                "일간오행": saju_data["gyeokGuk"]["dayMasterOhHaeng"],
                "강약": saju_data["gyeokGuk"]["strength"],
                "계절": saju_data["gyeokGuk"]["season"],
            },
            "용신": {
                "용신": saju_data["yongSin"]["yongSin"],
                "기신": saju_data["yongSin"]["giSin"],
            },
            "대운": saju_data["daewoon"],
            "세운": target_year_sewoon,
            "신살": saju_data["sinsal"],
            "성격": saju_data["personality"],
            "원본데이터": saju_data,  # 전체 데이터 보존
        }

        # 캐시 저장 (LRU 방식: 최대 크기 초과 시 첫 항목 제거)
        if len(_saju_cache) >= _SAJU_CACHE_MAX:
            oldest_key = next(iter(_saju_cache))
            del _saju_cache[oldest_key]
        _saju_cache[cache_key] = dict(result_data)

        return result_data

    except subprocess.TimeoutExpired:
        raise RuntimeError("사주 계산 시간 초과 (10초)")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"사주 계산 결과 파싱 실패: {e}")
    except Exception as e:
        raise RuntimeError(f"사주 계산 중 오류 발생: {e}")


def analyze_daily_fortune(
    birth_info: BirthInfo,
    target_date: datetime.date,
    saju_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    일간 운세 분석 (내부 해석)

    사주명리 데이터를 기반으로 일간 리듬 신호를 생성합니다.

    Args:
        birth_info: 출생 정보
        target_date: 분석 날짜
        saju_data: 사주명리 계산 결과 (calculate_saju 반환값)

    Returns:
        일간 운세 해석 (내부 표현)
    """
    # 세운 데이터 (해당 년도의 운)
    sewoon = saju_data.get("세운")

    # 대운 데이터
    daewoon = saju_data.get("대운", {})
    current_daewoon = daewoon.get("current")

    # 용신/기신
    yongsin_data = saju_data.get("용신", {})
    yongsin_list = yongsin_data.get("용신", [])
    gisin_list = yongsin_data.get("기신", [])

    # 오행 균형
    ohhaeng = saju_data.get("오행", {})
    dominant_element = max(ohhaeng.items(), key=lambda x: x[1])[0] if ohhaeng else "목"

    # 격국 정보
    gyeokguk = saju_data.get("격국", {})
    strength = gyeokguk.get("강약", "중화")
    season = gyeokguk.get("계절", "봄")

    # 일진(日辰) 계산 - 60간지 순환으로 당일 천간/지지 계산
    _JIAZI_DATE = date_type(1900, 1, 31)  # 甲子日 기준점
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    STEM_WUXING = {"甲": 0, "乙": 0, "丙": 1, "丁": 1, "戊": 2, "己": 2, "庚": 3, "辛": 3, "壬": 4, "癸": 4}
    # 오행: 木=0, 火=1, 土=2, 金=3, 水=4
    # 상생: 木生火, 火生土, 土生金, 金生水, 水生木
    SHENG_MAP = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
    # 상극: 木克土, 火克金, 土克水, 金克木, 水克火
    KE_MAP = {0: 2, 1: 3, 2: 4, 3: 0, 4: 1}

    # 당일 일주(日柱) 천간 계산
    delta = (target_date - _JIAZI_DATE).days
    today_stem_idx = delta % 10
    today_branch_idx = delta % 12
    today_stem = HEAVENLY_STEMS[today_stem_idx]
    today_branch = EARTHLY_BRANCHES[today_branch_idx]

    # 사주 일간(日干)과 당일 천간의 오행 관계 분석
    dayjugan = saju_data.get("사주", {}).get("일주", {}).get("천간", "")
    day_relation = "bi"  # 기본값: 비화(比和)
    daily_adjustment = 0  # 날짜별 에너지 조정값

    if dayjugan and dayjugan in STEM_WUXING and today_stem in STEM_WUXING:
        wa = STEM_WUXING[dayjugan]
        wb = STEM_WUXING[today_stem]
        if wa == wb:
            day_relation = "bi"
            daily_adjustment = 0
        elif SHENG_MAP[wa] == wb:
            day_relation = "sheng_out"   # 내가 생함(食傷) → 에너지 소모
            daily_adjustment = -1
        elif SHENG_MAP[wb] == wa:
            day_relation = "sheng_in"    # 내가 생받음(印) → 에너지 충전
            daily_adjustment = +1
        elif KE_MAP[wa] == wb:
            day_relation = "ke_out"      # 내가 극함(財) → 활동적
            daily_adjustment = +1
        elif KE_MAP[wb] == wa:
            day_relation = "ke_in"       # 내가 극받음(官殺) → 긴장/주의
            daily_adjustment = -1

    # 당일 지지의 계절 오행 계산 (날짜별 추가 조정)
    BRANCH_SEASON = {
        "子": 4, "丑": 2,  # 水/土
        "寅": 0, "卯": 0,  # 木
        "辰": 2, "巳": 1,  # 土/火
        "午": 1, "未": 2,  # 火/土
        "申": 3, "酉": 3,  # 金
        "戌": 2, "亥": 4,  # 土/水
    }
    branch_element = BRANCH_SEASON.get(today_branch, 2)
    # 용신 오행과 일지(日支) 오행이 일치하면 추가 보정
    if branch_element in [STEM_WUXING.get(y_elem, -1) for y_elem in yongsin_list if y_elem in ["목","화","토","금","수"]]:
        daily_adjustment += 0  # 용신은 한자 오행으로 비교하므로 스킵 (추후 정교화)

    # 에너지 수준 계산 (원국 기반 + 일진 조정)
    base_energy = 3  # 기본값
    if sewoon and dominant_element in yongsin_list:
        base_energy = 4
    elif sewoon and dominant_element in gisin_list:
        base_energy = 2

    # 일진 관계로 최종 에너지 조정 (1-5 범위)
    energy_level = max(1, min(5, base_energy + daily_adjustment))

    # 집중력/사회운/결정력 계산 (십성 기반 + 일진 조정)
    sipsung = saju_data.get("십성", {})
    # 기본값은 십성에서
    concentration = 3 + (sipsung.get("식신", 0) + sipsung.get("상관", 0)) // 2
    social = 3 + (sipsung.get("정관", 0) + sipsung.get("편관", 0)) // 2
    decision = 3 + (sipsung.get("비견", 0) + sipsung.get("겁재", 0)) // 2

    # 일진 관계에 따른 세부 조정
    if day_relation == "sheng_in":  # 인성일: 집중력 +1
        concentration = min(5, concentration + 1)
    elif day_relation == "sheng_out":  # 식상일: 창의/사교 +1
        social = min(5, social + 1)
    elif day_relation == "ke_out":  # 재성일: 결정력 +1
        decision = min(5, decision + 1)
    elif day_relation == "ke_in":  # 관살일: 집중력 변동 (긴장)
        concentration = max(1, concentration - 1)

    # 1-5 범위로 제한
    concentration = min(5, max(1, concentration))
    social = min(5, max(1, social))
    decision = min(5, max(1, decision))

    # 일진 정보를 fortune_analysis에 저장 (시간/방향 계산에 활용)
    _daily_ganzhi_info = {
        "stem": today_stem,
        "branch": today_branch,
        "relation": day_relation,
        "adjustment": daily_adjustment,
    }

    fortune_analysis = {
        "에너지_수준": energy_level,
        "집중력": concentration,
        "사회운": social,
        "결정력": decision,
        "유리한_시간": get_favorable_times(saju_data, target_date),
        "주의_시간": get_caution_times(saju_data, target_date),
        "유리한_방향": get_favorable_directions(saju_data, target_date),
        "주요_흐름": f"{season}의 에너지, {strength} 상태",
        "기회_요소": [f"{element} 오행 활용" for element in yongsin_list],
        "도전_요소": [f"{element} 오행 주의" for element in gisin_list],
        "격국": gyeokguk,
        "세운점수": sewoon.get("score", 50) if sewoon else 50,
        "일진": {
            "천간": today_stem,
            "지지": today_branch,
            "관계": day_relation,
        },
    }

    return fortune_analysis


def get_favorable_times(saju_data: Dict[str, Any], target_date: datetime.date) -> list[str]:
    """
    유리한 시간대 계산 (천을귀인 기반 + 일진 시간대)
    """
    sinsal = saju_data.get("신살", {})

    # 당일 일진 계산으로 시간대 결정
    _JIAZI_DATE = datetime.date(1900, 1, 31)
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    # 12지지별 시간대 (한국 표준시)
    BRANCH_TIMES = {
        "子": "23-01시", "丑": "01-03시", "寅": "03-05시", "卯": "05-07시",
        "辰": "07-09시", "巳": "09-11시", "午": "11-13시", "未": "13-15시",
        "申": "15-17시", "酉": "17-19시", "戌": "19-21시", "亥": "21-23시",
    }
    delta = (target_date - _JIAZI_DATE).days
    today_branch = EARTHLY_BRANCHES[delta % 12]
    today_branch_time = BRANCH_TIMES.get(today_branch, "09-11시")

    # 천을귀인이 있으면 해당 시간대를 첫 번째로
    if sinsal.get("hasCheonEulGuiIn"):
        return [f"오전 9-11시 (사시)", f"오늘 {today_branch_time} ({today_branch}시)"]

    # 일진 지지 기반 시간대 + 기본 추천
    return [f"오늘 {today_branch_time} ({today_branch}시)", "오후 2-4시"]


def get_caution_times(saju_data: Dict[str, Any], target_date: datetime.date) -> list[str]:
    """
    주의 시간대 계산 (일진 기반)
    """
    sinsal = saju_data.get("신살", {})

    # 당일 일진의 반대 시간대(충하는 시간) 계산
    _JIAZI_DATE = datetime.date(1900, 1, 31)
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    # 충(冲): 子-午, 丑-未, 寅-申, 卯-酉, 辰-戌, 巳-亥
    CHUNG_MAP = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 0, 7: 1, 8: 2, 9: 3, 10: 4, 11: 5}
    BRANCH_TIMES = {
        "子": "23-01시", "丑": "01-03시", "寅": "03-05시", "卯": "05-07시",
        "辰": "07-09시", "巳": "09-11시", "午": "11-13시", "未": "13-15시",
        "申": "15-17시", "酉": "17-19시", "戌": "19-21시", "亥": "21-23시",
    }

    delta = (target_date - _JIAZI_DATE).days
    today_branch_idx = delta % 12
    chung_branch_idx = CHUNG_MAP[today_branch_idx]
    chung_branch = EARTHLY_BRANCHES[chung_branch_idx]
    chung_time = BRANCH_TIMES.get(chung_branch, "자정 전후")

    # 공망이 있으면 유시 추가
    if sinsal.get("hasGongMang"):
        return ["오후 5-7시 (유시)", f"오늘 {chung_time} ({chung_branch}시, 충 시간대)"]

    return [f"오늘 {chung_time} ({chung_branch}시, 충 시간대)"]


def get_favorable_directions(saju_data: Dict[str, Any], target_date: datetime.date) -> list[str]:
    """
    유리한 방향 계산 (용신 오행 기반)
    """
    yongsin_data = saju_data.get("용신", {})
    yongsin_list = yongsin_data.get("용신", [])

    # 오행별 방향 매핑
    element_directions = {
        "목": "동쪽",
        "화": "남쪽",
        "토": "중앙",
        "금": "서쪽",
        "수": "북쪽",
    }

    directions = [element_directions.get(elem, "동쪽") for elem in yongsin_list[:2]]
    return directions if directions else ["동쪽", "남쪽"]


def analyze_monthly_rhythm(
    birth_info: BirthInfo,
    year: int,
    month: int,
    saju_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    월간 리듬 분석 (내부 해석)

    Args:
        birth_info: 출생 정보
        year: 분석 대상 년도
        month: 분석 대상 월 (1-12)
        saju_data: 사주명리 계산 결과 (calculate_saju 반환값)

    Returns:
        월간 리듬 해석 (내부 표현)
    """
    import calendar

    # 월주 정보 (사주팔자에서 월주 추출)
    month_pillar = saju_data.get("사주", {}).get("월주", {})
    month_gan = month_pillar.get("천간", "")
    month_ji = month_pillar.get("지지", "")
    month_gan_element = month_pillar.get("천간오행", "목")  # 기본값

    # 용신/기신
    yongsin_data = saju_data.get("용신", {})
    yongsin_list = yongsin_data.get("용신", [])
    gisin_list = yongsin_data.get("기신", [])

    # 격국 정보
    gyeokguk = saju_data.get("격국", {})
    strength = gyeokguk.get("강약", "중화")
    season = gyeokguk.get("계절", "봄")

    # 월간 테마 결정 (월주 천간 오행 기반)
    element_themes = {
        "목": "성장과 확장",
        "화": "활동과 표현",
        "토": "안정과 정리",
        "금": "수확과 결단",
        "수": "휴식과 계획",
    }

    # 사주팔자의 월주가 아니라 실제 해당 월의 오행을 계산
    # 간단히 월별로 오행 매핑 (실제로는 절기 기준이지만 간소화)
    month_elements = {
        1: "수", 2: "수", 3: "목", 4: "목", 5: "화", 6: "화",
        7: "토", 8: "금", 9: "금", 10: "토", 11: "수", 12: "수"
    }
    current_month_element = month_elements.get(month, "목")
    main_theme = element_themes.get(current_month_element, "균형과 조화")

    # 우선순위 결정 (용신 기반)
    priorities = []
    if "목" in yongsin_list:
        priorities.append("새로운 시작과 학습")
    if "화" in yongsin_list:
        priorities.append("관계 확장과 소통")
    if "토" in yongsin_list:
        priorities.append("기반 다지기와 정리")
    if "금" in yongsin_list:
        priorities.append("결단과 실행")
    if "수" in yongsin_list:
        priorities.append("계획과 준비")

    # 우선순위가 3개 미만이면 기본값 추가
    default_priorities = ["일상 루틴 유지", "건강 관리", "관계 점검"]
    while len(priorities) < 3:
        for default in default_priorities:
            if default not in priorities:
                priorities.append(default)
                if len(priorities) >= 3:
                    break

    # 상위 3개만 선택
    priorities = priorities[:3]

    # 일별 에너지 수준 계산 (일진 기반)
    import datetime as _dt
    days_in_month = calendar.monthrange(year, month)[1]
    daily_energy = {}

    _JIAZI_DATE = _dt.date(1900, 1, 31)
    HEAVENLY_STEMS_WUXING = {
        "甲": 0, "乙": 0,  # 木
        "丙": 1, "丁": 1,  # 火
        "戊": 2, "己": 2,  # 土
        "庚": 3, "辛": 3,  # 金
        "壬": 4, "癸": 4,  # 水
    }
    ALL_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    SHENG_MAP = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}
    KE_MAP = {0: 2, 1: 3, 2: 4, 3: 0, 4: 1}

    # 일간(사주 일주 천간) 가져오기
    dayjugan = saju_data.get("사주", {}).get("일주", {}).get("천간", "")

    for day in range(1, days_in_month + 1):
        target_day = _dt.date(year, month, day)
        delta = (target_day - _JIAZI_DATE).days
        today_stem = ALL_STEMS[delta % 10]

        # 일간과 당일 천간의 오행 관계로 에너지 결정
        base_energy = 3
        if dayjugan in HEAVENLY_STEMS_WUXING and today_stem in HEAVENLY_STEMS_WUXING:
            wa = HEAVENLY_STEMS_WUXING[dayjugan]
            wb = HEAVENLY_STEMS_WUXING[today_stem]
            if SHENG_MAP[wb] == wa:      # 오늘이 나를 생함 (인성) → 에너지 +1
                base_energy = 4
            elif KE_MAP[wb] == wa:       # 오늘이 나를 극함 (관살) → 에너지 -1
                base_energy = 2
            elif SHENG_MAP[wa] == wb:    # 내가 오늘을 생함 (식상) → 보통
                base_energy = 3
            elif KE_MAP[wa] == wb:       # 내가 오늘을 극함 (재성) → 약간 활동적
                base_energy = 4
        # 용신 오행과 당일 오행이 일치하면 추가 보정
        if today_stem in HEAVENLY_STEMS_WUXING:
            wb = HEAVENLY_STEMS_WUXING[today_stem]
            # 용신 오행 인덱스 (한국어 → 숫자)
            yongsin_wuxing = {"목": 0, "화": 1, "토": 2, "금": 3, "수": 4}
            for yong in yongsin_list:
                if yongsin_wuxing.get(yong) == wb:
                    base_energy = min(5, base_energy + 1)
                    break
            for gi in gisin_list:
                if yongsin_wuxing.get(gi) == wb:
                    base_energy = max(1, base_energy - 1)
                    break

        daily_energy[day] = base_energy

    # 기회/도전 요소
    opportunities = [f"{elem} 오행 활용" for elem in yongsin_list] or ["루틴 최적화"]
    challenges = [f"{elem} 오행 주의" for elem in gisin_list] or ["과도한 활동 자제"]

    monthly_analysis = {
        "년월": f"{year}년 {month}월",
        "주제": main_theme,
        "우선순위": priorities,
        "일별_에너지": daily_energy,
        "기회_요소": opportunities,
        "도전_요소": challenges,
        "월주_정보": {
            "천간": month_gan,
            "지지": month_ji,
            "간지": f"{month_gan}{month_ji}",
        },
        "전체_흐름": f"{season}의 {main_theme} 시기",
    }

    return monthly_analysis


def analyze_yearly_rhythm(
    birth_info: BirthInfo,
    year: int,
    saju_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    연간 리듬 분석 (내부 해석)

    Args:
        birth_info: 출생 정보
        year: 분석 대상 년도
        saju_data: 사주명리 계산 결과 (calculate_saju 반환값)

    Returns:
        연간 리듬 해석 (내부 표현)
    """
    # 년주 정보
    year_pillar = saju_data.get("사주", {}).get("년주", {})

    # 대운 정보
    daewoon = saju_data.get("대운", {})
    current_daewoon = daewoon.get("current")

    # 세운 정보
    sewoon = saju_data.get("세운")

    # 용신/기신
    yongsin_data = saju_data.get("용신", {})
    yongsin_list = yongsin_data.get("용신", [])
    gisin_list = yongsin_data.get("기신", [])

    # 격국
    gyeokguk = saju_data.get("격국", {})

    # 연간 테마 (대운 + 세운 조합)
    yearly_theme = "안정과 성장의 해"
    if current_daewoon:
        daewoon_gan = current_daewoon.get("gan", "")
        yearly_theme = f"{daewoon_gan} 대운 - 변화와 성장의 시기"

    # 월별 간단한 신호 (12개월)
    monthly_signals = {}
    month_themes = {
        1: "새해 계획", 2: "기반 다지기", 3: "활동 시작",
        4: "성장 가속", 5: "관계 확장", 6: "성과 점검",
        7: "재정비", 8: "실행력", 9: "수확 준비",
        10: "정리와 마무리", 11: "성찰", 12: "다음 준비"
    }

    # 용신/기신 오행 인덱스 매핑
    _yongsin_wuxing = {"목": 0, "화": 1, "토": 2, "금": 3, "수": 4}
    # 월별 주도 오행 (절기 기준 간소화)
    _month_wuxing = {
        1: 4, 2: 4,   # 수(Water) - 겨울
        3: 0, 4: 0,   # 목(Wood) - 봄
        5: 1, 6: 1,   # 화(Fire) - 여름
        7: 2, 8: 3,   # 토(Earth)/금(Metal) - 환절기/가을
        9: 3, 10: 2,  # 금(Metal)/토(Earth) - 가을/환절기
        11: 4, 12: 4, # 수(Water) - 겨울
    }

    for month in range(1, 13):
        month_wx = _month_wuxing.get(month, 2)
        base_score = 3

        # 용신 오행과 월 오행이 일치하면 +1
        for yong in yongsin_list:
            if _yongsin_wuxing.get(yong) == month_wx:
                base_score = min(5, base_score + 1)
                break
        # 기신 오행과 월 오행이 일치하면 -1
        for gi in gisin_list:
            if _yongsin_wuxing.get(gi) == month_wx:
                base_score = max(1, base_score - 1)
                break

        monthly_signals[month] = {
            "월": month,
            "테마": month_themes.get(month, "균형"),
            "에너지": base_score,
        }

    yearly_analysis = {
        "년도": year,
        "주제": yearly_theme,
        "대운_정보": current_daewoon,
        "세운_정보": sewoon,
        "월별_신호": monthly_signals,
        "용신": yongsin_list,
        "기신": gisin_list,
        "전체_흐름": f"{year}년은 {yearly_theme}",
        "핵심_과제": ["대운에 맞춘 성장", "세운 활용", "용신 오행 강화"],
    }

    return yearly_analysis
