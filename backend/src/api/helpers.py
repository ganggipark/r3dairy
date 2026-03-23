"""
공유 헬퍼 함수
콘텐츠 생성 파이프라인에서 공통으로 사용하는 유틸리티
"""
from fastapi import HTTPException, status
from supabase import Client
from typing import Optional


def get_birth_data(
    user_id: str,
    recipient_id: Optional[str],
    supabase_db: Client
) -> dict:
    """
    콘텐츠 생성을 위한 생년월일 데이터 조회.

    recipient_id가 제공되면 diary_recipients 테이블에서 조회 (소유권 검증 포함).
    recipient_id가 None이면 profiles 테이블에서 조회 (기존 동작).

    Args:
        user_id: 현재 인증된 사용자의 ID
        recipient_id: 대상자 UUID (None이면 본인 프로필 사용)
        supabase_db: RLS가 적용된 Supabase DB 클라이언트

    Returns:
        dict: name, birth_date, birth_time, gender, birth_place, role 키를 포함한 딕셔너리

    Raises:
        HTTPException 403: recipient_id가 현재 사용자 소유가 아닌 경우
        HTTPException 404: 프로필 또는 대상자가 존재하지 않는 경우
    """
    if recipient_id:
        # diary_recipients 테이블에서 조회
        result = supabase_db.table("diary_recipients").select("*").eq("id", recipient_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대상자를 찾을 수 없습니다."
            )

        recipient = result.data[0]

        # 소유권 검증 (RLS가 적용되어 있지만 명시적 확인)
        if recipient["owner_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 대상자에 접근할 권한이 없습니다."
            )

        return {
            "name": recipient["name"],
            "birth_date": recipient["birth_date"],
            "birth_time": recipient["birth_time"],
            "gender": recipient["gender"],
            "birth_place": recipient.get("birth_place", ""),
            "role": recipient.get("role", "office_worker"),
        }
    else:
        # profiles 테이블에서 조회 (기존 동작)
        result = supabase_db.table("profiles").select("*").eq("id", user_id).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로필이 존재하지 않습니다. 먼저 프로필을 생성해주세요."
            )

        profile = result.data[0]
        return {
            "name": profile["name"],
            "birth_date": profile["birth_date"],
            "birth_time": profile["birth_time"],
            "gender": profile["gender"],
            "birth_place": profile.get("birth_place", ""),
            "role": profile.get("roles", ["office_worker"])[0] if profile.get("roles") else "office_worker",
        }
