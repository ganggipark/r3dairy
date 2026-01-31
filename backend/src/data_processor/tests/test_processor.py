"""Tests for DataProcessor orchestrator."""

import pytest
from unittest.mock import MagicMock, AsyncMock

from ..processor import DataProcessor


@pytest.fixture
def processor():
    return DataProcessor()


@pytest.fixture
def valid_survey():
    return {
        "name": "Kim Sung-hoon",
        "email": "kim@example.com",
        "birth_date": "1990-05-15",
        "gender": "Male",
        "role": "office_worker",
        "personality_scores": [4, 3, 4, 4, 2, 4, 3, 3],
        "interests": ["career", "personal_growth", "health"],
        "subscription_type": "hybrid",
        "paper_size": "A5",
        "delivery_frequency": "monthly",
        "email_frequency": "weekly",
        "consent_privacy": True,
        "consent_marketing": False,
    }


@pytest.fixture
def invalid_survey():
    return {
        "name": "",
        "email": "not-an-email",
        "birth_date": "2020-01-01",
        "gender": "Male",
    }


class TestProcessSurveyResponse:
    @pytest.mark.asyncio
    async def test_valid_survey(self, processor, valid_survey):
        success, profile, errors = await processor.process_survey_response(valid_survey)
        assert success is True
        assert profile is not None
        assert profile.name == "Kim Sung-hoon"
        assert profile.age > 0
        assert profile.zodiac_sign == "Taurus"
        assert profile.preferences.preferred_tone in {
            "analytical", "formal", "casual", "supportive"
        }

    @pytest.mark.asyncio
    async def test_invalid_survey_fails_validation(self, processor, invalid_survey):
        success, profile, errors = await processor.process_survey_response(invalid_survey)
        assert success is False
        assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_minimal_survey(self, processor):
        raw = {
            "name": "Test",
            "email": "test@example.com",
            "birth_date": "2000-06-15",
            "gender": "Other",
            "consent_privacy": True,
            "interests": ["health"],
        }
        success, profile, errors = await processor.process_survey_response(raw)
        assert success is True
        assert profile.primary_role.value == "other"


class TestCreateCustomerInDb:
    @pytest.mark.asyncio
    async def test_creates_records(self, processor, valid_survey):
        success, profile, _ = await processor.process_survey_response(valid_survey)
        assert success

        # Mock Supabase client
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
        mock_table.insert.return_value.execute.return_value = MagicMock(data=[{"id": "123"}])
        mock_client.table.return_value = mock_table

        customer_id = await processor.create_customer_in_db(profile, mock_client)
        assert customer_id is not None

        # Verify 4 tables were written to
        assert mock_client.table.call_count == 5  # 1 select + 4 inserts

    @pytest.mark.asyncio
    async def test_duplicate_email_rejected(self, processor, valid_survey):
        success, profile, _ = await processor.process_survey_response(valid_survey)

        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[{"id": "existing"}]
        )
        mock_client.table.return_value = mock_table

        with pytest.raises(ValueError, match="already exists"):
            await processor.create_customer_in_db(profile, mock_client)
