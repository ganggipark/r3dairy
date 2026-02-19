"""
리듬 신호 생성 엔진
Rhythm Signal Generator

사주명리 계산 결과를 RhythmSignal 객체로 변환
"""
import datetime
from typing import List, Dict, Any
from .models import BirthInfo, RhythmSignal, MonthlyRhythmSignal, YearlyRhythmSignal
from .saju import calculate_saju, analyze_daily_fortune, analyze_monthly_rhythm, analyze_yearly_rhythm


class RhythmAnalyzer:
    """리듬 분석기 - 사주명리 계산을 리듬 신호로 변환"""

    def __init__(self):
        self.version = "1.0.0"

    def generate_daily_signal(
        self,
        birth_info: BirthInfo,
        target_date: datetime.date
    ) -> RhythmSignal:
        """
        일간 리듬 신호 생성

        Args:
            birth_info: 출생 정보
            target_date: 분석 대상 날짜

        Returns:
            RhythmSignal: 일간 리듬 신호 (내부 표현)
        """
        # 1. 사주명리 계산
        saju_data = calculate_saju(birth_info, target_date)

        # 2. 일간 운세 분석
        fortune = analyze_daily_fortune(birth_info, target_date, saju_data)

        # 3. RhythmSignal 객체 생성
        signal = RhythmSignal(
            date=target_date,
            saju_data=saju_data,
            energy_level=fortune.get("에너지_수준", 3),
            focus_capacity=fortune.get("집중력", 3),
            social_energy=fortune.get("사회운", 3),
            decision_clarity=fortune.get("결정력", 3),
            favorable_times=fortune.get("유리한_시간", []),
            caution_times=fortune.get("주의_시간", []),
            favorable_directions=fortune.get("유리한_방향", []),
            main_theme=fortune.get("주요_흐름", "안정"),
            opportunities=fortune.get("기회_요소", []),
            challenges=fortune.get("도전_요소", []),
            calculation_version=self.version,
            created_at=datetime.datetime.now()
        )

        return signal

    def generate_monthly_signal(
        self,
        birth_info: BirthInfo,
        year: int,
        month: int
    ) -> MonthlyRhythmSignal:
        """
        월간 리듬 신호 생성

        Args:
            birth_info: 출생 정보
            year: 연도
            month: 월 (1-12)

        Returns:
            MonthlyRhythmSignal: 월간 리듬 신호
        """
        # 1. 사주 원국 계산 (해당 월 1일 기준)
        target_date = datetime.date(year, month, 1)
        saju_data = calculate_saju(birth_info, target_date)

        # 2. 월간 리듬 분석
        monthly = analyze_monthly_rhythm(birth_info, year, month, saju_data)

        # 3. 일별_에너지로부터 에너지 추세 문자열 생성
        daily_energy: Dict[int, int] = monthly.get("일별_에너지", {})
        energy_trend = self._derive_energy_trend(daily_energy)

        # 4. 기회/도전 요소에서 내부 용어 제거 후 사용자 친화적으로 변환
        raw_focus = monthly.get("기회_요소", [])
        raw_caution = monthly.get("도전_요소", [])
        focus_areas = self._sanitize_ohaeng_terms(raw_focus)
        caution_areas = self._sanitize_ohaeng_terms(raw_caution)

        signal = MonthlyRhythmSignal(
            year=year,
            month=month,
            main_theme=monthly.get("주제", "안정과 유지"),
            energy_trend=energy_trend,
            focus_areas=focus_areas,
            caution_areas=caution_areas,
        )

        return signal

    def generate_yearly_signal(
        self,
        birth_info: BirthInfo,
        year: int
    ) -> YearlyRhythmSignal:
        """
        연간 리듬 신호 생성

        Args:
            birth_info: 출생 정보
            year: 연도

        Returns:
            YearlyRhythmSignal: 연간 리듬 신호
        """
        # 1. 사주 원국 계산 (해당 년도 1월 1일 기준)
        target_date = datetime.date(year, 1, 1)
        saju_data = calculate_saju(birth_info, target_date)

        # 2. 연간 리듬 분석
        yearly = analyze_yearly_rhythm(birth_info, year, saju_data)

        # 3. 키워드: 핵심_과제 + 용신 결합 (중복 제거, 5~7개 제한)
        core_tasks = yearly.get("핵심_과제", [])
        yongsin = yearly.get("용신", [])
        # 용신은 오행 단어이므로 사용자 친화적 표현으로 변환
        yongsin_friendly = self._ohaeng_to_user_keyword(yongsin)
        combined = list(dict.fromkeys(core_tasks + yongsin_friendly))  # 순서 유지 중복 제거
        keywords = combined[:7]

        # 4. 월별_신호에서 성장 월(에너지 >= 4)과 주의 월(에너지 <= 2) 추출
        monthly_signals: Dict[int, Dict] = yearly.get("월별_신호", {})
        month_name_map = {
            1: "1월", 2: "2월", 3: "3월", 4: "4월", 5: "5월", 6: "6월",
            7: "7월", 8: "8월", 9: "9월", 10: "10월", 11: "11월", 12: "12월"
        }
        month_wuxing_map = {
            1: "수", 2: "수", 3: "목", 4: "목", 5: "화", 6: "화",
            7: "토", 8: "금", 9: "금", 10: "토", 11: "수", 12: "수"
        }

        growth_areas: List[str] = []
        caution_periods: List[str] = []

        for m_num in range(1, 13):
            m_data = monthly_signals.get(m_num, {})
            energy = m_data.get("에너지", 3)
            wx_label = month_wuxing_map.get(m_num, "목")
            label = f"{month_name_map[m_num]} ({wx_label} 에너지)"
            if energy >= 4:
                growth_areas.append(label)
            elif energy <= 2:
                caution_periods.append(label)

        # 5. monthly_summary: {월번호: "테마 (에너지 N/5)"}
        monthly_summary: Dict[int, str] = {}
        for m_num in range(1, 13):
            m_data = monthly_signals.get(m_num, {})
            theme = m_data.get("테마", "균형")
            energy = m_data.get("에너지", 3)
            monthly_summary[m_num] = f"{theme} (에너지 {energy}/5)"

        signal = YearlyRhythmSignal(
            year=year,
            main_theme=yearly.get("주제", "안정과 성장의 해"),
            keywords=keywords,
            growth_areas=growth_areas,
            caution_periods=caution_periods,
            monthly_summary=monthly_summary,
        )

        return signal

    # ========================================================================
    # 내부 유틸리티 메서드
    # ========================================================================

    def _derive_energy_trend(self, daily_energy: Dict[int, int]) -> str:
        """
        일별 에너지 딕셔너리(day → 1~5)에서 초반/중반/후반 평균을 계산하여
        사람이 읽기 좋은 추세 문자열을 반환한다.

        예: "초반 강세 (3.8), 중반 안정 (3.2), 후반 약세 (2.8)"
        """
        if not daily_energy:
            return "초반 안정, 중반 안정, 후반 안정"

        days = sorted(daily_energy.keys())
        total = len(days)
        third = max(1, total // 3)

        early = days[:third]
        mid = days[third: third * 2]
        late = days[third * 2:]

        def avg(d_list: List[int]) -> float:
            if not d_list:
                return 3.0
            return round(sum(daily_energy[d] for d in d_list) / len(d_list), 1)

        def label(score: float) -> str:
            if score >= 4.0:
                return "강세"
            elif score >= 3.5:
                return "활발"
            elif score >= 2.5:
                return "안정"
            else:
                return "약세"

        e_avg = avg(early)
        m_avg = avg(mid)
        l_avg = avg(late)

        return (
            f"초반 {label(e_avg)} ({e_avg}), "
            f"중반 {label(m_avg)} ({m_avg}), "
            f"후반 {label(l_avg)} ({l_avg})"
        )

    def _sanitize_ohaeng_terms(self, items: List[str]) -> List[str]:
        """
        오행(목/화/토/금/수) 전문 용어가 포함된 항목을
        사용자 친화적 표현으로 대체한다.

        예: "목 오행 활용" → "성장·확장 에너지 활용"
        """
        ohaeng_map = {
            "목 오행 활용": "성장·확장 에너지 활용",
            "화 오행 활용": "활동·소통 에너지 활용",
            "토 오행 활용": "안정·정리 에너지 활용",
            "금 오행 활용": "결단·실행 에너지 활용",
            "수 오행 활용": "계획·휴식 에너지 활용",
            "목 오행 주의": "과도한 확장 주의",
            "화 오행 주의": "과열·충동 주의",
            "토 오행 주의": "과도한 고집 주의",
            "금 오행 주의": "지나친 단호함 주의",
            "수 오행 주의": "과도한 소극성 주의",
        }
        result = []
        for item in items:
            result.append(ohaeng_map.get(item, item))
        return result

    def _ohaeng_to_user_keyword(self, ohaeng_list: List[str]) -> List[str]:
        """
        용신 오행 목록(["목", "화", ...])을 사용자 친화적 키워드로 변환한다.
        """
        mapping = {
            "목": "성장·도전",
            "화": "소통·활동",
            "토": "안정·기반",
            "금": "결단·실행",
            "수": "계획·성찰",
        }
        return [mapping[o] for o in ohaeng_list if o in mapping]


# ============================================================================
# 편의 함수
# ============================================================================

def create_daily_rhythm(
    birth_info: BirthInfo,
    target_date: datetime.date
) -> RhythmSignal:
    """
    일간 리듬 신호 생성 (편의 함수)

    Usage:
        birth_info = BirthInfo(
            name="홍길동",
            birth_date=datetime.date(1990, 1, 15),
            birth_time=datetime.time(14, 30),
            gender=Gender.MALE,
            birth_place="서울"
        )
        signal = create_daily_rhythm(birth_info, datetime.date.today())
    """
    analyzer = RhythmAnalyzer()
    return analyzer.generate_daily_signal(birth_info, target_date)


def create_monthly_rhythm(
    birth_info: BirthInfo,
    year: int,
    month: int
) -> MonthlyRhythmSignal:
    """월간 리듬 신호 생성 (편의 함수)"""
    analyzer = RhythmAnalyzer()
    return analyzer.generate_monthly_signal(birth_info, year, month)


def create_yearly_rhythm(
    birth_info: BirthInfo,
    year: int
) -> YearlyRhythmSignal:
    """연간 리듬 신호 생성 (편의 함수)"""
    analyzer = RhythmAnalyzer()
    return analyzer.generate_yearly_signal(birth_info, year)
