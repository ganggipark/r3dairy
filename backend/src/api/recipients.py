"""
Diary Recipients API
다이어리 대상자 관리 CRUD 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from supabase import Client
from typing import Optional, List
from pydantic import BaseModel
import datetime

from src.db.supabase import get_supabase, SupabaseClient
from src.api.auth import get_current_user

router = APIRouter(prefix="/api/recipients", tags=["Recipients"])


# ============================================================================
# Request/Response Models
# ============================================================================

class RecipientCreate(BaseModel):
    name: str
    birth_date: str          # YYYY-MM-DD
    birth_time: str = "00:00:00"  # HH:MM:SS
    gender: str              # male, female, other
    birth_place: str = ""
    role: str = "office_worker"
    relationship: Optional[str] = None
    notes: Optional[str] = None
    diary_period: str = "monthly"
    is_default: bool = False


class RecipientUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    gender: Optional[str] = None
    birth_place: Optional[str] = None
    role: Optional[str] = None
    relationship: Optional[str] = None
    notes: Optional[str] = None
    diary_period: Optional[str] = None
    is_default: Optional[bool] = None


# ============================================================================
# Helper
# ============================================================================

def _get_auth(authorization: Optional[str], supabase_auth: Client):
    """인증 처리 공통 헬퍼"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다."
        )
    user = get_current_user(authorization, supabase_auth)
    token = authorization.split(" ")[1]
    supabase_db = SupabaseClient.create_user_db_client(token)
    return user, supabase_db


def _check_ownership(recipient: dict, user_id: str):
    """소유권 검증"""
    if recipient["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 대상자에 접근할 권한이 없습니다."
        )


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_recipient(
    data: RecipientCreate,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """대상자 생성"""
    user, supabase_db = _get_auth(authorization, supabase_auth)

    # is_default=True이면 기존 기본 대상자 해제
    if data.is_default:
        supabase_db.table("diary_recipients").update({"is_default": False}).eq("owner_id", user.id).eq("is_default", True).execute()

    result = supabase_db.table("diary_recipients").insert({
        "owner_id": user.id,
        "name": data.name,
        "birth_date": data.birth_date,
        "birth_time": data.birth_time,
        "gender": data.gender,
        "birth_place": data.birth_place,
        "role": data.role,
        "relationship": data.relationship,
        "notes": data.notes,
        "diary_period": data.diary_period,
        "is_default": data.is_default,
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="대상자 생성에 실패했습니다.")

    return result.data[0]


@router.get("")
async def list_recipients(
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """대상자 목록 조회"""
    user, supabase_db = _get_auth(authorization, supabase_auth)

    result = supabase_db.table("diary_recipients").select("*").eq("owner_id", user.id).order("created_at").execute()

    return result.data or []


@router.get("/{recipient_id}")
async def get_recipient(
    recipient_id: str,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """대상자 단건 조회"""
    user, supabase_db = _get_auth(authorization, supabase_auth)

    result = supabase_db.table("diary_recipients").select("*").eq("id", recipient_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="대상자를 찾을 수 없습니다.")

    _check_ownership(result.data[0], user.id)
    return result.data[0]


@router.put("/{recipient_id}")
async def update_recipient(
    recipient_id: str,
    data: RecipientUpdate,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """대상자 수정"""
    user, supabase_db = _get_auth(authorization, supabase_auth)

    # 존재 및 소유권 확인
    existing = supabase_db.table("diary_recipients").select("*").eq("id", recipient_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="대상자를 찾을 수 없습니다.")
    _check_ownership(existing.data[0], user.id)

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        return existing.data[0]

    # is_default=True로 변경 시 기존 기본 해제
    if update_data.get("is_default"):
        supabase_db.table("diary_recipients").update({"is_default": False}).eq("owner_id", user.id).eq("is_default", True).neq("id", recipient_id).execute()

    update_data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = supabase_db.table("diary_recipients").update(update_data).eq("id", recipient_id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="대상자 수정에 실패했습니다.")

    return result.data[0]


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipient(
    recipient_id: str,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """대상자 삭제"""
    user, supabase_db = _get_auth(authorization, supabase_auth)

    existing = supabase_db.table("diary_recipients").select("*").eq("id", recipient_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="대상자를 찾을 수 없습니다.")
    _check_ownership(existing.data[0], user.id)

    supabase_db.table("diary_recipients").delete().eq("id", recipient_id).execute()


@router.put("/{recipient_id}/default")
async def set_default_recipient(
    recipient_id: str,
    authorization: Optional[str] = Header(None),
    supabase_auth: Client = Depends(get_supabase),
):
    """기본 대상자 설정"""
    user, supabase_db = _get_auth(authorization, supabase_auth)

    existing = supabase_db.table("diary_recipients").select("*").eq("id", recipient_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="대상자를 찾을 수 없습니다.")
    _check_ownership(existing.data[0], user.id)

    # 기존 기본 해제 후 새 기본 설정
    supabase_db.table("diary_recipients").update({"is_default": False}).eq("owner_id", user.id).eq("is_default", True).execute()
    result = supabase_db.table("diary_recipients").update({"is_default": True}).eq("id", recipient_id).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="기본 대상자 설정에 실패했습니다.")

    return result.data[0]
