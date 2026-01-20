"""
Supabase Client Configuration
"""
import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseClient:
    """Supabase 클라이언트 싱글톤"""

    _instance: Optional[Client] = None
    _service_instance: Optional[Client] = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Supabase 클라이언트 인스턴스 반환 (Anon Key - Auth 전용)

        Returns:
            Supabase Client 인스턴스

        Raises:
            ValueError: SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않은 경우
        """
        if cls._instance is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")

            if not url or not key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
                )

            cls._instance = create_client(url, key)

        return cls._instance

    @classmethod
    def get_service_client(cls) -> Client:
        """
        Supabase Service Role 클라이언트 인스턴스 반환 (RLS 우회)

        Returns:
            Supabase Service Role Client 인스턴스

        Raises:
            ValueError: SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY가 설정되지 않은 경우
        """
        if cls._service_instance is None:
            url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

            if not url or not service_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables"
                )

            cls._service_instance = create_client(url, service_key)

        return cls._service_instance


def get_supabase() -> Client:
    """
    의존성 주입용 Supabase 클라이언트 반환 (Anon Key - Auth 전용)

    Usage (FastAPI):
        @app.get("/api/auth/login")
        async def login(supabase: Client = Depends(get_supabase)):
            response = supabase.auth.sign_in_with_password(...)
            return response
    """
    return SupabaseClient.get_client()


def get_supabase_service() -> Client:
    """
    의존성 주입용 Supabase Service Role 클라이언트 반환 (DB 작업용)

    Usage (FastAPI):
        @app.get("/api/profile")
        async def get_profile(supabase: Client = Depends(get_supabase_service)):
            result = supabase.table("profiles").select("*").execute()
            return result.data
    """
    return SupabaseClient.get_service_client()
