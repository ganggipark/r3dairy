"""
Pytest Configuration and Fixtures
공통 테스트 설정 및 픽스처
"""
import pytest
import os
from datetime import date, time
from typing import Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# 환경변수 설정 (테스트용)
os.environ["ENVIRONMENT"] = "test"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """테스트 설정"""
    return {
        "environment": "test",
        "supabase_url": "https://test.supabase.co",
        "supabase_key": "test-key",
    }


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase 클라이언트"""
    mock_client = MagicMock()

    # Mock auth
    mock_client.auth.sign_up.return_value = {
        "user": {"id": "test-user-id", "email": "test@example.com"}
    }
    mock_client.auth.sign_in_with_password.return_value = {
        "user": {"id": "test-user-id", "email": "test@example.com"},
        "session": {"access_token": "test-token"}
    }
    mock_client.auth.get_user.return_value = {
        "id": "test-user-id",
        "email": "test@example.com"
    }

    # Mock table queries
    mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": "test-user-id",
        "name": "테스트",
        "birth_date": "1990-01-15",
        "birth_time": "14:30:00",
        "gender": "male",
        "birth_place": "서울",
        "roles": ["student"]
    }

    return mock_client


@pytest.fixture
def sample_birth_info():
    """샘플 출생 정보"""
    from src.rhythm.models import BirthInfo, Gender

    return BirthInfo(
        name="테스트",
        birth_date=date(1990, 1, 15),
        birth_time=time(14, 30),
        gender=Gender.MALE,
        birth_place="서울",
        birth_place_lat=37.5665,
        birth_place_lng=126.9780
    )


@pytest.fixture
def sample_rhythm_signal():
    """샘플 리듬 신호"""
    from src.rhythm.models import RhythmSignal

    return RhythmSignal(
        date=date(2026, 1, 20),
        saju_data={"test": "data"},
        energy_level=3,
        focus_capacity=4,
        social_energy=3,
        decision_clarity=4,
        favorable_times=["오전 9-11시", "오후 2-4시"],
        caution_times=["오후 5-7시"],
        favorable_directions=["북동", "남서"],
        main_theme="안정과 정리",
        opportunities=["학습", "관계 강화"],
        challenges=["충동 조절"]
    )


@pytest.fixture
def sample_daily_content():
    """샘플 일간 콘텐츠"""
    from src.content.models import (
        DailyContent,
        FocusCaution,
        ActionGuide,
        TimeDirection,
        StateTrigger
    )

    return DailyContent(
        date=date(2026, 1, 20),
        summary="오늘은 안정적인 에너지가 있는 날입니다. 정리와 마무리에 집중하면 좋습니다.",
        keywords=["안정", "정리", "마무리"],
        rhythm_description=(
            "오늘의 리듬은 차분하고 안정적입니다. 에너지가 내부로 향하며, "
            "외부 활동보다는 내면 정리와 기존 작업 완성에 적합한 흐름입니다. "
            "급하게 새로운 일을 시작하기보다는 지금까지 해온 일들을 점검하고 "
            "마무리하는 시간으로 활용하면 좋습니다. 차분함이 주는 집중력을 활용하여 "
            "미뤄둔 정리 작업이나 세부 사항 점검에 시간을 할애하세요."
        ),
        focus_caution=FocusCaution(
            focus=["정리", "마무리", "성찰"],
            caution=["새로운 시작", "큰 결정"]
        ),
        action_guide=ActionGuide(
            do=["할 일 정리", "공간 정리", "마무리"],
            avoid=["충동 구매", "중요한 계약"]
        ),
        time_direction=TimeDirection(
            good_time="오전 9-11시, 오후 2-4시",
            avoid_time="오후 5-7시",
            good_direction="북동쪽",
            avoid_direction="남서쪽",
            notes="집중이 필요한 작업은 오전 시간대에 하세요"
        ),
        state_trigger=StateTrigger(
            gesture="양손을 가슴에 모으고 천천히 호흡",
            phrase="지금 이 순간, 나는 충분히 잘하고 있다",
            how_to="불안감이 올라올 때 3번 반복하세요"
        ),
        meaning_shift=(
            "오늘의 차분한 에너지는 '무기력'이 아니라 '내면 충전'의 시간입니다. "
            "급하지 않게 한 걸음씩 나아가는 것이 오늘의 지혜입니다."
        ),
        rhythm_question="오늘 마무리하고 싶은 일은 무엇인가요? 그것을 완성하면 어떤 기분이 들까요?"
    )


@pytest.fixture
def api_client(mock_supabase_client):
    """FastAPI 테스트 클라이언트"""
    from src.main import app
    from src.db.supabase import get_supabase_client

    # Supabase 클라이언트 오버라이드
    app.dependency_overrides[get_supabase_client] = lambda: mock_supabase_client

    client = TestClient(app)

    yield client

    # 클린업
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """인증 헤더"""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def sample_profile_data():
    """샘플 프로필 데이터"""
    return {
        "name": "테스트 사용자",
        "birth_date": "1990-01-15",
        "birth_time": "14:30:00",
        "gender": "male",
        "birth_place": "서울",
        "birth_place_lat": 37.5665,
        "birth_place_lng": 126.9780,
        "roles": ["student"],
        "preferences": {
            "interests": ["학습", "성장"],
            "rhythm_type": "detailed",
            "record_style": "structured"
        }
    }


# 테스트 시작/종료 훅
def pytest_configure(config):
    """pytest 시작 시 설정"""
    print("\n" + "="*80)
    print("R³ Diary System - Test Suite Starting")
    print("="*80)


def pytest_sessionfinish(session, exitstatus):
    """pytest 종료 시 정리"""
    print("\n" + "="*80)
    print(f"Test Suite Finished - Exit Status: {exitstatus}")
    print("="*80)
