"""
기문둔갑(奇門遁甲) 리듬 분석 모듈
내부 계산 전용 - 사용자에게 직접 노출 금지

8문(八門), 9궁(九宮), 일주(日柱) 기반 시간대별 길흉 산출
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple
from datetime import date


# ---------------------------------------------------------------------------
# 데이터클래스
# ---------------------------------------------------------------------------

@dataclass
class HourlyQimenResult:
    hour_start: int   # 시작 시각 (0-23)
    hour_end: int     # 종료 시각 (2-25, 자시는 23→1로 표기)
    quality: str      # "good" | "neutral" | "avoid"
    direction: str    # 한국어 방위
    direction_en: str # 영문 코드
    energy_level: int # 1-10
    label: str        # 사용자 노출 라벨 (전문용어 금지)


# ---------------------------------------------------------------------------
# 상수: 12지지 시간 슬롯
# (자시는 전날 23시~당일 1시이므로 hour_end=1 로 특수 처리)
# ---------------------------------------------------------------------------

# (지지명, hour_start, hour_end)
TWELVE_BRANCHES: List[Tuple[str, int, int]] = [
    ("자", 23, 1),   # 子時 23:00 ~ 01:00
    ("축", 1,  3),   # 丑時
    ("인", 3,  5),   # 寅時
    ("묘", 5,  7),   # 卯時
    ("진", 7,  9),   # 辰時
    ("사", 9,  11),  # 巳時
    ("오", 11, 13),  # 午時
    ("미", 13, 15),  # 未時
    ("신", 15, 17),  # 申時
    ("유", 17, 19),  # 酉時
    ("술", 19, 21),  # 戌時
    ("해", 21, 23),  # 亥時
]

# ---------------------------------------------------------------------------
# 상수: 8문(八門)
# ---------------------------------------------------------------------------

# (문 이름, quality, 사용자 라벨)
EIGHT_GATES: List[Tuple[str, str, str]] = [
    ("휴문",  "good",    "집중하기 좋은 시간"),
    ("생문",  "good",    "에너지가 충만한 시간"),
    ("상문",  "avoid",   "에너지가 낮은 시간"),
    ("두문",  "neutral", "내면 정리 시간"),
    ("경문",  "neutral", "창의적 활동에 적합한 시간"),
    ("사문",  "avoid",   "휴식이 필요한 시간"),
    ("경문2", "avoid",   "중요한 결정을 피해야 할 시간"),  # 驚門 (경문/惊門)
    ("개문",  "good",    "새로운 시작에 좋은 시간"),
]

# 각 문의 에너지 기준치
GATE_BASE_ENERGY: Dict[str, int] = {
    "휴문":  8,
    "생문":  9,
    "상문":  2,
    "두문":  5,
    "경문":  5,
    "사문":  2,
    "경문2": 3,
    "개문":  8,
}

# ---------------------------------------------------------------------------
# 상수: 9궁(九宮) 방위
# 1궁=坎(북), 2궁=坤(남서), 3궁=震(동), 4궁=巽(남동),
# 5궁=中央, 6궁=乾(북서), 7궁=兌(서), 8궁=艮(북동), 9궁=離(남)
# ---------------------------------------------------------------------------

PALACE_DIRECTIONS: Dict[int, Tuple[str, str]] = {
    1: ("북",   "N"),
    2: ("남서", "SW"),
    3: ("동",   "E"),
    4: ("남동", "SE"),
    5: ("중앙", "C"),
    6: ("북서", "NW"),
    7: ("서",   "W"),
    8: ("북동", "NE"),
    9: ("남",   "S"),
}

# ---------------------------------------------------------------------------
# 상수: 천간(天干), 지지(地支), 오행(五行)
# ---------------------------------------------------------------------------

HEAVENLY_STEMS: List[str] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES: List[str] = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 천간 → 오행 인덱스 (木=0, 火=1, 土=2, 金=3, 水=4)
STEM_WUXING: Dict[str, int] = {
    "甲": 0, "乙": 0,  # 木
    "丙": 1, "丁": 1,  # 火
    "戊": 2, "己": 2,  # 土
    "庚": 3, "辛": 3,  # 金
    "壬": 4, "癸": 4,  # 水
}

# 상생표: SHENG[a][b] == True  →  a가 b를 생(生)함
# 木生火, 火生土, 土生金, 金生水, 水生木
_SHENG_MAP: Dict[int, int] = {0: 1, 1: 2, 2: 3, 3: 4, 4: 0}

# 상극표: KE[a][b] == True  →  a가 b를 극(克)함
# 木克土, 土克水, 水克火, 火克金, 金克木
_KE_MAP: Dict[int, int] = {0: 2, 1: 3, 2: 4, 3: 0, 4: 1}

# 기준일: 1900-01-31 = 甲子日 (60갑자 기준점)
_JIAZI_DATE = date(1900, 1, 31)


# ---------------------------------------------------------------------------
# 내부 유틸리티 함수
# ---------------------------------------------------------------------------

def _get_day_ganzhi(target_date: date) -> Tuple[str, str]:
    """날짜 → (천간, 지지) 일주 반환 (60간지 순환)"""
    delta = (target_date - _JIAZI_DATE).days
    idx = delta % 60
    stem_idx = idx % 10
    branch_idx = idx % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _wuxing_relation(stem_a: str, stem_b: str) -> str:
    """
    두 천간의 오행 관계 반환
    "sheng" (생/生), "ke" (극/克), "bi" (비화/比和)
    """
    wa = STEM_WUXING[stem_a]
    wb = STEM_WUXING[stem_b]
    if wa == wb:
        return "bi"
    if _SHENG_MAP[wa] == wb or _SHENG_MAP[wb] == wa:
        return "sheng"
    if _KE_MAP[wa] == wb or _KE_MAP[wb] == wa:
        return "ke"
    return "bi"


def _determine_ju(target_date: date, day_offset: int) -> tuple:
    """
    旬(sun)과 局(ju) 번호를 결정하고, 양둔/음둔 여부를 반환한다.

    양둔(陽遁): 동지(冬至)~하지(夏至) 사이, 대략 11월~5월
    음둔(陰遁): 하지(夏至)~동지(冬至) 사이, 대략 6월~10월

    Args:
        target_date: 분석 대상 날짜
        day_offset:  60갑자 순환 내 날짜 인덱스 (0-59)

    Returns:
        (ju_number: int 1-9, is_yang_dun: bool)
    """
    # 양둔/음둔 판별 (절기 기반 간략화: 월별 판별)
    # 양둔: 11, 12, 1, 2, 3, 4, 5월 (동지 전후 ~ 하지 전)
    # 음둔: 6, 7, 8, 9, 10월
    is_yang_dun = target_date.month in (11, 12, 1, 2, 3, 4, 5)

    # 旬 인덱스: 60갑자 내 10일 단위 (0-5)
    sun_index = day_offset // 10

    # 局 번호 결정
    # 양둔: 1→2→3→4→5→6→7→8→9 순환 (旬별로 다른 시작점)
    # 음둔: 9→8→7→6→5→4→3→2→1 역순환
    YANG_DUN_JU = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    YIN_DUN_JU  = [9, 8, 7, 6, 5, 4, 3, 2, 1, 9, 8, 7, 6, 5, 4, 3, 2, 1]

    sun_in_cycle = sun_index % 18
    ju_number = YANG_DUN_JU[sun_in_cycle] if is_yang_dun else YIN_DUN_JU[sun_in_cycle]

    return ju_number, is_yang_dun


def _gate_for_hour_slot(
    slot_index: int,
    ju_number: int,
    is_yang_dun: bool,
) -> int:
    """
    旬/局 기반 8문(八門) 인덱스 결정.

    局 번호를 시작 오프셋으로 사용하여 양둔은 순방향, 음둔은 역방향으로
    8문을 배치한다.

    Args:
        slot_index:  시간 슬롯 인덱스 (0-11, 자시~해시)
        ju_number:   局 번호 (1-9)
        is_yang_dun: 양둔 여부 (True=양둔, False=음둔)

    Returns:
        8문 인덱스 (0-7)
    """
    gate_base = (ju_number - 1) * 2  # 局에 따른 시작 위치
    if is_yang_dun:
        return (gate_base + slot_index) % 8
    else:
        return (gate_base + (11 - slot_index)) % 8


def _palace_for_hour_slot(
    slot_index: int,
    ju_number: int,
    is_yang_dun: bool,
) -> int:
    """
    旬/局 기반 9궁(九宮) 번호 결정 (1~9).

    양둔: ju_number를 시작으로 순방향 회전 (1→2→3→...→9→1)
    음둔: ju_number를 시작으로 역방향 회전 (9→8→7→...→1→9)

    Args:
        slot_index:  시간 슬롯 인덱스 (0-11, 자시~해시)
        ju_number:   局 번호 (1-9)
        is_yang_dun: 양둔 여부 (True=양둔, False=음둔)

    Returns:
        궁 번호 (1-9)
    """
    if is_yang_dun:
        return ((ju_number - 1 + slot_index) % 9) + 1
    else:
        return ((9 - ju_number + (8 - slot_index)) % 9) + 1


# ---------------------------------------------------------------------------
# 공개 함수
# ---------------------------------------------------------------------------

def calculate_daily_qimen(birth_date: date, target_date: date) -> List[HourlyQimenResult]:
    """
    날짜 기반 기문둔갑 시간대별 길흉 계산

    Args:
        birth_date:  출생일 (사주 일주 계산용)
        target_date: 분석 대상 날짜

    Returns:
        12개의 HourlyQimenResult 리스트 (자시~해시 순)
    """
    # 1) 날짜 오프셋 (60간지 순환의 날짜 인덱스)
    target_offset = (target_date - _JIAZI_DATE).days % 60

    # 2) 旬/局 기반 양둔/음둔 판별 및 局 번호 결정
    ju_number, is_yang_dun = _determine_ju(target_date, target_offset)

    # 3) 출생일 & 당일 천간 → 오행 관계 → 에너지 보정값
    birth_stem, _ = _get_day_ganzhi(birth_date)
    today_stem, _ = _get_day_ganzhi(target_date)
    relation = _wuxing_relation(birth_stem, today_stem)
    energy_bonus = {"sheng": 2, "ke": -2, "bi": 0}[relation]

    results: List[HourlyQimenResult] = []

    for slot_idx, (branch_name, h_start, h_end) in enumerate(TWELVE_BRANCHES):
        # 4) 해당 슬롯의 8문 결정 (旬/局 기반)
        gate_idx = _gate_for_hour_slot(slot_idx, ju_number, is_yang_dun)
        gate_name, quality, label = EIGHT_GATES[gate_idx]

        # 5) 9궁 방위 결정 (旬/局 기반)
        palace_no = _palace_for_hour_slot(slot_idx, ju_number, is_yang_dun)
        direction_ko, direction_en = PALACE_DIRECTIONS[palace_no]

        # 6) 에너지 레벨 계산 (1~10 범위 클램프)
        base_energy = GATE_BASE_ENERGY[gate_name]
        energy = max(1, min(10, base_energy + energy_bonus))

        results.append(HourlyQimenResult(
            hour_start=h_start,
            hour_end=h_end,
            quality=quality,
            direction=direction_ko,
            direction_en=direction_en,
            energy_level=energy,
            label=label,
        ))

    return results


def get_daily_summary(birth_date: date, target_date: date) -> Dict[str, str]:
    """
    하루 요약: 최고 방위, 피할 방위, 최고 시간대 반환

    Returns:
        {
            "best_direction":  "북동",
            "avoid_direction": "남서",
            "peak_hours":      "09-11시",
        }
    """
    hourly = calculate_daily_qimen(birth_date, target_date)

    # 에너지 최고 슬롯
    best = max(hourly, key=lambda r: r.energy_level)
    # 에너지 최저 슬롯
    worst = min(hourly, key=lambda r: r.energy_level)

    def _fmt_hours(r: HourlyQimenResult) -> str:
        end = r.hour_end if r.hour_end != 1 else 1
        return f"{r.hour_start:02d}-{end:02d}시"

    return {
        "best_direction":  best.direction,
        "avoid_direction": worst.direction,
        "peak_hours":      _fmt_hours(best),
    }


# ---------------------------------------------------------------------------
# 간단한 자가 테스트
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_birth = date(1971, 11, 17)
    test_target = date(2026, 2, 19)

    results = calculate_daily_qimen(test_birth, test_target)
    print("시간대별 기문 분석 결과")
    print("-" * 65)
    for r in results:
        end_str = f"{r.hour_end:02d}" if r.hour_end != 1 else "01"
        print(
            f"{r.hour_start:02d}:00-{end_str}:00 | "
            f"{r.quality:7} | {r.direction:3} ({r.direction_en:2}) | "
            f"에너지 {r.energy_level:2d} | {r.label}"
        )

    summary = get_daily_summary(test_birth, test_target)
    print()
    print(f"최고 방위  : {summary['best_direction']}")
    print(f"피할 방위  : {summary['avoid_direction']}")
    print(f"집중 시간대: {summary['peak_hours']}")
