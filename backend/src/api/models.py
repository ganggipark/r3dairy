"""
API Request/Response Models
"""
import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from src.rhythm.models import Gender
from src.translation.models import Role


# ============================================================================
# Auth Models
# ============================================================================

class SignUpRequest(BaseModel):
    """회원가입 요청"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2, max_length=100)


class LoginRequest(BaseModel):
    """로그인 요청"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """인증 응답"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: str
    email: str
    requires_email_confirmation: bool = False
    message: Optional[str] = None


# ============================================================================
# Profile Models
# ============================================================================

class ProfileCreate(BaseModel):
    """프로필 생성 요청"""
    name: str = Field(..., min_length=2, max_length=100)
    birth_date: datetime.date
    birth_time: datetime.time
    gender: Gender
    birth_place: str = Field(..., min_length=2, max_length=200)
    roles: List[Role] = Field(default=[Role.STUDENT])
    preferences: Optional[Dict[str, Any]] = None


class ProfileUpdate(BaseModel):
    """프로필 수정 요청 (모든 필드 optional)"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    birth_date: Optional[datetime.date] = None
    birth_time: Optional[datetime.time] = None
    gender: Optional[Gender] = None
    birth_place: Optional[str] = Field(None, min_length=2, max_length=200)
    roles: Optional[List[Role]] = None
    preferences: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    """프로필 응답"""
    id: str
    name: str
    birth_date: datetime.date
    birth_time: datetime.time
    gender: Gender
    birth_place: str
    roles: List[Role]
    preferences: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


# ============================================================================
# Content Models
# ============================================================================

class DailyContentRequest(BaseModel):
    """일간 콘텐츠 요청 파라미터"""
    date: datetime.date
    role: Optional[Role] = None  # None이면 중립 콘텐츠


class DailyContentResponse(BaseModel):
    """일간 콘텐츠 응답"""
    date: datetime.date
    role: Optional[Role]
    content: Dict[str, Any]  # DailyContent를 dict로 변환


class MonthlyContentRequest(BaseModel):
    """월간 콘텐츠 요청 파라미터"""
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    role: Optional[Role] = None


class MonthlyContentResponse(BaseModel):
    """월간 콘텐츠 응답"""
    year: int
    month: int
    role: Optional[Role]
    content: Dict[str, Any]


# ============================================================================
# Log Models
# ============================================================================

class DailyLogCreate(BaseModel):
    """일간 기록 생성"""
    date: datetime.date
    schedule: Optional[str] = None
    todos: Optional[List[str]] = None
    mood: Optional[int] = Field(None, ge=1, le=5)
    energy: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    gratitude: Optional[str] = None


class DailyLogUpdate(BaseModel):
    """일간 기록 수정 (모든 필드 optional)"""
    schedule: Optional[str] = None
    todos: Optional[List[str]] = None
    mood: Optional[int] = Field(None, ge=1, le=5)
    energy: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    gratitude: Optional[str] = None


class DailyLogResponse(BaseModel):
    """일간 기록 응답"""
    id: str
    profile_id: str
    date: datetime.date
    schedule: Optional[str]
    todos: Optional[List[str]]
    mood: Optional[int]
    energy: Optional[int]
    notes: Optional[str]
    gratitude: Optional[str]
    created_at: str
    updated_at: str


# ============================================================================
# Common Response Models
# ============================================================================

class SuccessResponse(BaseModel):
    """성공 응답"""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: str
    details: Optional[str] = None
