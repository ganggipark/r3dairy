#!/usr/bin/env python3
"""
오늘의 안내 Markdown 생성 스크립트

요구사항:
1. today_energy_simple.json + today_time_direction_simple.json 로드
2. 데스크탑 예제 구조를 정확히 따라 Markdown 생성
3. 좌측 페이지 콘텐츠 >= 400자 (목표 700-1200자)
4. backend/daily/{date}.md에 출력
5. 사용자 노출 텍스트에서 전문 용어 사용 금지
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class DailyMarkdownGenerator:
    """일간 Markdown 생성기"""

    def __init__(self, energy_path: str, time_direction_path: str):
        """
        Args:
            energy_path: today_energy_simple.json 경로
            time_direction_path: today_time_direction_simple.json 경로
        """
        self.energy_data = self._load_json(energy_path)
        self.time_data = self._load_json(time_direction_path)

    def _load_json(self, filepath: str) -> Dict:
        """JSON 파일 로드"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_summary(self) -> str:
        """요약 섹션 생성 (2문장)"""
        energy = self.energy_data['energy']
        flags = self.energy_data['flags']

        rhythm = energy['rhythm_label']
        intensity = energy['intensity_level']
        focus = energy['focus_level']
        recovery = energy['recovery_need']

        # 첫 문장: 리듬과 집중력
        sentence1 = f"오늘은 **{rhythm} 리듬**의 날입니다. "
        if intensity == "낮음" and focus == "높음":
            sentence1 += "활동 에너지는 낮지만 집중력은 높아, 조용히 몰두할 수 있는 일에 적합합니다."
        elif intensity == "높음" and focus == "높음":
            sentence1 += "활동 에너지와 집중력이 모두 높아, 도전적인 일을 추진하기 좋은 날입니다."
        elif intensity == "높음" and focus == "낮음":
            sentence1 += "활동 에너지는 높지만 집중력은 낮아, 가벼운 일이나 사교 활동에 적합합니다."
        else:
            sentence1 += f"활동 에너지는 {intensity}, 집중력은 {focus} 수준입니다."

        # 두 번째 문장: 주의사항 또는 핵심 포인트
        sentence2 = ""
        if flags.get('fatigue_risk'):
            sentence2 = "과로 주의가 필요하니, 자신의 페이스를 지키며 휴식을 충분히 취하세요."
        elif flags.get('overpromise_risk'):
            sentence2 = "과도한 약속이나 의욕에 주의하며, 실현 가능한 범위 내에서 계획하세요."
        elif flags.get('conflict_risk'):
            sentence2 = "관계나 소통에서 오해가 생길 수 있으니, 신중한 표현이 필요합니다."
        elif flags.get('spending_risk'):
            sentence2 = "충동적인 지출에 주의하며, 계획적인 소비를 유지하세요."
        elif flags.get('mistake_risk'):
            sentence2 = "실수나 놓침이 생기기 쉬우니, 꼼꼼한 확인이 필요합니다."
        elif recovery == "높음":
            sentence2 = "휴식이 필요한 날이니, 무리한 일정보다는 여유를 두세요."
        else:
            sentence2 = "오늘의 흐름을 따라가며 균형 있게 하루를 운영하세요."

        return sentence1 + " " + sentence2

    def generate_keywords(self) -> str:
        """키워드 섹션 생성 (8-10개)"""
        keywords_scores = self.energy_data['keywords']['scores']
        # 점수 기준 내림차순 정렬 후 상위 8-10개 선택
        sorted_keywords = sorted(keywords_scores.items(), key=lambda x: x[1], reverse=True)
        top_keywords = [kw for kw, score in sorted_keywords if score >= 0.3][:10]

        return " • ".join(top_keywords)

    def generate_rhythm_explanation(self) -> str:
        """리듬 해설 섹션 생성 (3 문단, 250+ 자)"""
        energy = self.energy_data['energy']

        # 문단 1: 오늘의 전체 흐름
        para1 = f"오늘은 {energy['rhythm_label']} 흐름이 주를 이룹니다. "
        if energy['intensity_level'] == "낮음":
            para1 += "활동 에너지가 낮아 큰 일보다는 차근차근 진행하는 작업에 적합합니다. "
        elif energy['intensity_level'] == "높음":
            para1 += "활동 에너지가 높아 많은 일을 추진할 수 있는 날입니다. "
        else:
            para1 += "활동 에너지가 보통 수준으로, 적당한 페이스 유지가 좋습니다. "

        if energy['focus_level'] == "높음":
            para1 += "반면 **집중력은 높은 편**이라, 한 가지 일에 몰두하면 좋은 성과를 낼 수 있습니다."
        elif energy['focus_level'] == "낮음":
            para1 += "다만 집중력은 다소 낮아, 가볍고 짧은 작업 위주로 진행하는 것이 좋습니다."
        else:
            para1 += "집중력은 보통 수준이므로, 적절한 휴식을 섞어가며 일하세요."

        # 문단 2: 의사결정과 소통
        para2 = ""
        if energy['decision_level'] == "높음":
            para2 += "의사결정이나 마무리 능력이 뛰어난 날입니다. "
        elif energy['decision_level'] == "낮음":
            para2 += "의사결정은 다소 어려울 수 있으니, 중요한 결정은 미루는 것이 좋습니다. "
        else:
            para2 += "의사결정이나 마무리 능력은 보통 수준이고, "

        if energy['social_level'] == "높음":
            para2 += "소통과 관계 활동도 활발하여 사람들과의 만남이 즐거운 날입니다."
        elif energy['social_level'] == "낮음":
            para2 += "소통과 관계 활동은 오늘 활발하지 않습니다."
        else:
            para2 += "소통 활동은 적당한 수준으로 유지하세요."

        # 문단 3: 휴식 필요도
        para3 = ""
        if energy['recovery_need'] == "높음":
            para3 = "대신 **휴식의 필요성이 높은 날**이므로, 무리한 일정보다는 여유를 두고 운영하는 것이 중요합니다."
        elif energy['recovery_need'] == "낮음":
            para3 = "컨디션이 좋은 편이라 여러 활동을 소화할 수 있지만, 과신하지 말고 적절한 휴식도 챙기세요."
        else:
            para3 = "휴식과 활동의 균형을 유지하며, 자신의 상태를 잘 관찰하세요."

        return para1 + "\n\n" + para2 + " " + para3

    def generate_focus_attention(self) -> str:
        """집중/주의 포인트 섹션 생성"""
        energy = self.energy_data['energy']
        flags = self.energy_data['flags']

        # 집중 포인트 (2-3개)
        focus_points = []
        if energy['focus_level'] == "높음":
            focus_points.append("- **깊은 집중 작업**: 높은 집중력을 활용해 학습이나 정리 작업을 하기 좋습니다.")
            focus_points.append("- **조용한 몰두**: 혼자 집중할 수 있는 환경에서 효율이 올라갑니다.")
        if energy['decision_level'] == "높음":
            focus_points.append("- **중요한 결정**: 판단력이 좋은 날이니 미뤄뒀던 결정을 내리기 좋습니다.")
        if energy['social_level'] == "높음":
            focus_points.append("- **관계 활동**: 사람들과의 만남이나 소통이 자연스럽고 즐거운 날입니다.")
        if energy['intensity_level'] == "낮음" and energy['focus_level'] != "낮음":
            focus_points.append("- **계획적 실행**: 급하게 서두르지 않고 천천히 진행하면 실수가 줄어듭니다.")

        # 기본값
        if not focus_points:
            focus_points.append("- **균형 유지**: 오늘의 리듬에 맞춰 적절한 페이스로 일하세요.")

        # 주의 포인트 (2-3개)
        attention_points = []
        if flags.get('fatigue_risk'):
            attention_points.append("- **과로 위험**: 컨디션이 낮은 상태에서 무리하면 피로가 쌓입니다.")
            attention_points.append("- **체력 관리**: 에너지를 아껴 쓰고, 중간중간 휴식을 꼭 챙기세요.")
        if flags.get('overpromise_risk'):
            attention_points.append("- **과도한 약속**: 의욕이 앞서 너무 많은 것을 약속하지 마세요.")
        if flags.get('conflict_risk'):
            attention_points.append("- **소통 주의**: 오해나 마찰이 생기기 쉬우니 신중한 표현이 필요합니다.")
        if flags.get('spending_risk'):
            attention_points.append("- **지출 관리**: 충동 구매나 불필요한 지출을 자제하세요.")
        if flags.get('mistake_risk'):
            attention_points.append("- **실수 방지**: 놓치거나 착각하기 쉬운 날이니 꼼꼼히 확인하세요.")

        # 기본값
        if not attention_points:
            attention_points.append("- **자기 관찰**: 자신의 상태를 잘 살피며 무리하지 마세요.")

        result = "### 집중\n"
        result += "\n".join(focus_points[:3])
        result += "\n\n### 주의\n"
        result += "\n".join(attention_points[:3])

        return result

    def generate_action_guide(self) -> str:
        """행동 가이드 섹션 생성"""
        energy = self.energy_data['energy']
        flags = self.energy_data['flags']

        # 권장 행동 (3-5개)
        do_actions = []
        if energy['focus_level'] == "높음":
            do_actions.append("- 한 가지 일에 집중해서 마무리하기")
            do_actions.append("- 조용한 공간에서 정리 작업 진행")
            do_actions.append("- 학습이나 독서처럼 개인 활동 우선")
        if energy['intensity_level'] == "낮음":
            do_actions.append("- 천천히 시작하고 여유 있는 일정 유지")
        if energy['recovery_need'] == "높음":
            do_actions.append("- 필요한 휴식은 미루지 말고 바로 취하기")
        if energy['decision_level'] == "높음":
            do_actions.append("- 중요한 결정이나 계획 수립하기")
        if energy['social_level'] == "높음":
            do_actions.append("- 사람들과의 만남이나 네트워킹 활동")

        # 기본값
        if not do_actions:
            do_actions = [
                "- 자신의 리듬에 맞춰 하루 운영하기",
                "- 중요한 일 우선순위 정하기",
                "- 적절한 휴식 시간 확보하기"
            ]

        # 지양 행동 (3-5개)
        avoid_actions = []
        if energy['intensity_level'] == "낮음":
            avoid_actions.append("- 빡빡한 스케줄로 하루를 채우기")
            avoid_actions.append("- 격한 운동이나 과도한 활동")
        if energy['social_level'] == "낮음":
            avoid_actions.append("- 새로운 만남이나 사교 활동에 에너지 쓰기")
            avoid_actions.append("- 장시간 SNS나 디지털 소통")
        if flags.get('spending_risk'):
            avoid_actions.append("- 충동적인 결정이나 큰 지출")
        if flags.get('conflict_risk'):
            avoid_actions.append("- 민감한 주제로 대화하거나 논쟁하기")
        if flags.get('mistake_risk'):
            avoid_actions.append("- 서두르거나 확인 없이 진행하기")

        # 기본값
        if not avoid_actions:
            avoid_actions = [
                "- 무리한 일정 강행하기",
                "- 에너지 소모가 큰 활동",
                "- 불필요한 스트레스 받기"
            ]

        result = "### 권장\n"
        result += "\n".join(do_actions[:5])
        result += "\n\n### 지양\n"
        result += "\n".join(avoid_actions[:5])

        return result

    def generate_time_direction(self) -> str:
        """시간/방향 섹션 생성"""
        qimen = self.time_data['qimen']

        result = "### 좋은 시간:\n"
        if qimen['good_windows']:
            for window in qimen['good_windows']:
                result += f"- **{window['start']}~{window['end']}**: {window['reason_plain']}\n"
        else:
            result += "- 특별한 시간 구분 없이 전반적으로 무난합니다.\n"

        result += "\n### 피할 시간:\n"
        if qimen['avoid_windows']:
            for window in qimen['avoid_windows']:
                result += f"- **{window['start']}~{window['end']}**: {window['reason_plain']}\n"
        else:
            result += "- 특별히 피해야 할 시간은 없습니다.\n"

        result += "\n### 좋은 방향:\n"
        if qimen['good_directions']:
            result += "- " + ", ".join(qimen['good_directions']) + "\n"
        else:
            result += "- 특별히 좋은 방향은 없습니다.\n"

        result += "\n### 피할 방향:\n"
        if qimen['avoid_directions']:
            result += "- " + ", ".join(qimen['avoid_directions']) + "\n"
        else:
            result += "- 특별히 없음\n"

        return result

    def generate_state_triggers(self) -> str:
        """상태 전환 트리거 섹션 생성"""
        energy = self.energy_data['energy']

        # 리듬에 따른 제스처/문구/방법 제안
        if energy['recovery_need'] == "높음":
            gesture = "- 깊게 숨 쉬기, 가만히 앉아서 명상하기"
            phrase = '- "오늘은 천천히 간다", "내 페이스대로"'
            method = "- 조용한 음악 들으며 스트레칭하기, 따뜻한 차 마시며 정리하기"
        elif energy['intensity_level'] == "높음":
            gesture = "- 힘차게 스트레칭하기, 큰 소리로 응원하기"
            phrase = '- "해낼 수 있다", "오늘은 도전의 날"'
            method = "- 경쾌한 음악 들으며 시작하기, 목표 적어보기"
        else:
            gesture = "- 가볍게 몸 풀기, 편안한 자세 잡기"
            phrase = '- "적당히 균형 있게", "무리하지 않기"'
            method = "- 차분한 음악 들으며 계획 점검하기, 짧은 산책하기"

        return f"### 제스처:\n{gesture}\n\n### 문구:\n{phrase}\n\n### 방법:\n{method}"

    def generate_meaning_shift(self) -> str:
        """의미 전환 섹션 생성"""
        energy = self.energy_data['energy']

        if energy['recovery_need'] == "높음":
            return '오늘은 "많이 하는 날"이 아니라 **"잘 쉬는 날"**입니다. 휴식은 게으름이 아니라 다음을 위한 준비입니다. 차분한 리듬을 따라가면서, 집중력을 활용해 정말 중요한 한두 가지만 마무리하세요. 나머지는 내일로 미뤄도 괜찮습니다.'
        elif energy['intensity_level'] == "높음":
            return '오늘은 "버티는 날"이 아니라 **"도전하는 날"**입니다. 높은 에너지를 활용해 미뤄뒀던 일이나 새로운 시도를 해보세요. 다만 과신하지 말고, 현실적인 범위 내에서 계획하세요.'
        elif energy['decision_level'] == "높음":
            return '오늘은 "망설이는 날"이 아니라 **"결정하는 날"**입니다. 판단력이 좋은 날이니, 미뤄뒀던 선택이나 정리를 마무리하세요. 결정 후에는 흔들리지 말고 실행에 집중하세요.'
        else:
            return '오늘은 "특별한 날"이 아니라 **"평범한 날"**입니다. 평범함은 실패가 아니라 안정입니다. 오늘의 리듬에 맞춰 자신의 페이스를 유지하며, 작은 일상을 잘 운영하세요.'

    def generate_rhythm_question(self) -> str:
        """리듬 질문 섹션 생성"""
        energy = self.energy_data['energy']

        if energy['focus_level'] == "높음":
            return "- 오늘 내가 정말 집중해야 할 한 가지는 무엇인가요?"
        elif energy['recovery_need'] == "높음":
            return "- 오늘 나에게 필요한 휴식은 무엇인가요?"
        elif energy['decision_level'] == "높음":
            return "- 오늘 결정해야 할 가장 중요한 것은 무엇인가요?"
        elif energy['social_level'] == "높음":
            return "- 오늘 누구와 어떤 대화를 나누고 싶나요?"
        else:
            return "- 오늘 하루를 어떻게 마무리하고 싶나요?"

    def generate_lifestyle_sections(self) -> str:
        """생활 카테고리 섹션 생성 (이모지 포함)"""
        lifestyle = self.energy_data['lifestyle']['reco']

        sections = []

        # 각 카테고리별 이모지와 제목
        categories = [
            ("🏃", "건강/운동", "health"),
            ("🍜", "음식/영양", "food"),
            ("👔", "패션/뷰티", "fashion"),
            ("💰", "쇼핑/금융", "finance"),
            ("🏠", "생활 공간", "space"),
            ("⏰", "일상 루틴", "routine"),
            ("📱", "디지털 소통", "digital"),
            ("🎨", "취미/창작", "hobby"),
            ("🤝", "관계/사회", "social"),
            ("❄️", "계절/환경", "season")
        ]

        for emoji, title, key in categories:
            if key in lifestyle:
                cat = lifestyle[key]
                section = f"## {emoji} {title}\n"
                section += f"**권장**: {', '.join(cat['do'])}\n"
                section += f"**지양**: {', '.join(cat['avoid'])}\n"
                section += f"**팁**: {cat['tip']}"
                sections.append(section)

        return "\n\n".join(sections)

    def generate_markdown(self) -> str:
        """전체 Markdown 생성"""
        md = "# 오늘의 안내\n\n"

        # 요약
        md += "## 요약\n"
        md += self.generate_summary() + "\n\n"

        # 키워드
        md += "## 키워드\n"
        md += "- " + self.generate_keywords() + "\n\n"

        # 리듬 해설
        md += "## 리듬 해설\n"
        md += self.generate_rhythm_explanation() + "\n\n"

        # 집중/주의 포인트
        md += "## 집중/주의 포인트\n\n"
        md += self.generate_focus_attention() + "\n\n"

        # 행동 가이드
        md += "## 행동 가이드\n\n"
        md += self.generate_action_guide() + "\n\n"

        # 시간/방향
        md += "## 시간/방향\n\n"
        md += self.generate_time_direction() + "\n"

        # 상태 전환 트리거
        md += "## 상태 전환 트리거\n\n"
        md += self.generate_state_triggers() + "\n\n"

        # 의미 전환
        md += "## 의미 전환\n"
        md += self.generate_meaning_shift() + "\n\n"

        # 리듬 질문
        md += "## 리듬 질문\n"
        md += self.generate_rhythm_question() + "\n\n"

        # 구분선
        md += "---\n\n"

        # 생활 카테고리
        md += self.generate_lifestyle_sections() + "\n"

        return md

    def save_markdown(self, output_dir: str = None, date_str: str = None) -> Path:
        """Markdown 파일 저장

        Args:
            output_dir: 출력 디렉토리 (기본값: backend/daily)
            date_str: 날짜 문자열 (기본값: 오늘 날짜)

        Returns:
            저장된 파일 경로
        """
        if output_dir is None:
            # 스크립트 위치 기준 backend/daily 디렉토리
            script_dir = Path(__file__).parent
            output_dir = script_dir / "daily"
        else:
            output_dir = Path(output_dir)

        # 디렉토리 생성
        output_dir.mkdir(parents=True, exist_ok=True)

        # 날짜 문자열
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        # 파일 경로
        output_path = output_dir / f"{date_str}.md"

        # Markdown 생성
        markdown = self.generate_markdown()

        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        # 글자 수 확인
        char_count = len(markdown)
        print(f"[OK] Markdown 생성 완료: {output_path}")
        print(f"[INFO] 총 글자 수: {char_count} 자")

        if char_count >= 700:
            print("[OK] 좌측 페이지 글자 수 목표 달성 (700+ 자)")
        elif char_count >= 400:
            print("[WARN] 좌측 페이지 최소 글자 수 충족 (400+ 자)")
        else:
            print("[ERROR] 좌측 페이지 글자 수 부족 (400 자 미만)")

        return output_path


def main():
    """메인 실행 함수"""
    import sys

    # 기본 경로 설정
    script_dir = Path(__file__).parent
    energy_path = script_dir / "output" / "today_energy_simple.json"
    time_path = script_dir / "output" / "today_time_direction_simple.json"

    # 커맨드라인 인자로 경로 변경 가능
    if len(sys.argv) >= 3:
        energy_path = Path(sys.argv[1])
        time_path = Path(sys.argv[2])

    try:
        # 생성기 초기화
        generator = DailyMarkdownGenerator(
            energy_path=str(energy_path),
            time_direction_path=str(time_path)
        )

        # Markdown 생성 및 저장
        output_path = generator.save_markdown()

        print(f"\n[SUCCESS] 생성된 파일: {output_path}")

    except FileNotFoundError as e:
        print(f"[ERROR] 에러: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
