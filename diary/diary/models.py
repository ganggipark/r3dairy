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


class CompleteSajuData(BaseModel):
    model_config = ConfigDict(extra="allow")
    version: str
    isComplete: bool
    fourPillars: FourPillars
    fullSajuString: str


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
    """LLM이 생성하는 7개 narrative 필드 (lucky_*는 Python이 결정)."""
    model_config = ConfigDict(extra="forbid")

    daily_summary: str = Field(..., min_length=50, max_length=400)
    daily_focus: str = Field(..., min_length=20, max_length=200)
    daily_caution: str = Field(..., min_length=20, max_length=200)
    mindfulness: str = Field(..., min_length=80, max_length=300)
    right_page_hint: str = Field(..., min_length=8, max_length=60)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=5)
    things_to_avoid: list[str] = Field(..., min_length=1, max_length=5)


class DailyContent(BaseModel):
    """1일치 일기 콘텐츠 (11 필드). 좌측: 가이드, 우측: 작성 공간 + hint."""
    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    lucky_color: str
    lucky_direction: str
    lucky_time: str

    daily_summary: str = Field(..., min_length=50, max_length=400)
    daily_focus: str = Field(..., min_length=20, max_length=200)
    daily_caution: str = Field(..., min_length=20, max_length=200)
    mindfulness: str = Field(..., min_length=80, max_length=300)
    right_page_hint: str = Field(..., min_length=8, max_length=60)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=5)
    things_to_avoid: list[str] = Field(..., min_length=1, max_length=5)
