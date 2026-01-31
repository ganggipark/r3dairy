"""
Content Block Templates

Base templates for generating content blocks.
These are neutral templates before role-specific adaptation.
"""

from typing import Dict, List

# Energy-level based summary templates
SUMMARY_TEMPLATES: Dict[int, List[str]] = {
    5: [
        "오늘은 매우 활기찬 에너지가 넘치는 날입니다. {theme}의 흐름 속에서 적극적으로 움직여보세요.",
        "높은 에너지와 함께 {theme}의 기운이 가득한 날입니다.",
    ],
    4: [
        "오늘은 충만한 에너지와 함께 {theme}의 흐름이 함께합니다.",
        "{theme}의 기운 속에서 새로운 시도가 가능한 날입니다.",
    ],
    3: [
        "오늘은 안정적인 에너지 속에서 {theme}을 실천하기 좋은 날입니다.",
        "{theme}의 균형 잡힌 흐름이 하루를 이끕니다.",
    ],
    2: [
        "오늘은 차분한 에너지가 흐르며, {theme}에 집중하기 좋습니다.",
        "고요한 흐름 속에서 {theme}의 의미를 찾아보세요.",
    ],
    1: [
        "오늘은 깊은 고요함 속에서 {theme}을 되돌아보는 시간입니다.",
        "에너지가 안으로 향하는 날, {theme}의 본질을 느껴보세요.",
    ],
}

# Meaning shift templates by energy level
MEANING_SHIFT_TEMPLATES: Dict[str, str] = {
    "high_energy": (
        "오늘 느끼는 높은 에너지는 단순한 흥분이 아니라 성장의 추진력입니다. "
        "{challenge}이(가) 찾아오더라도 이것은 더 나은 방향으로 가기 위한 과정입니다."
    ),
    "medium_energy": (
        "오늘은 균형 잡힌 에너지가 흐르는 날입니다. "
        "{challenge}이(가) 나타나더라도 차근차근 대응하면 됩니다."
    ),
    "low_energy": (
        "오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. "
        "{challenge}이(가) 마음을 흔들어도 급하지 않게 한 걸음씩 나아가세요."
    ),
}

# State trigger templates by concern type
STATE_TRIGGER_TEMPLATES: Dict[str, Dict[str, str]] = {
    "anxiety": {
        "gesture": "양손을 가슴에 모으고 천천히 세 번 호흡하세요",
        "phrase": "지금 이 순간, 나는 안전합니다",
        "how_to": "불안감이 올라올 때 눈을 감고 이 동작을 3번 반복하세요",
    },
    "procrastination": {
        "gesture": "책상을 가볍게 두 번 두드리세요",
        "phrase": "지금 시작하면 충분합니다",
        "how_to": "미루고 싶을 때 이 동작과 함께 5분만 시작해보세요",
    },
    "fatigue": {
        "gesture": "두 손으로 따뜻한 음료를 감싸세요",
        "phrase": "쉬어가는 것도 전진입니다",
        "how_to": "지칠 때 잠시 모든 것을 내려놓고 이 순간에 집중하세요",
    },
    "default": {
        "gesture": "양손을 가슴에 대고 천천히 호흡하세요",
        "phrase": "지금 이 순간, 나는 충분히 잘하고 있습니다",
        "how_to": "긴장되거나 불안할 때 이 동작을 3번 반복하세요",
    },
}
