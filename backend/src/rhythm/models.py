"""
Data models for Rhythm Analysis Engine
입출력 인터페이스 표준화
"""
from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class Gender(str, Enum):
    """성별"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BirthInfo(BaseModel):
    """
    출생 정보 입력 모델
    사주명리 계산을 위한 필수 입력값
    """
    name: str = Field(..., description="이름")
    birth_date: date = Field(..., description="생년월일")
    birth_time: time = Field(..., description="출생 시간")
    gender: Gender = Field(..., description="성별")
    birth_place: str = Field(..., description="출생지 (도시명)")
    birth_place_lat: Optional[float] = Field(None, description="출생지 위도")
    birth_place_lng: Optional[float] = Field(None, description="출생지 경도")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "홍길동",
                "birth_date": "1990-01-15",
                "birth_time": "14:30:00",
                "gender": "male",
                "birth_place": "서울",
                "birth_place_lat": 37.5665,
                "birth_place_lng": 126.9780
            }
        }


class RhythmSignal(BaseModel):
    """
    리듬 신호 출력 모델

    ⚠️ 중요: 이 모델은 내부 계산 결과를 담습니다
    사용자에게 절대 직접 노출하지 마세요!

    내부 전문 용어 (사주명리, 기문둔갑 등) 사용 가능
    사용자 노출 시 Content Assembly Engine에서 변환 필수
    """
    date: date = Field(..., description="분석 대상 날짜")

    # 내부 계산 결과 (전문 용어 사용)
    saju_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="사주명리 계산 결과 (천간, 지지, 오행, 십성 등)"
    )

    qimen_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="기문둔갑 계산 결과 (옵션)"
    )

    # 리듬 분석 결과 (내부 표현)
    energy_level: int = Field(..., ge=1, le=5, description="에너지 레벨 (1-5)")
    focus_capacity: int = Field(..., ge=1, le=5, description="집중력 (1-5)")
    social_energy: int = Field(..., ge=1, le=5, description="사회적 에너지 (1-5)")
    decision_clarity: int = Field(..., ge=1, le=5, description="결정 명확도 (1-5)")

    # 시간/방향 (내부 용어)
    favorable_times: List[str] = Field(
        default_factory=list,
        description="유리한 시간대 (예: ['오전 9-11시', '오후 3-5시'])"
    )
    caution_times: List[str] = Field(
        default_factory=list,
        description="주의 시간대"
    )
    favorable_directions: List[str] = Field(
        default_factory=list,
        description="유리한 방향 (예: ['북동', '남서'])"
    )

    # 주요 흐름 (내부 표현)
    main_theme: str = Field(..., description="주요 테마 (내부 표현)")
    opportunities: List[str] = Field(
        default_factory=list,
        description="기회 요소"
    )
    challenges: List[str] = Field(
        default_factory=list,
        description="도전 요소"
    )

    # 메타데이터
    calculation_version: str = Field(default="1.0.0", description="계산 버전")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-01-20",
                "saju_data": {
                    "년주": {"천간": "甲", "지지": "子"},
                    "월주": {"천간": "丙", "지지": "寅"},
                    "일주": {"천간": "戊", "지지": "辰"},
                    "시주": {"천간": "庚", "지지": "午"}
                },
                "energy_level": 4,
                "focus_capacity": 3,
                "social_energy": 5,
                "decision_clarity": 4,
                "favorable_times": ["오전 9-11시", "오후 2-4시"],
                "caution_times": ["오후 5-7시"],
                "favorable_directions": ["북동", "남서"],
                "main_theme": "안정과 정리",
                "opportunities": ["관계 강화", "학습"],
                "challenges": ["충동 조절"]
            }
        }


class MonthlyRhythmSignal(BaseModel):
    """월간 리듬 신호"""
    year: int
    month: int

    main_theme: str = Field(..., description="월간 주요 테마")
    energy_trend: str = Field(..., description="에너지 흐름 추세")
    focus_areas: List[str] = Field(default_factory=list, description="집중 영역")
    caution_areas: List[str] = Field(default_factory=list, description="주의 영역")

    # 주차별 신호 (옵션)
    weekly_signals: Optional[List[Dict[str, Any]]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2026,
                "month": 1,
                "main_theme": "새로운 시작과 계획",
                "energy_trend": "초반 강화, 후반 안정",
                "focus_areas": ["목표 설정", "관계 정리"],
                "caution_areas": ["과도한 약속", "충동 결정"]
            }
        }


class YearlyRhythmSignal(BaseModel):
    """연간 리듬 신호"""
    year: int

    main_theme: str = Field(..., description="연간 주요 테마")
    keywords: List[str] = Field(default_factory=list, description="핵심 키워드")
    growth_areas: List[str] = Field(default_factory=list, description="성장 영역")
    caution_periods: List[str] = Field(default_factory=list, description="주의 시기")

    # 분기별 신호 (옵션)
    quarterly_signals: Optional[List[Dict[str, Any]]] = None

    # 월별 요약
    monthly_summary: Optional[Dict[int, str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2026,
                "main_theme": "확장과 실험",
                "keywords": ["도전", "학습", "관계", "건강"],
                "growth_areas": ["전문성 강화", "네트워크 확대"],
                "caution_periods": ["3월 중순", "8월 말"],
                "monthly_summary": {
                    1: "새 시작",
                    2: "관계 집중",
                    3: "조정 필요"
                }
            }
        }
