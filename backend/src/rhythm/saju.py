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
from .models import BirthInfo, RhythmSignal


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
    # Node.js CLI 경로 (정확한 saju-engine 사용)
    current_dir = Path(__file__).parent.parent.parent  # backend/
    cli_path = current_dir / "saju-engine" / "cli.js"

    if not cli_path.exists():
        raise RuntimeError(f"사주 계산기 CLI를 찾을 수 없습니다: {cli_path}")

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

    # 에너지 수준 계산 (용신 맞는지 확인)
    energy_level = 3  # 기본값
    if sewoon and dominant_element in yongsin_list:
        energy_level = 4
    elif sewoon and dominant_element in gisin_list:
        energy_level = 2

    # 집중력/사회운/결정력 계산 (십성 기반)
    sipsung = saju_data.get("십성", {})
    concentration = 3 + (sipsung.get("식신", 0) + sipsung.get("상관", 0)) // 2
    social = 3 + (sipsung.get("정관", 0) + sipsung.get("편관", 0)) // 2
    decision = 3 + (sipsung.get("비견", 0) + sipsung.get("겁재", 0)) // 2

    # 1-5 범위로 제한
    concentration = min(5, max(1, concentration))
    social = min(5, max(1, social))
    decision = min(5, max(1, decision))

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
    }

    return fortune_analysis


def get_favorable_times(saju_data: Dict[str, Any], target_date: datetime.date) -> list[str]:
    """
    유리한 시간대 계산 (천을귀인 기반)
    """
    sinsal = saju_data.get("신살", {})

    # 천을귀인이 있으면 해당 시간대가 유리
    if sinsal.get("hasCheonEulGuiIn"):
        return ["오전 9-11시 (사시)", "오후 2-4시 (신시)"]

    # 기본값
    return ["오전 10-12시", "오후 3-5시"]


def get_caution_times(saju_data: Dict[str, Any], target_date: datetime.date) -> list[str]:
    """
    주의 시간대 계산
    """
    # 공망이 있으면 해당 시간대 주의
    sinsal = saju_data.get("신살", {})
    if sinsal.get("hasGongMang"):
        return ["오후 5-7시 (유시)"]

    return ["자정 전후"]


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

    # 일별 에너지 수준 계산 (간단한 알고리즘)
    days_in_month = calendar.monthrange(year, month)[1]
    daily_energy = {}

    for day in range(1, days_in_month + 1):
        # 매우 단순한 알고리즘: 날짜를 기반으로 1-5 사이 점수
        # 실제로는 각 날짜의 일주를 계산해야 하지만, 성능을 위해 간소화
        base_energy = 3

        # 용신 오행이 강한 날은 에너지 +1
        if day % 5 == 0:  # 예시: 5의 배수는 에너지 높음
            base_energy = 4
        elif day % 7 == 0:  # 7의 배수는 에너지 낮음
            base_energy = 2

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

    for month in range(1, 13):
        # 각 월의 에너지 수준 (간단한 알고리즘)
        base_score = 3
        if month in [3, 4, 5, 9, 10]:  # 봄, 가을은 에너지 높음
            base_score = 4
        elif month in [7, 8]:  # 여름은 활동적
            base_score = 4

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
