"""Saju + Qimen I/O models. Minimal typing; rest via extra='allow'."""
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


OverallQuality = Literal["excellent", "good", "neutral", "bad"]


class QimenPalace(BaseModel):
    """9궁 중 한 궁의 기문 정보."""
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
    """기문둔갑 1시진 계산 결과 (9궁 + best/avoid)."""
    model_config = ConfigDict(extra="allow")

    hourStart: int
    hourEnd: int
    hourBranch: str
    palaces: list[QimenPalace] = Field(..., min_length=9, max_length=9)
    bestPalace: QimenPalace
    avoidPalace: QimenPalace
    overallQuality: OverallQuality
    userGuidance: str


class DailyContent(BaseModel):
    """1일치 일기 콘텐츠. MVP 9필드, 사주 용어 금지(고객 노출)."""
    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    daily_summary: str = Field(..., min_length=50, max_length=400)
    daily_focus: str = Field(..., min_length=20, max_length=200)
    daily_caution: str = Field(..., min_length=20, max_length=200)
    lucky_color: str = Field(..., max_length=20)
    lucky_direction: str = Field(..., max_length=10)
    lucky_time: str = Field(..., max_length=30)
    recommended_actions: list[str] = Field(..., min_length=1, max_length=5)
    things_to_avoid: list[str] = Field(..., min_length=1, max_length=5)
