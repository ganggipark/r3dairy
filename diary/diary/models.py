"""Saju + Qimen + Content models."""
from __future__ import annotations
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SajuInput(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    gender: Literal["male", "female"]
    isLunar: bool = False
    isLeapMonth: bool = False
    useTrueSolarTime: bool = True
    birthPlace: str = "서울"


class Pillar(BaseModel):
    model_config = ConfigDict(extra="allow")
    gan: str
    ji: str
    ganJi: str


class FourPillars(BaseModel):
    model_config = ConfigDict(extra="allow")
    year: Pillar
    month: Pillar
    day: Pillar
    time: Pillar


class YongSinAnalysis(BaseModel):
    """사주 용신/기신/희신 분석 (M21)."""
    model_config = ConfigDict(extra="allow")
    yongSin: list[str] = Field(default_factory=list)
    giSin: list[str] = Field(default_factory=list)
    huiSin: list[str] = Field(default_factory=list)
    yongSinReason: str = ""
    giSinReason: str = ""
    yongSinScore: dict[str, float] = Field(default_factory=dict)


class CompleteSajuData(BaseModel):
    model_config = ConfigDict(extra="allow")
    version: str
    isComplete: bool
    fourPillars: FourPillars
    fullSajuString: str
    yongSin: YongSinAnalysis | None = Field(default=None)


class QimenPalace(BaseModel):
    model_config = ConfigDict(extra="allow")
    palaceNum: int
    directionKo: str
    directionEn: str
    gate: str
    star: str
    deity: str
    earthlyPlateGan: str
    heavenlyPlateGan: str
    qualityScore: float


class QimenResult(BaseModel):
    model_config = ConfigDict(extra="allow")
    hourStart: int
    hourEnd: int
    hourBranch: str
    palaces: list[QimenPalace] = Field(..., min_length=9, max_length=9)
    bestPalace: QimenPalace
    avoidPalace: QimenPalace
    overallQuality: Literal["excellent", "good", "neutral", "bad"]
    userGuidance: str


class _LLMNarrative(BaseModel):
    """LLM이 생성하는 narrative 필드 (lucky_*는 Python이 결정)."""
    model_config = ConfigDict(extra="forbid")

    daily_summary: str = Field(..., min_length=100, max_length=180)
    daily_focus: str = Field(..., min_length=60, max_length=100)
    daily_caution: str = Field(..., min_length=60, max_length=100)
    mindfulness: str = Field(..., min_length=100, max_length=180)
    right_page_hint: str = Field(..., min_length=8, max_length=80)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=6)
    things_to_avoid: list[str] = Field(..., min_length=1, max_length=5)
    domain_advice: dict[str, str] = Field(
        default_factory=dict,
        description="영역별 짧은 조언. keys: work/relations/health/finance (각 30~100자)",
    )
    reflection_questions: list[str] = Field(
        default_factory=list, max_length=5,
        description="자기성찰 질문 3개 (각 15-40자)",
    )


class DailyContent(BaseModel):
    """1일치 일기 콘텐츠. 좌측: 가이드, 우측: 시간 그리드 + hint."""
    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    lucky_color: str
    lucky_direction: str
    lucky_time: str
    # M24: 일과시간(07-23) 내 추천. 메인과 같으면 None (중복 회피)
    lucky_color_workday: str | None = None
    lucky_direction_workday: str | None = None
    lucky_time_workday: str | None = None
    hour_start_workday: int | None = None
    hour_end_workday: int | None = None
    # M25: 일진통변 + 신살 + 자기성찰
    ilji_pillar: str | None = Field(default=None, description="오늘 일주 (예: '병자')")
    ilji_relation: str | None = Field(
        default=None, max_length=200,
        description="본인 사주 vs 오늘 일진 천간/지지 관계 해석",
    )
    sinsal_alerts: list[str] = Field(
        default_factory=list,
        description="발동 신살 (예: ['천을귀인 발동'])",
    )
    reflection_questions: list[str] = Field(
        default_factory=list,
        description="자기성찰 질문 3개",
    )

    daily_summary: str = Field(..., min_length=100, max_length=180)
    daily_focus: str = Field(..., min_length=60, max_length=100)
    daily_caution: str = Field(..., min_length=60, max_length=100)
    mindfulness: str = Field(..., min_length=100, max_length=180)
    right_page_hint: str = Field(..., min_length=8, max_length=80)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=6)
    things_to_avoid: list[str] = Field(..., min_length=1, max_length=5)
    domain_advice: dict[str, str] = Field(
        default_factory=dict,
        description="영역별 조언 (work/relations/health/finance)",
    )
