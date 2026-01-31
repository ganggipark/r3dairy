"""
Supabase Client Configuration
"""
import os
from typing import Optional
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
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

            # Avoid confusing Supabase 401s when the service key is left as a placeholder.
            if service_key and service_key.strip() in {"your-service-role-key-here", "YOUR_SERVICE_ROLE_KEY_HERE"}:
                raise ValueError(
                    "SUPABASE_SERVICE_ROLE_KEY is still a placeholder. Set a real service_role key in backend/.env "
                    "(Supabase Dashboard -> Project Settings -> API -> service_role key)."
                )

            if not url or not service_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables"
                )

            cls._service_instance = create_client(url, service_key)

        return cls._service_instance

    @staticmethod
    def create_user_db_client(access_token: str) -> Client:
        """Create a Supabase client scoped to a user's JWT for PostgREST/RLS.

        This avoids requiring a service_role key for local development and keeps RLS intact.
        """
        url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_KEY")

        if not url or not anon_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )

        if not access_token:
            raise ValueError("access_token is required")

        options = SyncClientOptions(
            headers={"Authorization": f"Bearer {access_token}"},
            auto_refresh_token=False,
            persist_session=False,
        )
        return create_client(url, anon_key, options)


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


# Alias for backward compatibility
get_supabase_client = get_supabase


# ============================================================================
# Survey Configuration Operations
# ============================================================================

async def save_survey_config(config: dict) -> dict:
    """
    Save survey configuration to Supabase.

    Args:
        config: Survey configuration dict with id, name, description, form_json, status, etc.

    Returns:
        Saved survey configuration

    Raises:
        Exception: If save operation fails
    """
    client = get_supabase_service()

    # Prepare data for insert/upsert
    data = {
        "id": config.get("id"),
        "name": config.get("name"),
        "description": config.get("description", ""),
        "form_json": config.get("form_json"),
        "status": config.get("status", "draft"),
        "deployed_to": config.get("deployed_to", {"n8n": False, "google_forms": False, "web": False}),
        "response_count": config.get("response_count", 0),
        "metadata": config.get("metadata", {}),
    }

    # Upsert (insert or update)
    result = client.table("survey_configurations").upsert(data).execute()

    if not result.data:
        raise Exception("Failed to save survey configuration")

    return result.data[0]


async def get_survey_config(survey_id: str) -> Optional[dict]:
    """
    Get survey configuration from Supabase.

    Args:
        survey_id: Survey ID

    Returns:
        Survey configuration dict or None if not found
    """
    client = get_supabase_service()

    result = client.table("survey_configurations").select("*").eq("id", survey_id).execute()

    if not result.data:
        return None

    return result.data[0]


async def list_survey_configs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> list:
    """
    List survey configurations with optional filtering.

    Args:
        status: Filter by status (draft, active, archived)
        limit: Maximum number of surveys to return
        offset: Number of surveys to skip

    Returns:
        List of survey configurations
    """
    client = get_supabase_service()

    query = client.table("survey_configurations").select("*")

    if status:
        query = query.eq("status", status)

    query = query.range(offset, offset + limit - 1).order("created_at", desc=True)

    result = query.execute()

    return result.data


async def update_survey_status(survey_id: str, status: str) -> dict:
    """
    Update survey status.

    Args:
        survey_id: Survey ID
        status: New status (draft, active, archived)

    Returns:
        Updated survey configuration

    Raises:
        Exception: If update operation fails
    """
    client = get_supabase_service()

    result = client.table("survey_configurations").update({"status": status}).eq("id", survey_id).execute()

    if not result.data:
        raise Exception("Failed to update survey status")

    return result.data[0]


async def update_survey_deployment(survey_id: str, deployed_to: dict) -> dict:
    """
    Update survey deployment status.

    Args:
        survey_id: Survey ID
        deployed_to: Deployment status dict (e.g., {"n8n": True, "web": False})

    Returns:
        Updated survey configuration

    Raises:
        Exception: If update operation fails
    """
    client = get_supabase_service()

    result = client.table("survey_configurations").update({"deployed_to": deployed_to}).eq("id", survey_id).execute()

    if not result.data:
        raise Exception("Failed to update survey deployment")

    return result.data[0]


# ============================================================================
# Survey Response Operations
# ============================================================================

async def save_survey_response(response: dict) -> dict:
    """
    Save survey response to Supabase.

    Args:
        response: Survey response dict with id, survey_id, response_data, normalized_data, etc.

    Returns:
        Saved survey response

    Raises:
        Exception: If save operation fails
    """
    client = get_supabase_service()

    # Prepare data for insert
    data = {
        "id": response.get("id"),
        "survey_id": response.get("survey_id"),
        "response_data": response.get("response_data"),
        "normalized_data": response.get("normalized_data"),
        "ip_address": response.get("ip_address"),
        "source": response.get("source", "web"),
        "user_id": response.get("user_id"),
        "metadata": response.get("metadata", {}),
    }

    # Insert response (triggers response_count increment via DB trigger)
    result = client.table("survey_responses").insert(data).execute()

    if not result.data:
        raise Exception("Failed to save survey response")

    return result.data[0]


async def list_survey_responses(
    survey_id: str,
    limit: int = 100,
    offset: int = 0,
    source: Optional[str] = None
) -> dict:
    """
    List survey responses with pagination.

    Args:
        survey_id: Survey ID
        limit: Maximum number of responses to return
        offset: Number of responses to skip
        source: Filter by response source (n8n, google_forms, web, api)

    Returns:
        Dict with total count and list of responses
    """
    client = get_supabase_service()

    # Query for responses
    query = client.table("survey_responses").select("*", count="exact").eq("survey_id", survey_id)

    if source:
        query = query.eq("source", source)

    query = query.range(offset, offset + limit - 1).order("submitted_at", desc=True)

    result = query.execute()

    return {
        "total": result.count if result.count is not None else len(result.data),
        "responses": result.data
    }


async def get_survey_response_summary(survey_id: str) -> dict:
    """
    Get summary statistics for a survey.

    Args:
        survey_id: Survey ID

    Returns:
        Summary statistics dict
    """
    client = get_supabase_service()

    # Get all responses (could optimize with aggregation queries)
    result = client.table("survey_responses").select("source, submitted_at").eq("survey_id", survey_id).execute()

    responses = result.data
    total_responses = len(responses)

    # Count by source
    responses_by_source = {}
    for r in responses:
        source = r.get("source", "web")
        responses_by_source[source] = responses_by_source.get(source, 0) + 1

    # Count by date
    responses_by_date = {}
    for r in responses:
        if "submitted_at" in r:
            # Extract date from timestamp
            date_key = r["submitted_at"][:10]  # ISO format YYYY-MM-DD
            responses_by_date[date_key] = responses_by_date.get(date_key, 0) + 1

    return {
        "survey_id": survey_id,
        "total_responses": total_responses,
        "responses_by_source": responses_by_source,
        "responses_by_date": responses_by_date,
    }


# ============================================================================
# Customer Profile Operations
# ============================================================================

async def save_customer_profile(profile: dict) -> dict:
    """
    Save customer profile to Supabase.

    Args:
        profile: CustomerProfile dict with id, name, birth_date, etc.

    Returns:
        Saved customer profile

    Raises:
        Exception: If save operation fails
    """
    client = get_supabase_service()

    # Prepare data for insert/upsert
    # Convert date objects to ISO strings
    data = {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "birth_date": profile.get("birth_date").isoformat() if hasattr(profile.get("birth_date"), "isoformat") else profile.get("birth_date"),
        "birth_time": profile.get("birth_time"),
        "gender": profile.get("gender", "other"),
        "birth_place": profile.get("birth_place", ""),
        "primary_role": profile.get("primary_role"),
        "personality": profile.get("personality", {}),
        "interests": profile.get("interests", {}),
        "activity_preferences": profile.get("activity_preferences", {}),
    }

    # Upsert (insert or update based on id)
    result = client.table("profiles").upsert(data).execute()

    if not result.data:
        raise Exception("Failed to save customer profile")

    return result.data[0]


async def get_customer_profile(profile_id: str) -> Optional[dict]:
    """
    Get customer profile from Supabase.

    Args:
        profile_id: Profile ID

    Returns:
        Customer profile dict or None if not found
    """
    client = get_supabase_service()

    result = client.table("profiles").select("*").eq("id", profile_id).execute()

    if not result.data:
        return None

    return result.data[0]
