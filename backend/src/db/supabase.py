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

    @classmethod
    def get_client(cls) -> Client:
        """
        Supabase 클라이언트 인스턴스 반환

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


def get_supabase() -> Client:
    """
    의존성 주입용 Supabase 클라이언트 반환

    Usage (FastAPI):
        @app.get("/api/example")
        async def example(supabase: Client = Depends(get_supabase)):
            result = supabase.table("profiles").select("*").execute()
            return result.data
    """
    return SupabaseClient.get_client()
