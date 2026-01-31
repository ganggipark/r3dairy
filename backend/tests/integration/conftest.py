"""
Pytest fixtures for integration tests

Provides shared test setup for:
- Database sessions
- Sample data
- Mock clients
- API clients
"""

import pytest
from typing import Dict, Any, Generator
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
import json

# Sample survey responses for testing

EXAMPLE_STUDENT = {
    "name": "Lee Min-ji",
    "email": "minji@student.com",
    "birth_date": "2005-03-15",
    "birth_time": "09:30",
    "birth_location": "Seoul, South Korea",
    "gender": "Female",
    "role": "student",
    "personality_scores": [3, 4, 4, 4, 3, 4, 3, 3],  # Conscientious, open
    "interests": ["education", "personal_growth", "career"],
    "subscription_type": "app_only",
    "email_frequency": "weekly",
}

EXAMPLE_OFFICE_WORKER = {
    "name": "Park Ji-hoon",
    "email": "jihoon@company.com",
    "birth_date": "1988-07-22",
    "birth_time": "14:15",
    "birth_location": "Busan, South Korea",
    "gender": "Male",
    "role": "office_worker",
    "personality_scores": [3, 4, 3, 4, 2, 4, 3, 3],
    "interests": ["career", "finance", "personal_growth"],
    "subscription_type": "hybrid",
    "paper_size": "A5",
    "delivery_frequency": "monthly",
    "email_frequency": "weekly",
}

EXAMPLE_FREELANCER = {
    "name": "Choi Na-ri",
    "email": "nari@freelance.com",
    "birth_date": "1995-11-08",
    "birth_time": "18:45",
    "birth_location": "Incheon, South Korea",
    "gender": "Female",
    "role": "freelancer",
    "personality_scores": [4, 2, 4, 3, 2, 2, 4, 3],  # Creative, flexible
    "interests": ["creative", "career", "hobbies"],
    "subscription_type": "paper_only",
    "paper_size": "A4",
    "delivery_frequency": "monthly",
    "email_frequency": "none",
}

EXAMPLE_PARENT = {
    "name": "Kim Sung-hoon",
    "email": "sunghoon@family.com",
    "birth_date": "1982-01-14",
    "birth_time": "07:20",
    "birth_location": "Daegu, South Korea",
    "gender": "Male",
    "role": "parent",
    "personality_scores": [3, 4, 3, 4, 3, 4, 3, 3],
    "interests": ["family", "health", "personal_growth"],
    "subscription_type": "hybrid",
    "paper_size": "A5",
    "delivery_frequency": "monthly",
    "email_frequency": "weekly",
}

EXAMPLE_OTHER = {
    "name": "Yoon Ji-woo",
    "email": "jiwoo@example.com",
    "birth_date": "1999-09-30",
    "birth_time": "11:00",
    "birth_location": "Gwangju, South Korea",
    "gender": "Other",
    "role": "other",
    "personality_scores": [4, 3, 4, 4, 2, 3, 4, 3],
    "interests": ["hobbies", "creative", "personal_growth"],
    "subscription_type": "app_only",
    "email_frequency": "monthly",
}

EXAMPLE_KOREAN_RESPONSE = {
    "name": "김성훈",
    "email": "kim@example.com",
    "birth_date": "1990-05-15",
    "birth_time": "10:30",
    "birth_location": "서울, 대한민국",
    "gender": "남성",
    "role": "직장인",
    "personality_scores": [3, 4, 3, 4, 2, 4, 3, 3],
    "interests": ["커리어", "재무", "자기계발"],
    "subscription_type": "hybrid",
    "paper_size": "A5",
    "delivery_frequency": "monthly",
    "email_frequency": "weekly",
}

ALL_EXAMPLES = [
    EXAMPLE_STUDENT,
    EXAMPLE_OFFICE_WORKER,
    EXAMPLE_FREELANCER,
    EXAMPLE_PARENT,
    EXAMPLE_OTHER,
]


@pytest.fixture
def sample_survey_response() -> Dict[str, Any]:
    """Return sample survey response JSON"""
    return EXAMPLE_OFFICE_WORKER.copy()


@pytest.fixture
def sample_korean_response() -> Dict[str, Any]:
    """Return sample Korean survey response"""
    return EXAMPLE_KOREAN_RESPONSE.copy()


@pytest.fixture
def all_example_responses() -> list:
    """Return all 5 example responses"""
    return [example.copy() for example in ALL_EXAMPLES]


@pytest.fixture
def invalid_responses() -> Dict[str, Dict[str, Any]]:
    """Return various invalid responses for validation testing"""
    return {
        "duplicate_email": {
            **EXAMPLE_STUDENT,
            "email": "duplicate@example.com",
        },
        "invalid_email": {
            **EXAMPLE_STUDENT,
            "email": "not-an-email",
        },
        "future_birth_date": {
            **EXAMPLE_STUDENT,
            "birth_date": "2030-01-01",
        },
        "age_below_13": {
            **EXAMPLE_STUDENT,
            "birth_date": datetime.now().strftime("%Y-%m-%d"),
        },
        "missing_required_field": {
            **EXAMPLE_STUDENT,
            "name": None,
        },
        "invalid_likert_score": {
            **EXAMPLE_STUDENT,
            "personality_scores": [1, 2, 3, 4, 6, 3, 2, 1],  # 6 is invalid
        },
    }


@pytest.fixture
def mock_n8n_client():
    """Mock n8n API client (supports both sync and async)"""
    mock = MagicMock()

    # Return value for workflow creation
    workflow_result = {
        "id": "test-workflow-id",
        "name": "Test Survey Workflow",
        "webhook_url": "https://n8n.example.com/webhook/test-webhook-id",
        "active": True,
    }

    # Use AsyncMock for async methods
    mock.create_workflow = AsyncMock(return_value=workflow_result)
    mock.activate_workflow = AsyncMock(return_value=True)
    mock.test_webhook = AsyncMock(return_value={"success": True})

    return mock


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with full async chain support"""
    mock = MagicMock()

    # Create a chainable mock where every method returns itself
    # and .execute() is always an AsyncMock
    class ChainableMock(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.execute = AsyncMock(return_value=MagicMock(data=[]))

        def __getattr__(self, name):
            if name in ('execute',):
                return super().__getattr__(name)
            # For chained methods (select, insert, update, delete, eq, lt, lte, gte, gt, count, single, etc.)
            # return self so chaining works, but ensure execute is always AsyncMock
            attr = super().__getattr__(name)
            if callable(attr) and name not in ('assert_called', 'assert_called_once', 'assert_called_with',
                                                 'assert_called_once_with', 'assert_any_call', 'assert_not_called',
                                                 'reset_mock', 'called', 'call_count', 'call_args', 'call_args_list'):
                chain = ChainableMock()
                attr.return_value = chain
                return attr
            return attr

    table_chain = ChainableMock()
    mock.table = MagicMock(return_value=table_chain)

    return mock


@pytest.fixture
def data_processor():
    """Mock DataProcessor instance for testing"""
    class MockDataProcessor:
        def normalize_survey_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
            """Normalize survey response data"""
            # Simple passthrough normalization for testing
            normalized = response.copy()

            # Map Korean roles to English if needed
            role_mapping = {
                "직장인": "office_worker",
                "학생": "student",
                "프리랜서": "freelancer",
                "부모": "parent",
                "기타": "other",
            }
            if "role" in normalized and normalized["role"] in role_mapping:
                normalized["role"] = role_mapping[normalized["role"]]

            return normalized

        def validate_email(self, email: str) -> bool:
            """Validate email format"""
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                raise ValueError("Invalid email")
            return True

    return MockDataProcessor()


@pytest.fixture
async def api_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from src.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_n8n_workflow_config() -> Dict[str, Any]:
    """Sample n8n workflow configuration"""
    return {
        "name": "Test Survey Workflow",
        "nodes": [
            {
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "position": [250, 300],
                "parameters": {
                    "path": "test-survey",
                    "responseMode": "responseNode",
                    "httpMethod": "POST",
                }
            },
            {
                "name": "Data Processor",
                "type": "n8n-nodes-base.function",
                "position": [450, 300],
                "parameters": {
                    "functionCode": "// Normalize survey data\nreturn items;"
                }
            },
            {
                "name": "Store Response",
                "type": "n8n-nodes-base.supabase",
                "position": [650, 300],
                "parameters": {
                    "operation": "insert",
                    "table": "survey_responses",
                }
            }
        ],
        "connections": {
            "Webhook": {"main": [[{"node": "Data Processor", "type": "main", "index": 0}]]},
            "Data Processor": {"main": [[{"node": "Store Response", "type": "main", "index": 0}]]},
        }
    }


@pytest.fixture
def survey_template_default() -> Dict[str, Any]:
    """Default survey template"""
    return {
        "name": "Default Survey",
        "description": "Standard onboarding survey",
        "version": "1.0",
        "sections": [
            {
                "id": "basic_info",
                "title": "Basic Information",
                "fields": [
                    {"name": "name", "type": "text", "required": True},
                    {"name": "email", "type": "email", "required": True},
                    {"name": "birth_date", "type": "date", "required": True},
                ]
            },
            {
                "id": "preferences",
                "title": "Preferences",
                "fields": [
                    {"name": "role", "type": "select", "required": True},
                    {"name": "interests", "type": "multiselect", "required": True},
                ]
            }
        ]
    }


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database state before each test"""
    # This would connect to test database and clean tables
    # For now, using mock/in-memory approach
    yield
    # Cleanup after test
    pass


@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time

    class Timer:
        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, *args):
            self.end = time.time()
            self.elapsed = self.end - self.start

    return Timer
