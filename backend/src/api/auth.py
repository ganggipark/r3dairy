"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from src.db.supabase import get_supabase
from src.api.models import SignUpRequest, LoginRequest, AuthResponse, ErrorResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignUpRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    회원가입

    Args:
        request: 회원가입 정보 (email, password, name)

    Returns:
        AuthResponse: 액세스 토큰, 리프레시 토큰, 사용자 ID

    Raises:
        HTTPException 400: 이미 존재하는 이메일
        HTTPException 500: 서버 오류
    """
    try:
        # Supabase Auth를 통한 회원가입
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name
                }
            }
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="회원가입에 실패했습니다. 이미 존재하는 이메일일 수 있습니다."
            )

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id,
            email=response.user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    로그인

    Args:
        request: 로그인 정보 (email, password)

    Returns:
        AuthResponse: 액세스 토큰, 리프레시 토큰, 사용자 ID

    Raises:
        HTTPException 401: 인증 실패 (잘못된 이메일/비밀번호)
        HTTPException 500: 서버 오류
    """
    try:
        # Supabase Auth를 통한 로그인
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id,
            email=response.user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/logout")
async def logout(supabase: Client = Depends(get_supabase)):
    """
    로그아웃

    Returns:
        성공 메시지

    Note:
        클라이언트는 액세스 토큰을 삭제해야 합니다.
    """
    try:
        supabase.auth.sign_out()
        return {"success": True, "message": "로그아웃되었습니다."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그아웃 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str,
    supabase: Client = Depends(get_supabase)
):
    """
    토큰 갱신

    Args:
        refresh_token: 리프레시 토큰

    Returns:
        AuthResponse: 새로운 액세스 토큰, 리프레시 토큰

    Raises:
        HTTPException 401: 유효하지 않은 리프레시 토큰
        HTTPException 500: 서버 오류
    """
    try:
        response = supabase.auth.refresh_session(refresh_token)

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다."
            )

        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user_id=response.user.id,
            email=response.user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 갱신 중 오류가 발생했습니다: {str(e)}"
        )


def get_current_user(
    authorization: str,
    supabase: Client = Depends(get_supabase)
) -> dict:
    """
    현재 사용자 가져오기 (의존성 주입용)

    Args:
        authorization: Authorization 헤더 (Bearer {access_token})
        supabase: Supabase 클라이언트

    Returns:
        사용자 정보 dict

    Raises:
        HTTPException 401: 인증되지 않은 요청
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다."
        )

    token = authorization.split(" ")[1]

    try:
        user = supabase.auth.get_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다."
            )
        return user.user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다."
        )
