"""diary — saju + qimen based print diary generator."""
from .content import ContentGenerationError, generate_daily_content
from .models import (
    CompleteSajuData,
    DailyContent,
    FourPillars,
    Pillar,
    QimenPalace,
    QimenResult,
    SajuInput,
)
from .qimen import QimenEngineError, calculate_qimen
from .render import color_to_hex, render_diary
from .saju import SajuEngineError, calculate_saju

__all__ = [
    "calculate_saju",
    "calculate_qimen",
    "generate_daily_content",
    "render_diary",
    "color_to_hex",
    "CompleteSajuData",
    "DailyContent",
    "FourPillars",
    "Pillar",
    "QimenPalace",
    "QimenResult",
    "SajuInput",
    "SajuEngineError",
    "QimenEngineError",
    "ContentGenerationError",
]
__version__ = "0.1.0"
