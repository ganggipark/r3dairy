"""
NLP-Based Content Generation System

에너지 데이터와 색은식(五運六氣) 데이터를 기반으로
자연스러운 한국어 콘텐츠를 생성합니다.

**중요**: 사용자 노출 텍스트에서 전문 용어(사주명리, 기문둔갑, 오운육기 등) 절대 사용 금지.
내부 계산 결과를 일상 언어로 변환하여 실용적 라이프스타일 가이드를 제공합니다.
"""
from typing import Dict, Any, List, Optional, Tuple
from copy import deepcopy
import random


# ---------------------------------------------------------------------------
# 오행(五行) -> 사용자 친화 매핑 (내부 전문 용어 노출 금지)
# ---------------------------------------------------------------------------
_MOVEMENT_FLAVOR_MAP = {
    "木": {"flavor": "신맛", "foods": ["귤", "레몬", "매실", "식초 드레싱 샐러드", "자몽"],
           "color": "초록", "direction": "동쪽", "organ": "간",
           "activity": "스트레칭", "emotion": "창의력"},
    "火": {"flavor": "쓴맛", "foods": ["쑥", "커피(소량)", "녹차", "고들빼기", "케일"],
           "color": "빨강", "direction": "남쪽", "organ": "심장",
           "activity": "유산소", "emotion": "열정"},
    "土": {"flavor": "단맛", "foods": ["고구마", "호박", "대추", "꿀", "바나나"],
           "color": "노랑", "direction": "중앙", "organ": "소화기관",
           "activity": "걷기", "emotion": "안정감"},
    "金": {"flavor": "매운맛", "foods": ["무", "생강차", "마늘", "양파", "고추냉이"],
           "color": "흰색", "direction": "서쪽", "organ": "호흡기",
           "activity": "호흡 운동", "emotion": "집중력"},
    "水": {"flavor": "짠맛", "foods": ["미역국", "해산물", "콩", "검은깨", "두부"],
           "color": "검정/남색", "direction": "북쪽", "organ": "신장",
           "activity": "수영", "emotion": "지혜"},
}

# 六氣 -> 건강 조언 매핑 (사용자 언어)
_QI_HEALTH_MAP = {
    "풍": {"risk": "어지러움이나 근육 긴장", "advice": "바람을 직접 맞는 것을 피하고, 목과 어깨를 따뜻하게 유지하세요."},
    "열": {"risk": "열감이나 갈증", "advice": "수분을 자주 섭취하고, 시원한 환경에서 활동하세요."},
    "습": {"risk": "무거움이나 부종감", "advice": "가벼운 운동으로 순환을 돕고, 따뜻한 음식을 드세요."},
    "조": {"risk": "건조함이나 피부 트러블", "advice": "보습에 신경 쓰고, 물을 충분히 드세요."},
    "한": {"risk": "추위나 혈액순환 저하", "advice": "보온에 신경 쓰고, 따뜻한 차를 즐겨보세요."},
    "화": {"risk": "긴장이나 피로", "advice": "과도한 스트레스를 피하고, 충분한 휴식을 취하세요."},
}

# 에너지 레벨별 표현 팔레트
_ENERGY_EXPRESSIONS = {
    5: {"tone": "활기", "adjectives": ["역동적인", "충만한", "에너지 넘치는"],
        "verbs": ["도전하세요", "적극적으로 움직이세요", "시도해보세요"]},
    4: {"tone": "충실", "adjectives": ["안정적으로 높은", "생산적인", "집중력 있는"],
        "verbs": ["계획을 실행하세요", "한 걸음 나아가세요", "정리해보세요"]},
    3: {"tone": "균형", "adjectives": ["편안한", "고른", "자연스러운"],
        "verbs": ["흐름을 따르세요", "무리하지 마세요", "있는 그대로 받아들이세요"]},
    2: {"tone": "차분", "adjectives": ["조용한", "내향적인", "고요한"],
        "verbs": ["쉬어가세요", "내면에 귀 기울이세요", "천천히 진행하세요"]},
    1: {"tone": "휴식", "adjectives": ["깊은 휴식이 필요한", "재충전의", "멈춤이 필요한"],
        "verbs": ["멈추세요", "내려놓으세요", "자신을 돌보세요"]},
}

# 역할별 어휘 및 예시 매핑
_ROLE_VOCAB = {
    "student": {
        "work": "공부", "project": "과제", "meeting": "수업",
        "colleague": "친구", "boss": "선생님", "deadline": "제출일",
        "performance": "성적", "career": "진로",
        "morning_context": "등교 전", "evening_context": "하교 후",
        "decision_context": "시험이나 진로 선택",
        "social_context": "학교 친구들과의 관계",
    },
    "office_worker": {
        "work": "업무", "project": "프로젝트", "meeting": "회의",
        "colleague": "동료", "boss": "상사", "deadline": "마감",
        "performance": "성과", "career": "커리어",
        "morning_context": "출근 전", "evening_context": "퇴근 후",
        "decision_context": "보고나 의사결정",
        "social_context": "직장 동료나 거래처와의 관계",
    },
    "freelancer": {
        "work": "작업", "project": "프로젝트", "meeting": "미팅",
        "colleague": "파트너", "boss": "클라이언트", "deadline": "납기",
        "performance": "수익", "career": "사업",
        "morning_context": "하루를 시작하기 전", "evening_context": "작업을 마친 후",
        "decision_context": "계약이나 사업 판단",
        "social_context": "클라이언트나 협업 파트너와의 관계",
    },
}

# 기본 역할 (프로필에 역할 없을 때)
_DEFAULT_ROLE = "office_worker"


class NLPContentGenerator:
    """
    에너지 데이터와 색은식 데이터를 기반으로
    자연스러운 한국어 라이프스타일 콘텐츠를 생성합니다.

    사용 예시:
        gen = NLPContentGenerator(role="student")
        explanation = gen.generate_rhythm_explanation(energy_data, saekeunshik_data)
    """

    def __init__(self, role: str = _DEFAULT_ROLE):
        """
        Args:
            role: 사용자 역할 ("student", "office_worker", "freelancer")
        """
        self.role = role if role in _ROLE_VOCAB else _DEFAULT_ROLE
        self.vocab = _ROLE_VOCAB[self.role]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_rhythm_explanation(
        self,
        energy_data: Dict[str, Any],
        saekeunshik_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        3단락 리듬 해설을 생성합니다 (250자 이상).

        Args:
            energy_data: 에너지 레벨 데이터
                - energy_level (1-5): 전반 에너지
                - concentration (1-5): 집중력
                - social (1-5): 사회적 에너지
                - decision (1-5): 결정력
                - recovery_need ("high"/"medium"/"low"): 회복 필요도
                - flags (list[str]): 특수 플래그
            saekeunshik_data: 색은식 데이터 (optional)
                - dominant_movement (str): 우세 오행 ("木","火","土","金","水")
                - secondary_movement (str): 부차 오행
                - six_qi_main (str): 주기 ("풍","열","습","조","한","화")
                - six_qi_guest (str): 객기
                - balance_score (1-10): 균형 점수

        Returns:
            3단락 자연어 해설 (250자 이상)
        """
        energy = energy_data.get("energy_level", 3)
        concentration = energy_data.get("concentration", 3)
        social = energy_data.get("social", 3)
        decision = energy_data.get("decision", 3)
        recovery = energy_data.get("recovery_need", "medium")
        flags = energy_data.get("flags", [])

        expr = _ENERGY_EXPRESSIONS.get(energy, _ENERGY_EXPRESSIONS[3])
        sk = saekeunshik_data or {}
        dominant = sk.get("dominant_movement", "")
        mv_info = _MOVEMENT_FLAVOR_MAP.get(dominant, {})

        # -- 1단락: 전반적 흐름 --
        p1 = self._build_overview_paragraph(energy, expr, recovery, mv_info)

        # -- 2단락: 집중력 + 사회성 + 결정력 구체 안내 --
        p2 = self._build_detail_paragraph(concentration, social, decision, flags)

        # -- 3단락: 색은식 기반 실용 조언 --
        p3 = self._build_practical_paragraph(sk, energy)

        text = f"{p1}\n\n{p2}\n\n{p3}"

        # 최소 250자 보장
        if len(text) < 250:
            text += self._expansion_filler(energy)

        return text

    def generate_summary(self, energy_data: Dict[str, Any]) -> str:
        """
        2문장 요약을 생성합니다 (110자 이상).

        Args:
            energy_data: 에너지 레벨 데이터

        Returns:
            2문장 요약 문자열
        """
        energy = energy_data.get("energy_level", 3)
        concentration = energy_data.get("concentration", 3)
        decision = energy_data.get("decision", 3)
        recovery = energy_data.get("recovery_need", "medium")

        expr = _ENERGY_EXPRESSIONS.get(energy, _ENERGY_EXPRESSIONS[3])
        adj = random.choice(expr["adjectives"])
        verb = random.choice(expr["verbs"])

        # 문장 1: 리듬 상태
        s1 = f"오늘의 흐름은 {adj} 에너지가 주를 이루고 있습니다."

        # 문장 2: 핵심 운영 포인트
        if recovery == "high":
            s2 = f"충분한 휴식을 우선하되, 꼭 필요한 {self.vocab['work']}만 가볍게 처리하세요."
        elif decision >= 4:
            s2 = f"{self.vocab['decision_context']}에 적합한 날이니, {verb}"
        elif concentration >= 4:
            s2 = f"집중력이 높으므로 중요한 {self.vocab['work']}에 시간을 투자해보세요."
        else:
            s2 = f"무리하지 말고, 자연스러운 흐름 속에서 {verb}"

        summary = f"{s1} {s2}"
        # 최소 110자 보장
        while len(summary) < 110:
            fillers = [
                f" 오늘 하루가 의미 있는 시간이 되길 바랍니다.",
                f" {self.vocab['morning_context']} 잠시 오늘의 우선순위를 정리해보세요.",
                f" 나만의 페이스를 존중하며 하루를 보내세요.",
            ]
            for filler in fillers:
                if len(summary) >= 110:
                    break
                summary += filler
        return summary

    def generate_meaning_shift(
        self,
        recovery_need: str,
        decision_level: int,
    ) -> str:
        """
        관점 전환 문장을 생성합니다.
        높은 회복 필요도 -> 휴식의 정당성
        높은 결정력 -> 결정 기준 제시

        Args:
            recovery_need: "high" / "medium" / "low"
            decision_level: 결정력 레벨 (1-5)

        Returns:
            관점 전환 문장 (80자 이상)
        """
        if recovery_need == "high":
            shift = (
                "오늘 피곤함을 느끼는 것은 게으름이 아니라, "
                "몸과 마음이 보내는 자연스러운 충전 신호입니다. "
                f"{self.vocab['evening_context']}에는 일찍 쉬는 것이 "
                "내일의 나를 위한 가장 현명한 투자입니다. "
                "지금 멈추는 용기가 내일의 활력을 만들어줍니다."
            )
        elif decision_level >= 4:
            shift = (
                "지금 느끼는 확신은 일시적 충동이 아니라, "
                "차곡차곡 쌓인 경험에서 나오는 직감입니다. "
                f"다만 {self.vocab['decision_context']}에서는 "
                "감정과 논리를 모두 점검한 뒤 움직이세요. "
                "신중함과 결단력이 함께할 때 최선의 선택이 됩니다."
            )
        elif recovery_need == "low" and decision_level <= 2:
            shift = (
                "에너지는 충분하지만 방향이 잡히지 않는 느낌이 들 수 있습니다. "
                "이럴 때는 큰 결정을 미루고, 작은 것부터 정리하는 것이 도움이 됩니다. "
                "오늘의 작은 정돈이 내일의 명확한 방향을 만들어줍니다."
            )
        else:
            shift = (
                "특별한 일이 없는 하루도 소중한 리듬의 일부입니다. "
                "평범함 속에서 나만의 속도를 찾는 것이 진짜 성장입니다. "
                f"오늘 하루도 {self.vocab['work']}과 휴식 사이에서 "
                "자신만의 균형을 찾아가세요."
            )

        return shift

    def generate_lifestyle_tips(
        self,
        category: str,
        energy_data: Dict[str, Any],
        saekeunshik_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        카테고리별 라이프스타일 추천을 생성합니다.

        Args:
            category: 카테고리명
                "health", "food", "fashion", "finance",
                "space", "routine", "digital", "hobby",
                "social", "season"
            energy_data: 에너지 데이터
            saekeunshik_data: 색은식 데이터 (optional)

        Returns:
            { "do": [...], "avoid": [...], "tip": "..." }
        """
        sk = saekeunshik_data or {}
        dominant = sk.get("dominant_movement", "")
        six_qi = sk.get("six_qi_main", "")
        energy = energy_data.get("energy_level", 3)
        concentration = energy_data.get("concentration", 3)
        social = energy_data.get("social", 3)
        decision = energy_data.get("decision", 3)

        generator = _LIFESTYLE_GENERATORS.get(category)
        if generator is None:
            return {"do": [], "avoid": [], "tip": ""}

        return generator(
            self, energy, concentration, social, decision,
            dominant, six_qi, sk,
        )

    def ensure_minimum_length(
        self,
        sections: Dict[str, Any],
        min_chars: int = 400,
        target_chars: int = 900,
    ) -> Dict[str, Any]:
        """
        좌측 페이지 콘텐츠의 최소 글자 수를 보장합니다.

        Args:
            sections: 콘텐츠 섹션 딕셔너리
                - summary, rhythm_description, meaning_shift, rhythm_question 등
            min_chars: 최소 글자 수 (기본 400)
            target_chars: 목표 글자 수 (기본 900)

        Returns:
            글자 수가 보장된 콘텐츠 딕셔너리
        """
        result = deepcopy(sections)

        current = self._count_left_page_chars(result)
        if current >= min_chars:
            return result

        # 보강 전략 1: rhythm_description 확장
        expansions = self._generate_expansion_blocks(
            result.get("_energy_data", {}),
        )
        for block in expansions:
            if self._count_left_page_chars(result) >= target_chars:
                break
            result["rhythm_description"] = (
                result.get("rhythm_description", "") + " " + block
            )

        # 보강 전략 2: meaning_shift 확장
        if self._count_left_page_chars(result) < min_chars:
            result["meaning_shift"] = (
                result.get("meaning_shift", "") + " "
                "오늘 하루의 의미는 결과가 아니라 과정에 있습니다. "
                "지금 이 순간 느끼는 감정과 생각을 있는 그대로 인정하고, "
                "그 안에서 작은 배움을 찾아보세요. "
                "매일의 작은 깨달음이 모여 큰 변화를 만듭니다."
            )

        return result

    # ------------------------------------------------------------------
    # Paragraph builders (internal)
    # ------------------------------------------------------------------

    def _build_overview_paragraph(
        self, energy: int, expr: dict, recovery: str, mv_info: dict,
    ) -> str:
        """1단락: 전반적 흐름 설명."""
        adj = random.choice(expr["adjectives"])
        tone = expr["tone"]

        p = f"오늘의 흐름은 전반적으로 {adj} 리듬을 띠고 있습니다. "

        if recovery == "high":
            p += (
                "신체와 마음 모두 재충전이 필요한 시기이므로, "
                f"무리한 {self.vocab['work']}보다는 충분한 휴식을 우선하세요. "
            )
        elif recovery == "low":
            p += (
                f"컨디션이 좋으니 평소 미뤄뒀던 {self.vocab['work']}을 "
                "처리하기에 적합한 날입니다. "
            )
        else:
            p += (
                f"에너지가 고르게 유지되므로 {self.vocab['work']}과 "
                "휴식을 적절히 배분하면 좋습니다. "
            )

        # 색은식 기반 보조 정보 (전문 용어 없이)
        if mv_info:
            emotion = mv_info.get("emotion", "")
            if emotion:
                p += f"특히 {emotion}이 자연스럽게 올라올 수 있는 날입니다."

        return p

    def _build_detail_paragraph(
        self, concentration: int, social: int, decision: int,
        flags: List[str],
    ) -> str:
        """2단락: 집중력/사회성/결정력 구체 안내."""
        parts = []

        # 집중력
        if concentration >= 4:
            parts.append(
                f"집중력이 뛰어난 시간대가 있으므로, 중요한 {self.vocab['work']}은 "
                f"오전에 배치하면 효율이 높아집니다."
            )
        elif concentration <= 2:
            parts.append(
                "집중력이 분산되기 쉬우므로, 작은 단위로 나누어 처리하는 것이 좋습니다. "
                "짧은 휴식을 자주 넣어 리듬을 유지하세요."
            )

        # 사회성
        if social >= 4:
            parts.append(
                f"{self.vocab['social_context']}에서 긍정적인 흐름이 예상됩니다. "
                f"{self.vocab['meeting']}이나 대화가 있다면 적극적으로 임해보세요."
            )
        elif social <= 2:
            parts.append(
                "사람들과의 교류에서 에너지 소모가 클 수 있습니다. "
                "꼭 필요한 소통만 하고, 혼자만의 시간을 확보하세요."
            )

        # 결정력
        if decision >= 4:
            parts.append(
                f"판단력이 선명해지는 날이므로, {self.vocab['decision_context']}이 "
                "있다면 오늘 정리하는 것이 유리합니다."
            )
        elif decision <= 2:
            parts.append(
                "큰 결정은 하루 이틀 미루는 편이 안전합니다. "
                "오늘은 정보를 수집하고 정리하는 데 시간을 쓰세요."
            )

        # 특수 플래그
        if "이동" in flags or "travel" in flags:
            parts.append(
                "이동이나 장소 변화가 자연스러운 날입니다. "
                "새로운 환경에서 신선한 자극을 받을 수 있습니다."
            )
        if "변화" in flags or "change" in flags:
            parts.append(
                "변화의 기운이 감지됩니다. "
                "준비된 변화라면 실행해도 좋지만, 충동적 변화는 자제하세요."
            )

        if not parts:
            parts.append(
                f"오늘은 특별한 기복 없이 안정적인 하루가 될 것입니다. "
                f"평소처럼 {self.vocab['work']}을 이어가되, "
                f"자신의 페이스를 존중하세요."
            )

        return " ".join(parts)

    def _build_practical_paragraph(
        self, sk: Dict[str, Any], energy: int,
    ) -> str:
        """3단락: 색은식 기반 실용 조언."""
        dominant = sk.get("dominant_movement", "")
        six_qi = sk.get("six_qi_main", "")
        balance = sk.get("balance_score", 5)

        parts = []

        # 오행 기반 실용 팁
        mv = _MOVEMENT_FLAVOR_MAP.get(dominant)
        if mv:
            foods_sample = random.sample(mv["foods"], min(2, len(mv["foods"])))
            foods_str = ", ".join(foods_sample)
            parts.append(
                f"오늘은 {mv['flavor']}이 도움이 되는 날입니다. "
                f"{foods_str} 같은 음식을 식단에 포함해보세요."
            )
            parts.append(
                f"{mv['activity']}처럼 가벼운 움직임이 컨디션 유지에 효과적입니다."
            )

        # 육기 기반 건강 조언
        qi = _QI_HEALTH_MAP.get(six_qi)
        if qi:
            parts.append(
                f"{qi['risk']}에 유의하세요. {qi['advice']}"
            )

        # 균형 점수 기반
        if balance and balance <= 3:
            parts.append(
                "오늘은 몸과 마음의 균형이 흔들리기 쉬운 날입니다. "
                "규칙적인 식사와 충분한 수면으로 기본기를 지키세요."
            )

        if not parts:
            parts.append(
                "오늘은 기본에 충실한 하루를 보내는 것이 가장 좋습니다. "
                "규칙적인 생활 리듬을 유지하고, 무리하지 않는 선에서 "
                "하루를 마무리하세요."
            )

        return " ".join(parts)

    def _expansion_filler(self, energy: int) -> str:
        """최소 글자 수 미달 시 보강 텍스트."""
        if energy >= 4:
            return (
                " 에너지가 높은 만큼 과도한 활동에 대한 균형도 필요합니다. "
                "오후 이후에는 속도를 늦추고 마무리에 집중하세요. "
                "오늘 쌓은 활력을 내일로 이어가는 것도 중요합니다."
            )
        elif energy <= 2:
            return (
                " 에너지가 낮은 날에는 작은 성취가 큰 힘이 됩니다. "
                "오늘 할 수 있는 가장 작은 일 하나를 골라 완성해보세요. "
                "그 작은 완성이 내일의 동력이 되어줄 것입니다."
            )
        else:
            return (
                " 균형 잡힌 에너지 속에서 자신만의 속도를 찾아가세요. "
                "남과 비교하지 않고 나만의 리듬으로 하루를 보내는 것이 "
                "가장 건강한 선택입니다."
            )

    def _generate_expansion_blocks(
        self, energy_data: Dict[str, Any],
    ) -> List[str]:
        """글자 수 확장용 보강 블록 목록."""
        energy = energy_data.get("energy_level", 3)
        concentration = energy_data.get("concentration", 3)
        social = energy_data.get("social", 3)

        blocks = []

        if concentration <= 3:
            blocks.append(
                "집중력이 고르게 분산되는 흐름이므로, 한 가지 일에 오래 매달리기보다는 "
                "여러 가지 작은 작업을 번갈아 처리하는 방식이 효율적입니다. "
                "짧은 휴식을 자주 취하며 리듬을 유지해보세요."
            )
        else:
            blocks.append(
                "집중력이 높은 시간대를 잘 활용하면 평소보다 훨씬 높은 효율을 낼 수 있습니다. "
                "가장 중요한 일을 오전에 배치하고, 오후에는 가벼운 정리 작업을 하세요."
            )

        if social <= 3:
            blocks.append(
                "대인 관계에서는 무리하게 에너지를 쏟기보다 자연스러운 교류에 "
                "집중하는 것이 좋습니다. 가까운 사람과의 편안한 대화가 "
                "오늘의 관계 에너지를 채워줄 것입니다."
            )
        else:
            blocks.append(
                "사람들과의 교류에서 긍정적인 에너지를 주고받을 수 있는 날입니다. "
                "열린 마음으로 대화에 임하되, 자신의 에너지를 지나치게 소모하지 않도록 "
                "적절한 선을 유지하세요."
            )

        if energy <= 3:
            blocks.append(
                "오늘은 자신의 페이스를 존중하는 것이 중요합니다. "
                "외부의 기대나 속도에 맞추려 하기보다, 내면의 리듬에 귀 기울여보세요. "
                "작은 성취를 하나씩 쌓아가는 것이 오늘의 가장 현명한 전략입니다."
            )
        else:
            blocks.append(
                "에너지가 높은 만큼 과도한 활동에 대한 균형도 필요합니다. "
                "오후 이후에는 속도를 늦추고 마무리에 집중하세요. "
                "오늘 쌓은 활력을 내일로 이어가는 것도 중요합니다."
            )

        # 범용 블록 (항상 사용 가능)
        blocks.append(
            "하루를 시작하기 전 잠시 멈추어 오늘 가장 중요한 일 한 가지를 떠올려보세요. "
            "그 한 가지에 마음을 모으는 것만으로도 하루의 방향이 달라질 수 있습니다. "
            "완벽하지 않아도 괜찮으니, 오늘 할 수 있는 만큼만 정성을 다해보세요."
        )

        return blocks

    # ------------------------------------------------------------------
    # Lifestyle tip generators (private)
    # ------------------------------------------------------------------

    def _tips_health(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        mv = _MOVEMENT_FLAVOR_MAP.get(dominant, {})
        qi = _QI_HEALTH_MAP.get(six_qi, {})

        do_list = []
        avoid_list = []

        if energy >= 4:
            do_list.extend(["유산소 운동 30분 이상", "활동적인 야외 산책"])
            avoid_list.append("과도한 운동으로 인한 부상 주의")
        elif energy <= 2:
            do_list.extend(["가벼운 스트레칭", "따뜻한 반신욕"])
            avoid_list.append("무리한 운동")
        else:
            do_list.extend(["적당한 걷기 운동", "간단한 요가"])
            avoid_list.append("갑작스러운 고강도 운동")

        if mv.get("activity"):
            do_list.append(f"{mv['activity']}으로 컨디션 관리")

        tip = qi.get("advice", "규칙적인 생활 리듬을 유지하는 것이 가장 중요합니다.")

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_food(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        mv = _MOVEMENT_FLAVOR_MAP.get(dominant, {})

        do_list = []
        avoid_list = []

        if mv:
            foods = mv.get("foods", [])
            flavor = mv.get("flavor", "")
            do_list.append(f"{flavor} 계열 음식 섭취 ({', '.join(foods[:2])})")

        # 반대 오행 음식은 줄이기
        opposite_map = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}
        opp = opposite_map.get(dominant, "")
        opp_mv = _MOVEMENT_FLAVOR_MAP.get(opp, {})
        if opp_mv:
            avoid_list.append(f"과도한 {opp_mv.get('flavor', '')} 음식 자제")

        if energy >= 4:
            do_list.append("가벼운 식사로 활동성 유지")
            avoid_list.append("과식으로 인한 나른함")
        else:
            do_list.append("따뜻하고 소화가 잘 되는 음식")
            avoid_list.append("차갑거나 자극적인 음식")

        do_list.append("충분한 수분 섭취")

        tip = (
            f"오늘은 {mv.get('flavor', '균형 잡힌')} 맛이 도움이 됩니다. "
            f"식사 시간을 규칙적으로 지키는 것도 중요합니다."
        ) if mv else "균형 잡힌 식단과 규칙적인 식사 시간을 유지하세요."

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_fashion(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        mv = _MOVEMENT_FLAVOR_MAP.get(dominant, {})
        color = mv.get("color", "")

        do_list = []
        avoid_list = []

        if color:
            do_list.append(f"{color} 계열 컬러 포인트 활용")

        if energy >= 4 and social >= 4:
            do_list.extend(["깔끔하고 활기찬 스타일", "밝은 톤의 액세서리"])
            avoid_list.append("지나치게 화려한 차림")
        elif energy <= 2:
            do_list.extend(["편안한 소재의 옷", "자연스러운 스타일"])
            avoid_list.append("불편한 신발이나 옷")
        else:
            do_list.extend(["캐주얼하면서 정돈된 스타일", "중간 톤 컬러"])
            avoid_list.append("과하게 캐주얼한 차림")

        tip = (
            f"오늘은 {color} 계열이 기분 전환에 도움이 됩니다. "
            "편안하면서도 자신감을 주는 스타일을 선택하세요."
        ) if color else "편안하면서도 자신감을 주는 스타일을 선택하세요."

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_finance(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        do_list = []
        avoid_list = []

        if decision >= 4:
            do_list.extend([
                "계획된 소비 실행",
                "가치 있는 자기 투자",
            ])
            avoid_list.append("감정적 충동구매")
        elif decision <= 2:
            do_list.extend([
                "지출 내역 점검",
                "구매 목록 작성 후 하루 보류",
            ])
            avoid_list.extend(["큰 금액 결제", "새로운 금융 상품 가입"])
        else:
            do_list.extend(["필요한 생활용품만 구매", "예산 범위 내 소비"])
            avoid_list.append("불필요한 온라인 쇼핑")

        tip = (
            f"오늘은 {self.vocab['work']} 관련 필수 지출 외에는 "
            "신중하게 판단하는 것이 좋습니다."
        )

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_space(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        mv = _MOVEMENT_FLAVOR_MAP.get(dominant, {})
        direction = mv.get("direction", "")

        do_list = []
        avoid_list = []

        if energy >= 4:
            do_list.extend(["불필요한 물건 정리", "환기와 자연광 활용"])
            avoid_list.append("어수선한 환경 방치")
        else:
            do_list.extend(["편안한 조명 설정", "아늑한 공간 만들기"])
            avoid_list.append("큰 규모의 정리 시도")

        if direction:
            do_list.append(f"공간의 {direction} 방향 정돈에 집중")

        tip = "깨끗하고 정돈된 공간이 마음의 여유를 만들어줍니다."

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_routine(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        do_list = []
        avoid_list = []

        if energy >= 4:
            do_list.extend([
                f"{self.vocab['morning_context']} 가벼운 운동으로 시작",
                "할 일 목록 작성 후 실행",
                f"{self.vocab['evening_context']} 정리 시간 확보",
            ])
            avoid_list.append("밤늦게까지 활동 연장")
        else:
            do_list.extend([
                "여유 있는 아침 시간 확보",
                "중간중간 짧은 휴식",
                "일찍 마무리하고 이완 시간 갖기",
            ])
            avoid_list.append("빠듯한 일정 강행")

        tip = f"오늘의 페이스를 존중하면서 {self.vocab['work']}과 쉼의 균형을 지키세요."

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_digital(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        do_list = []
        avoid_list = []

        if conc >= 4:
            do_list.extend(["집중 모드 활용", "알림 최소화"])
            avoid_list.append("SNS 무한 스크롤")
        elif conc <= 2:
            do_list.extend(["스마트폰 사용 시간 제한", "디지털 디톡스 시간 확보"])
            avoid_list.append("잠들기 전 화면 보기")
        else:
            do_list.extend(["필요한 정보만 선택적 확인", "타이머 설정 후 SNS 확인"])
            avoid_list.append("무의식적 앱 전환")

        if social >= 4:
            do_list.append("메시지나 영상통화로 소통")

        tip = "디지털 기기 사용을 의식적으로 조절하면 하루의 질이 달라집니다."

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_hobby(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        mv = _MOVEMENT_FLAVOR_MAP.get(dominant, {})

        do_list = []
        avoid_list = []

        if energy >= 4 and conc >= 4:
            do_list.extend(["새로운 기술 배우기", "창작 활동에 몰입"])
            avoid_list.append("쉬지 않고 장시간 집중")
        elif energy <= 2:
            do_list.extend(["가벼운 독서나 음악 감상", "산책하며 영감 얻기"])
            avoid_list.append("에너지 소모가 큰 취미")
        else:
            do_list.extend(["관심사 탐색", "짧은 학습 세션"])
            avoid_list.append("지나치게 많은 취미 동시 진행")

        emotion = mv.get("emotion", "")
        if emotion:
            do_list.append(f"{emotion}을 활용한 활동 시도")

        tip = "취미는 에너지를 채워주는 것이어야 합니다. 오늘의 컨디션에 맞는 활동을 선택하세요."

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_social(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        do_list = []
        avoid_list = []

        if social >= 4:
            do_list.extend([
                f"{self.vocab['colleague']}와 적극적 소통",
                "새로운 인연에 열린 자세",
            ])
            avoid_list.append("독단적인 태도")
        elif social <= 2:
            do_list.extend([
                "혼자만의 시간 확보",
                "꼭 필요한 대화만 간결하게",
            ])
            avoid_list.extend(["과도한 약속", "감정적 대화"])
        else:
            do_list.extend([
                "가까운 사람과 편안한 대화",
                "경청 위주의 소통",
            ])
            avoid_list.append("불필요한 논쟁")

        tip = (
            f"오늘 {self.vocab['social_context']}에서는 "
            "진솔하되 배려 있는 소통이 가장 효과적입니다."
        )

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    def _tips_season(
        self, energy, conc, social, decision,
        dominant, six_qi, sk,
    ) -> Dict[str, Any]:
        qi = _QI_HEALTH_MAP.get(six_qi, {})

        do_list = []
        avoid_list = []

        # 육기 기반 계절 조언
        if six_qi == "한":
            do_list.extend(["보온 철저", "따뜻한 음료 섭취"])
            avoid_list.append("차가운 환경에 오래 노출")
        elif six_qi == "열" or six_qi == "화":
            do_list.extend(["시원한 환경 유지", "수분 자주 섭취"])
            avoid_list.append("직사광선 장시간 노출")
        elif six_qi == "습":
            do_list.extend(["제습기 가동", "가벼운 옷차림"])
            avoid_list.append("축축한 환경에 오래 머물기")
        elif six_qi == "조":
            do_list.extend(["가습기 사용", "피부 보습"])
            avoid_list.append("건조한 환경 방치")
        elif six_qi == "풍":
            do_list.extend(["바람막이 준비", "목 보호"])
            avoid_list.append("강한 바람 직접 노출")
        else:
            do_list.extend(["날씨에 맞는 옷차림", "환기 자주 하기"])
            avoid_list.append("급격한 온도 변화")

        tip = qi.get("advice", "계절에 맞는 생활 습관을 유지하는 것이 건강의 기본입니다.")

        return {"do": do_list[:4], "avoid": avoid_list[:3], "tip": tip}

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _count_left_page_chars(sections: Dict[str, Any]) -> int:
        """좌측 페이지 주요 텍스트 필드의 총 글자 수."""
        total = 0
        for key in ("summary", "rhythm_description", "meaning_shift", "rhythm_question"):
            val = sections.get(key, "")
            if isinstance(val, str):
                total += len(val)
        return total


# ---------------------------------------------------------------------------
# Category -> generator method mapping
# ---------------------------------------------------------------------------
_LIFESTYLE_GENERATORS = {
    "health": NLPContentGenerator._tips_health,
    "food": NLPContentGenerator._tips_food,
    "fashion": NLPContentGenerator._tips_fashion,
    "finance": NLPContentGenerator._tips_finance,
    "space": NLPContentGenerator._tips_space,
    "routine": NLPContentGenerator._tips_routine,
    "digital": NLPContentGenerator._tips_digital,
    "hobby": NLPContentGenerator._tips_hobby,
    "social": NLPContentGenerator._tips_social,
    "season": NLPContentGenerator._tips_season,
}
