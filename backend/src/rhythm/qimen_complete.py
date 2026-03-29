"""
기문둔갑(奇門遁甲) 완전 구현 모듈
내부 계산 전용 - 사용자에게 직접 노출 금지

8문(八門), 9궁(九宮), 9성(九星), 8신(八神) 완전 계산
천반(天盤), 지반(地盤), 인반(人盤), 신반(神盤) 4층 구조
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from datetime import date, datetime
import math


# ---------------------------------------------------------------------------
# 데이터클래스
# ---------------------------------------------------------------------------

@dataclass
class QimenPalace:
    """기문둔갑 궁(宮) 정보"""
    palace_num: int         # 궁 번호 (1-9)
    direction_ko: str       # 한국어 방위
    direction_en: str       # 영문 코드
    gate: str              # 8문 (휴문, 생문 등)
    star: str              # 9성 (천봉, 천임 등) 
    deity: str             # 8신 (직부, 등사 등)
    earthly_plate_gan: str # 지반 천간
    heavenly_plate_gan: str # 천반 천간
    quality_score: int     # 종합 길흉 점수 (0-100)


@dataclass
class CompleteQimenResult:
    """완전한 기문둔갑 분석 결과"""
    hour_start: int        # 시작 시각 (0-23)
    hour_end: int         # 종료 시각
    hour_branch: str      # 시지 (子丑寅卯...)
    palaces: List[QimenPalace]  # 9개 궁 정보
    best_palace: QimenPalace    # 최적 궁
    avoid_palace: QimenPalace   # 회피 궁
    overall_quality: str  # "excellent", "good", "neutral", "bad"
    user_guidance: str    # 사용자 가이드 문구


# ---------------------------------------------------------------------------
# 상수: 기문둔갑 기본 구성 요소
# ---------------------------------------------------------------------------

# 9궁 방위 (낙서 배치)
LUOSHU_PALACE = {
    1: {"pos": (0, -1), "dir_ko": "북", "dir_en": "N", "element": "水"},
    2: {"pos": (-1, -1), "dir_ko": "남서", "dir_en": "SW", "element": "土"},
    3: {"pos": (1, 0), "dir_ko": "동", "dir_en": "E", "element": "木"},
    4: {"pos": (1, -1), "dir_ko": "남동", "dir_en": "SE", "element": "木"},
    5: {"pos": (0, 0), "dir_ko": "중앙", "dir_en": "C", "element": "土"},
    6: {"pos": (-1, 1), "dir_ko": "북서", "dir_en": "NW", "element": "金"},
    7: {"pos": (-1, 0), "dir_ko": "서", "dir_en": "W", "element": "金"},
    8: {"pos": (1, 1), "dir_ko": "북동", "dir_en": "NE", "element": "土"},
    9: {"pos": (0, 1), "dir_ko": "남", "dir_en": "S", "element": "火"},
}

# 8문(八門) - 문 이름과 길흉
EIGHT_GATES = {
    "휴문": {"quality": 90, "element": "水", "label": "휴식과 회복의 문"},
    "생문": {"quality": 95, "element": "土", "label": "생기와 발전의 문"},
    "상문": {"quality": 30, "element": "金", "label": "상처와 손실의 문"},
    "두문": {"quality": 50, "element": "木", "label": "은둔과 숨김의 문"},
    "경문": {"quality": 70, "element": "金", "label": "경치와 학문의 문"},
    "사문": {"quality": 20, "element": "土", "label": "죽음과 종말의 문"},
    "경문2": {"quality": 25, "element": "火", "label": "놀람과 변화의 문"},  # 驚門
    "개문": {"quality": 85, "element": "金", "label": "시작과 개척의 문"},
}

# 9성(九星) - 북두구성
NINE_STARS = {
    "천봉": {"quality": 95, "element": "土", "label": "리더십의 별"},
    "천임": {"quality": 90, "element": "土", "label": "책임과 신뢰의 별"},
    "천충": {"quality": 40, "element": "木", "label": "충돌과 도전의 별"},
    "천보": {"quality": 80, "element": "木", "label": "도움과 보조의 별"},
    "천심": {"quality": 85, "element": "金", "label": "지혜와 통찰의 별"},
    "천주": {"quality": 60, "element": "金", "label": "기둥과 지지의 별"},
    "천예": {"quality": 30, "element": "火", "label": "날카로운 비판의 별"},
    "천영": {"quality": 75, "element": "火", "label": "명예와 영광의 별"},
    "천임2": {"quality": 70, "element": "水", "label": "유연한 적응의 별"},  # 천르이
}

# 8신(八神) - 양둔과 음둔
EIGHT_DEITIES_YANG = ["직부", "등사", "태음", "육합", "백호", "현무", "구지", "구천"]
EIGHT_DEITIES_YIN = ["직부", "등사", "태음", "육합", "구천", "구지", "현무", "백호"]

DEITY_QUALITIES = {
    "직부": 95,  # 직부(直符) - 주신, 최고 길신
    "등사": 35,  # 등사(騰蛇) - 변화와 속임
    "태음": 80,  # 태음(太陰) - 은밀과 비밀
    "육합": 85,  # 육합(六合) - 화합과 인연
    "백호": 25,  # 백호(白虎) - 살기와 투쟁  
    "현무": 40,  # 현무(玄武) - 도둑과 손실
    "구지": 50,  # 구지(九地) - 안정과 정착
    "구천": 70,  # 구천(九天) - 상승과 발전
}

# 10천간
HEAVENLY_STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
HIDDEN_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 12지지
EARTHLY_BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

# 천간 오행
STEM_ELEMENT = {
    "갑": "木", "을": "木", "병": "火", "정": "火", "무": "土",
    "기": "土", "경": "金", "신": "金", "임": "水", "계": "水",
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

# 지지 오행
BRANCH_ELEMENT = {
    "자": "水", "축": "土", "인": "木", "묘": "木", "진": "土", "사": "火",
    "오": "火", "미": "土", "신": "金", "유": "金", "술": "土", "해": "水",
}

# 60갑자 기준일
JIAZI_DATE = date(1900, 1, 31)

# 24절기 (대략적인 날짜, 실제는 천문계산 필요)
SOLAR_TERMS = {
    "동지": (12, 22), "소한": (1, 5), "대한": (1, 20), "입춘": (2, 4),
    "우수": (2, 19), "경칩": (3, 6), "춘분": (3, 21), "청명": (4, 5),
    "곡우": (4, 20), "입하": (5, 6), "소만": (5, 21), "망종": (6, 6),
    "하지": (6, 21), "소서": (7, 7), "대서": (7, 23), "입추": (8, 8),
    "처서": (8, 23), "백로": (9, 8), "추분": (9, 23), "한로": (10, 8),
    "상강": (10, 23), "입동": (11, 7), "소설": (11, 22), "대설": (12, 7),
}


# ---------------------------------------------------------------------------
# 내부 계산 함수
# ---------------------------------------------------------------------------

def _get_day_stem_branch(target_date: date) -> Tuple[str, str]:
    """날짜의 일간지 반환"""
    days_from_jiazi = (target_date - JIAZI_DATE).days
    stem_idx = days_from_jiazi % 10
    branch_idx = days_from_jiazi % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _get_hour_stem_branch(day_stem: str, hour: int) -> Tuple[str, str]:
    """시간의 시간지 반환"""
    # 시지 결정
    hour_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
    branch_idx = (hour + 1) // 2 % 12
    hour_branch = hour_branches[branch_idx]
    
    # 일간에 따른 시간 결정 (五鼠遁)
    day_stem_idx = HEAVENLY_STEMS.index(day_stem)
    hour_stem_start = {
        0: 0,  # 갑일 → 갑자시부터
        1: 2,  # 을일 → 병자시부터
        2: 4,  # 병일 → 무자시부터
        3: 6,  # 정일 → 경자시부터
        4: 8,  # 무일 → 임자시부터
        5: 0,  # 기일 → 갑자시부터
        6: 2,  # 경일 → 병자시부터
        7: 4,  # 신일 → 무자시부터
        8: 6,  # 임일 → 경자시부터
        9: 8,  # 계일 → 임자시부터
    }
    
    stem_idx = (hour_stem_start[day_stem_idx % 5 * 2] + branch_idx) % 10
    hour_stem = HEAVENLY_STEMS[stem_idx]
    
    return hour_stem, hour_branch


def _determine_yang_yin_dun(target_date: date) -> bool:
    """양둔/음둔 결정 (절기 기반)"""
    # 간단한 월별 판정 (실제는 절기 정밀 계산 필요)
    # 동지(12/22) ~ 하지(6/21): 양둔
    # 하지(6/21) ~ 동지(12/22): 음둔
    month = target_date.month
    day = target_date.day
    
    if month == 12 and day >= 22:
        return True  # 양둔 시작
    elif month in [1, 2, 3, 4, 5]:
        return True  # 양둔
    elif month == 6 and day < 21:
        return True  # 양둔
    else:
        return False  # 음둔


def _calculate_ju_number(day_stem: str, day_branch: str, is_yang_dun: bool, target_date: date = None) -> int:
    """局數 계산 (1-9)"""
    # 60갑자를 6개 旬으로 분리 (갑자순, 갑술순, 갑신순, 갑오순, 갑진순, 갑인순)
    stems = HEAVENLY_STEMS
    branches = EARTHLY_BRANCHES
    
    stem_idx = stems.index(day_stem)
    branch_idx = branches.index(day_branch)
    
    # 旬首 계산 (해당 순의 시작 갑자)
    sun_head_idx = (branch_idx - stem_idx) % 12
    sun_heads = ["자", "술", "신", "오", "진", "인"]
    sun_index = sun_heads.index(branches[sun_head_idx]) if branches[sun_head_idx] in sun_heads else 0
    
    # 상원/중원/하원 결정 (절기 기반, 여기서는 간략화)
    # 각 절기마다 상/중/하 3원이 있고, 각 원마다 다른 局을 사용
    # 여기서는 날짜 기반으로 단순 계산
    if target_date:
        day_in_month = target_date.day
        yuan = (day_in_month - 1) // 5 % 3  # 상원(0), 중원(1), 하원(2)
    else:
        yuan = 0  # 기본값
    
    # 양둔: 1,7,4 / 2,8,5 / 3,9,6 / 4,1,7 / 5,2,8 / 6,3,9
    # 음둔: 9,3,6 / 8,2,5 / 7,1,4 / 6,9,3 / 5,8,2 / 4,7,1
    yang_ju_table = [
        [1, 7, 4], [2, 8, 5], [3, 9, 6],
        [4, 1, 7], [5, 2, 8], [6, 3, 9]
    ]
    yin_ju_table = [
        [9, 3, 6], [8, 2, 5], [7, 1, 4],
        [6, 9, 3], [5, 8, 2], [4, 7, 1]
    ]
    
    if is_yang_dun:
        return yang_ju_table[sun_index][yuan]
    else:
        return yin_ju_table[sun_index][yuan]


def _rotate_palaces(ju_number: int, is_yang_dun: bool) -> Dict[int, int]:
    """局에 따른 궁 회전 매핑"""
    # 중궁이 ju_number가 되도록 낙서를 회전
    # 양둔: 시계방향, 음둔: 반시계방향
    base_luoshu = [4, 9, 2, 3, 5, 7, 8, 1, 6]  # 낙서 기본 배치
    
    # ju_number가 5궁(중궁)에 오도록 이동
    shift = (ju_number - 5) % 9
    
    if is_yang_dun:
        # 시계방향 회전
        rotated = base_luoshu[-shift:] + base_luoshu[:-shift] if shift else base_luoshu
    else:
        # 반시계방향 회전
        rotated = base_luoshu[shift:] + base_luoshu[:shift] if shift else base_luoshu
    
    # 궁 번호 → 회전된 궁 번호 매핑
    mapping = {}
    for i, val in enumerate(rotated):
        mapping[i + 1] = val
    
    return mapping


def _arrange_gates(ju_number: int, is_yang_dun: bool) -> Dict[int, str]:
    """8문 배치"""
    gates = ["휴문", "생문", "상문", "두문", "경문", "사문", "경문2", "개문"]
    
    # 휴문이 1궁(坎)부터 시작
    # 양둔: 시계방향, 음둔: 반시계방향
    palace_order_yang = [1, 8, 3, 4, 9, 2, 7, 6]  # 시계방향
    palace_order_yin = [1, 6, 7, 2, 9, 4, 3, 8]   # 반시계방향
    
    palace_order = palace_order_yang if is_yang_dun else palace_order_yin
    
    # ju_number에 따른 시작점 조정
    start_idx = (ju_number - 1) % 8
    gates_rotated = gates[start_idx:] + gates[:start_idx]
    
    gate_map = {}
    for i, palace in enumerate(palace_order):
        gate_map[palace] = gates_rotated[i]
    
    # 5궁(중궁)은 寄門 없음 (2궁의 문을 사용)
    gate_map[5] = gate_map[2]
    
    return gate_map


def _arrange_stars(hour_stem: str, is_yang_dun: bool) -> Dict[int, str]:
    """9성 배치"""
    stars = ["천봉", "천임", "천충", "천보", "천심", "천주", "천예", "천영", "천임2"]
    
    # 시간 천간에 따른 천봉성 위치
    stem_to_palace = {
        "갑": 1, "을": 2, "병": 3, "정": 4, "무": 5,
        "기": 6, "경": 7, "신": 8, "임": 9, "계": 1
    }
    
    tianpeng_palace = stem_to_palace.get(hour_stem, 1)
    
    # 천봉성부터 순서대로 배치
    palace_order = list(range(1, 10))
    start_idx = palace_order.index(tianpeng_palace)
    palaces_rotated = palace_order[start_idx:] + palace_order[:start_idx]
    
    star_map = {}
    for i, palace in enumerate(palaces_rotated):
        star_map[palace] = stars[i]
    
    return star_map


def _arrange_deities(hour_branch: str, is_yang_dun: bool) -> Dict[int, str]:
    """8신 배치"""
    deities = EIGHT_DEITIES_YANG if is_yang_dun else EIGHT_DEITIES_YIN
    
    # 시지에 따른 직부 위치
    branch_to_palace = {
        "자": 1, "축": 8, "인": 3, "묘": 3, "진": 4, "사": 9,
        "오": 9, "미": 2, "신": 7, "유": 7, "술": 6, "해": 1
    }
    
    zhifu_palace = branch_to_palace.get(hour_branch, 1)
    
    # 직부부터 순서대로 배치
    palace_order_yang = [1, 8, 3, 4, 9, 2, 7, 6]
    palace_order_yin = [1, 6, 7, 2, 9, 4, 3, 8]
    palace_order = palace_order_yang if is_yang_dun else palace_order_yin
    
    start_idx = palace_order.index(zhifu_palace)
    palaces_rotated = palace_order[start_idx:] + palace_order[:start_idx]
    
    deity_map = {}
    for i, palace in enumerate(palaces_rotated[:8]):
        deity_map[palace] = deities[i]
    
    # 5궁은 2궁의 신을 사용
    deity_map[5] = deity_map.get(2, "직부")
    
    return deity_map


def _arrange_stems_on_plates(ju_number: int, hour_stem: str) -> Tuple[Dict[int, str], Dict[int, str]]:
    """지반과 천반의 천간 배치"""
    # 지반: 戊를 ju_number 궁에 배치하고 순서대로
    earth_plate_stems = ["무", "기", "경", "신", "임", "계", "정", "병", "을"]
    heaven_plate_stems = ["무", "기", "경", "신", "임", "계", "정", "병", "을"]
    
    # 갑은 항상 무 아래 숨음 (遁甲)
    # 지반 배치
    earth_plate = {}
    palace_order = [ju_number] + [(ju_number + i) % 9 + 1 for i in range(8)]
    for i, palace in enumerate(palace_order[:9]):
        if palace == 5:  # 중궁은 2궁과 공유
            earth_plate[5] = earth_plate.get(2, "무")
        else:
            earth_plate[palace] = earth_plate_stems[i]
    
    # 천반: 시간에 따라 회전
    hour_stem_value = HEAVENLY_STEMS.index(hour_stem) if hour_stem in HEAVENLY_STEMS else 0
    rotation = hour_stem_value % 9
    
    heaven_plate = {}
    for palace in range(1, 10):
        earth_stem = earth_plate.get(palace, "무")
        earth_idx = earth_plate_stems.index(earth_stem) if earth_stem in earth_plate_stems else 0
        heaven_idx = (earth_idx + rotation) % 9
        heaven_plate[palace] = heaven_plate_stems[heaven_idx]
    
    return earth_plate, heaven_plate


def _calculate_palace_quality(palace: QimenPalace) -> int:
    """궁의 종합 길흉 점수 계산 (0-100)"""
    score = 50  # 기본 점수
    
    # 문의 길흉
    gate_quality = EIGHT_GATES.get(palace.gate, {}).get("quality", 50)
    score = (score + gate_quality) // 2
    
    # 별의 길흉
    star_quality = NINE_STARS.get(palace.star, {}).get("quality", 50)
    score = (score + star_quality) // 2
    
    # 신의 길흉
    deity_quality = DEITY_QUALITIES.get(palace.deity, 50)
    score = (score + deity_quality) // 2
    
    # 천간 상생상극 (간단히 처리)
    earth_elem = STEM_ELEMENT.get(palace.earthly_plate_gan, "土")
    heaven_elem = STEM_ELEMENT.get(palace.heavenly_plate_gan, "土")
    
    # 오행 상생: 木生火, 火生土, 土生金, 金生水, 水生木
    sheng_map = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    # 오행 상극: 木克土, 土克水, 水克火, 火克金, 金克木
    ke_map = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    
    if sheng_map.get(earth_elem) == heaven_elem or sheng_map.get(heaven_elem) == earth_elem:
        score += 10  # 상생 보너스
    elif ke_map.get(earth_elem) == heaven_elem:
        score -= 15  # 천간이 지간을 극함 (불리)
    elif ke_map.get(heaven_elem) == earth_elem:
        score -= 5   # 지간이 천간을 극함 (약간 불리)
    
    # 특수 조합
    # 생문 + 천봉 + 직부 = 대길
    if palace.gate == "생문" and palace.star == "천봉" and palace.deity == "직부":
        score = 100
    
    # 사문 + 천예 + 백호 = 대흉
    if palace.gate == "사문" and palace.star == "천예" and palace.deity == "백호":
        score = 10
    
    return max(0, min(100, score))


# ---------------------------------------------------------------------------
# 공개 함수
# ---------------------------------------------------------------------------

def calculate_complete_qimen(
    birth_date: date,
    target_date: date,
    target_hour: int
) -> CompleteQimenResult:
    """
    완전한 기문둔갑 계산
    
    Args:
        birth_date: 출생일
        target_date: 분석 대상 날짜
        target_hour: 분석 대상 시간 (0-23)
    
    Returns:
        CompleteQimenResult: 완전한 기문둔갑 분석 결과
    """
    # 1. 일간지와 시간지 계산
    day_stem, day_branch = _get_day_stem_branch(target_date)
    hour_stem, hour_branch = _get_hour_stem_branch(day_stem, target_hour)
    
    # 2. 양둔/음둔 결정
    is_yang_dun = _determine_yang_yin_dun(target_date)
    
    # 3. 局數 계산
    ju_number = _calculate_ju_number(day_stem, day_branch, is_yang_dun, target_date)
    
    # 4. 각 요소 배치
    palace_rotation = _rotate_palaces(ju_number, is_yang_dun)
    gate_map = _arrange_gates(ju_number, is_yang_dun)
    star_map = _arrange_stars(hour_stem, is_yang_dun)
    deity_map = _arrange_deities(hour_branch, is_yang_dun)
    earth_plate, heaven_plate = _arrange_stems_on_plates(ju_number, hour_stem)
    
    # 5. 9궁 정보 생성
    palaces = []
    for palace_num in range(1, 10):
        palace_info = LUOSHU_PALACE[palace_num]
        
        palace = QimenPalace(
            palace_num=palace_num,
            direction_ko=palace_info["dir_ko"],
            direction_en=palace_info["dir_en"],
            gate=gate_map.get(palace_num, ""),
            star=star_map.get(palace_num, ""),
            deity=deity_map.get(palace_num, ""),
            earthly_plate_gan=earth_plate.get(palace_num, ""),
            heavenly_plate_gan=heaven_plate.get(palace_num, ""),
            quality_score=0  # 일단 0으로 초기화
        )
        
        # 종합 점수 계산
        palace.quality_score = _calculate_palace_quality(palace)
        palaces.append(palace)
    
    # 6. 최적/회피 궁 결정
    best_palace = max(palaces, key=lambda p: p.quality_score)
    avoid_palace = min(palaces, key=lambda p: p.quality_score)
    
    # 7. 전체 품질 판정
    avg_score = sum(p.quality_score for p in palaces) / 9
    if avg_score >= 70:
        overall_quality = "excellent"
    elif avg_score >= 50:
        overall_quality = "good"
    elif avg_score >= 30:
        overall_quality = "neutral"
    else:
        overall_quality = "bad"
    
    # 8. 사용자 가이드 생성
    hour_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
    hour_idx = (target_hour + 1) // 2 % 12
    current_hour_branch = hour_branches[hour_idx]
    
    guidance = f"{target_hour:02d}시({current_hour_branch}시)는 "
    
    if overall_quality == "excellent":
        guidance += "매우 좋은 시간입니다. "
        guidance += f"{best_palace.direction_ko}쪽이 특히 유리합니다."
    elif overall_quality == "good":
        guidance += "좋은 시간입니다. "
        guidance += f"{best_palace.direction_ko}쪽을 활용하세요."
    elif overall_quality == "neutral":
        guidance += "평범한 시간입니다. "
        guidance += f"{avoid_palace.direction_ko}쪽은 피하는 것이 좋습니다."
    else:
        guidance += "주의가 필요한 시간입니다. "
        guidance += f"중요한 일은 피하고 {best_palace.direction_ko}쪽에서 휴식을 취하세요."
    
    # 시작/종료 시간 계산
    if hour_idx == 0:  # 자시
        hour_start = 23
        hour_end = 1
    else:
        hour_start = (hour_idx * 2 - 1) % 24
        hour_end = (hour_idx * 2 + 1) % 24
    
    return CompleteQimenResult(
        hour_start=hour_start,
        hour_end=hour_end,
        hour_branch=current_hour_branch,
        palaces=palaces,
        best_palace=best_palace,
        avoid_palace=avoid_palace,
        overall_quality=overall_quality,
        user_guidance=guidance
    )


def get_daily_complete_qimen(
    birth_date: date,
    target_date: date
) -> List[CompleteQimenResult]:
    """
    하루 전체 (12시진)의 완전한 기문둔갑 분석
    
    Returns:
        12개의 CompleteQimenResult 리스트
    """
    results = []
    
    # 12시진 (2시간 단위)
    for hour_idx in range(12):
        if hour_idx == 0:  # 자시 (23:00 ~ 01:00)
            target_hour = 23
        else:
            target_hour = hour_idx * 2 - 1
        
        result = calculate_complete_qimen(birth_date, target_date, target_hour)
        results.append(result)
    
    return results


def get_qimen_summary(
    birth_date: date,
    target_date: date
) -> Dict[str, any]:
    """
    일일 기문둔갑 요약 정보
    
    Returns:
        {
            "best_hour": "09-11시 (사시)",
            "best_direction": "북동",
            "avoid_hour": "15-17시 (신시)",
            "avoid_direction": "남서",
            "lucky_gates": ["생문", "개문", "휴문"],
            "lucky_stars": ["천봉", "천임", "천심"],
            "daily_quality": "good",
            "guidance": "오늘은 전반적으로 좋은 날입니다..."
        }
    """
    daily_results = get_daily_complete_qimen(birth_date, target_date)
    
    # 최고/최악 시간 찾기
    best_hour = max(daily_results, key=lambda r: r.best_palace.quality_score)
    worst_hour = min(daily_results, key=lambda r: r.best_palace.quality_score)
    
    # 길한 문과 별 수집
    lucky_gates = set()
    lucky_stars = set()
    total_score = 0
    
    for result in daily_results:
        for palace in result.palaces:
            if palace.quality_score >= 70:
                if palace.gate:
                    lucky_gates.add(palace.gate)
                if palace.star:
                    lucky_stars.add(palace.star)
        
        # 각 시간대 최고 점수 누적
        total_score += result.best_palace.quality_score
    
    avg_score = total_score / 12
    
    if avg_score >= 70:
        daily_quality = "excellent"
        guidance = "오늘은 매우 좋은 날입니다. 적극적으로 활동하세요."
    elif avg_score >= 50:
        daily_quality = "good"
        guidance = "오늘은 전반적으로 좋은 날입니다. 계획한 일을 추진하기 좋습니다."
    elif avg_score >= 30:
        daily_quality = "neutral"
        guidance = "오늘은 평범한 날입니다. 무리하지 말고 차분히 진행하세요."
    else:
        daily_quality = "caution"
        guidance = "오늘은 신중함이 필요한 날입니다. 중요한 결정은 미루는 것이 좋습니다."
    
    return {
        "best_hour": f"{best_hour.hour_start:02d}-{best_hour.hour_end:02d}시 ({best_hour.hour_branch}시)",
        "best_direction": best_hour.best_palace.direction_ko,
        "avoid_hour": f"{worst_hour.hour_start:02d}-{worst_hour.hour_end:02d}시 ({worst_hour.hour_branch}시)",
        "avoid_direction": worst_hour.avoid_palace.direction_ko,
        "lucky_gates": list(lucky_gates)[:3],
        "lucky_stars": list(lucky_stars)[:3],
        "daily_quality": daily_quality,
        "guidance": guidance
    }


# ---------------------------------------------------------------------------
# 테스트 코드
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_birth = date(1971, 11, 17)
    test_date = date(2026, 3, 28)
    test_hour = 9  # 09시
    
    print("=" * 70)
    print("완전한 기문둔갑 분석")
    print("=" * 70)
    
    # 단일 시간 분석
    result = calculate_complete_qimen(test_birth, test_date, test_hour)
    
    print(f"\n날짜: {test_date}")
    print(f"시간: {test_hour:02d}:00 ({result.hour_branch}시)")
    print(f"전체 품질: {result.overall_quality}")
    print(f"가이드: {result.user_guidance}")
    
    print(f"\n최적 궁: {result.best_palace.palace_num}궁 ({result.best_palace.direction_ko})")
    print(f"  - 문: {result.best_palace.gate}")
    print(f"  - 별: {result.best_palace.star}")
    print(f"  - 신: {result.best_palace.deity}")
    print(f"  - 점수: {result.best_palace.quality_score}")
    
    print(f"\n회피 궁: {result.avoid_palace.palace_num}궁 ({result.avoid_palace.direction_ko})")
    print(f"  - 점수: {result.avoid_palace.quality_score}")
    
    print("\n" + "=" * 70)
    print("일일 요약")
    print("=" * 70)
    
    # 일일 요약
    summary = get_qimen_summary(test_birth, test_date)
    
    print(f"최적 시간: {summary['best_hour']}")
    print(f"최적 방향: {summary['best_direction']}")
    print(f"회피 시간: {summary['avoid_hour']}")
    print(f"회피 방향: {summary['avoid_direction']}")
    print(f"길한 문: {', '.join(summary['lucky_gates'])}")
    print(f"길한 별: {', '.join(summary['lucky_stars'])}")
    print(f"일일 품질: {summary['daily_quality']}")
    print(f"가이드: {summary['guidance']}")