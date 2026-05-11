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
from .pipeline import (
    PipelineProgress,
    PipelineResult,
    generate_diary,
)
from .qimen import QimenEngineError, calculate_qimen
from .render import color_to_hex, render_diary
from .retry import is_retryable, with_retry
from .saju import SajuEngineError, calculate_saju

__all__ = [
    "calculate_saju",
    "calculate_qimen",
    "generate_daily_content",
    "render_diary",
    "generate_diary",
    "color_to_hex",
    "with_retry",
    "is_retryable",
    "CompleteSajuData",
    "DailyContent",
    "FourPillars",
    "Pillar",
    "QimenPalace",
    "QimenResult",
    "SajuInput",
    "PipelineProgress",
    "PipelineResult",
    "SajuEngineError",
    "QimenEngineError",
    "ContentGenerationError",
]
__version__ = "0.1.0"
