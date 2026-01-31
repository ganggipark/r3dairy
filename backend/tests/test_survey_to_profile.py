"""Tests for survey response to CustomerProfile conversion."""

import pytest
from datetime import date
from src.data_processor.survey_to_profile import SurveyResponseToProfile
from src.skills.personalization_engine.models import Role


class TestSurveyResponseToProfile:
    """Test suite for SurveyResponseToProfile converter."""

    def test_convert_student_profile_success(self):
        """Test converting a complete student survey response."""
        normalized_data = {
            "profile": {
                "name": "김학생",
                "email": "student@example.com",
                "birth_date": "2000-03-15",
                "gender": "female",
                "role": "student",
            },
            "personality": {
                "extroversion": 4,  # Likert 1-5
                "structured": 3,
                "openness": 5,
                "empathy": 4,
                "calm": 2,  # Low calm = high neuroticism
                "focus": 4,
                "creative": 5,  # High creative = low analytical
                "logical": 3,
            },
            "interests": {
                "topics": ["독서", "영화감상", "여행"],
                "tone_preference": "supportive",
            },
            "activities": {
                "study_type": ["시험 준비", "프로젝트"],
                "student_exercise_type": ["러닝", "요가"],
                "student_social_type": ["스터디그룹", "동아리"],
            },
            "format": {
                "diary_type": "hybrid",
            },
        }

        profile = SurveyResponseToProfile.convert(normalized_data)

        # Verify basic profile fields
        assert profile.name == "김학생"
        assert profile.id == "student_example_com"
        assert profile.birth_date == date(2000, 3, 15)
        assert profile.gender == "female"
        assert profile.primary_role == Role.STUDENT

        # Verify personality mapping (1-5 Likert → 0-100)
        # extroversion=4 → 75
        assert profile.personality.extraversion == 75
        # structured=3 → 50
        assert profile.personality.conscientiousness == 50
        # openness=5 → 100
        assert profile.personality.openness == 100
        # empathy=4 → 75
        assert profile.personality.agreeableness == 75
        # calm=2 → (reversed) 100-25=75 neuroticism
        assert profile.personality.neuroticism == 75
        # creative=5 → (reversed) 100-100=0 analytical
        assert profile.personality.analytical_vs_intuitive == 0

        # Verify interests
        assert "독서" in profile.interests.primary_interests
        assert "영화감상" in profile.interests.primary_interests

        # Verify activity preferences
        assert "study" in profile.activity_preferences
        assert "시험 준비" in profile.activity_preferences["study"]
        assert "exercise" in profile.activity_preferences
        assert "러닝" in profile.activity_preferences["exercise"]
        assert "social" in profile.activity_preferences
        assert "스터디그룹" in profile.activity_preferences["social"]

    def test_convert_office_worker_profile_success(self):
        """Test converting an office worker survey response."""
        normalized_data = {
            "profile": {
                "name": "박직장",
                "email": "worker@company.com",
                "birth_date": "1990-07-22",
                "gender": "male",
                "role": "office_worker",
            },
            "personality": {
                "extroversion": 3,
                "structured": 5,
                "openness": 3,
                "empathy": 3,
                "calm": 4,
                "focus": 5,
                "creative": 2,
                "logical": 5,
            },
            "interests": {
                "topics": ["자기계발", "운동", "독서"],
            },
            "activities": {
                "work_type": ["보고서/기획", "회의/소통"],
                "worker_exercise_type": ["헬스", "등산"],
                "worker_social_type": ["팀빌딩", "네트워킹"],
            },
        }

        profile = SurveyResponseToProfile.convert(normalized_data)

        assert profile.primary_role == Role.OFFICE_WORKER
        assert "work" in profile.activity_preferences
        assert "보고서/기획" in profile.activity_preferences["work"]
        assert "exercise" in profile.activity_preferences
        assert "헬스" in profile.activity_preferences["exercise"]

    def test_convert_freelancer_profile_success(self):
        """Test converting a freelancer survey response."""
        normalized_data = {
            "profile": {
                "name": "이프리",
                "email": "freelancer@work.com",
                "birth_date": "1988-11-05",
                "gender": "other",
                "role": "freelancer",
            },
            "personality": {
                "extroversion": 2,
                "structured": 2,
                "openness": 5,
                "empathy": 4,
                "calm": 3,
                "focus": 3,
                "creative": 5,
                "logical": 4,
            },
            "interests": {
                "topics": ["디자인", "창작", "기술"],
            },
            "activities": {
                "freelance_work_type": ["창작/디자인", "기획/제안"],
                "freelancer_exercise_type": ["요가", "자전거"],
                "freelancer_social_type": ["콜라보", "커뮤니티"],
            },
        }

        profile = SurveyResponseToProfile.convert(normalized_data)

        assert profile.primary_role == Role.FREELANCER
        assert "work" in profile.activity_preferences
        assert "창작/디자인" in profile.activity_preferences["work"]

    def test_missing_required_field_name_raises_error(self):
        """Test that missing name field raises ValueError."""
        normalized_data = {
            "profile": {
                "email": "test@example.com",
                "birth_date": "2000-01-01",
                "role": "student",
            },
            "personality": {},
            "interests": {},
            "activities": {},
        }

        with pytest.raises(ValueError, match="Missing required field: 'name'"):
            SurveyResponseToProfile.convert(normalized_data)

    def test_missing_required_field_birth_date_raises_error(self):
        """Test that missing birth_date field raises ValueError."""
        normalized_data = {
            "profile": {
                "name": "Test User",
                "email": "test@example.com",
                "role": "student",
            },
            "personality": {},
            "interests": {},
            "activities": {},
        }

        with pytest.raises(ValueError, match="Missing required field: 'birth_date'"):
            SurveyResponseToProfile.convert(normalized_data)

    def test_invalid_birth_date_format_raises_error(self):
        """Test that invalid birth_date format raises ValueError."""
        normalized_data = {
            "profile": {
                "name": "Test User",
                "email": "test@example.com",
                "birth_date": "invalid-date",
                "role": "student",
            },
            "personality": {},
            "interests": {},
            "activities": {},
        }

        with pytest.raises(ValueError, match="Invalid birth_date format"):
            SurveyResponseToProfile.convert(normalized_data)

    def test_parse_birth_date_iso_format(self):
        """Test parsing ISO format date (YYYY-MM-DD)."""
        result = SurveyResponseToProfile._parse_birth_date("1995-06-15")
        assert result == date(1995, 6, 15)

    def test_parse_birth_date_us_format(self):
        """Test parsing US format date (MM/DD/YYYY)."""
        result = SurveyResponseToProfile._parse_birth_date("06/15/1995")
        assert result == date(1995, 6, 15)

    def test_parse_birth_date_eu_format(self):
        """Test parsing EU format date (DD/MM/YYYY)."""
        result = SurveyResponseToProfile._parse_birth_date("15/06/1995")
        assert result == date(1995, 6, 15)

    def test_map_personality_likert_scale_conversion(self):
        """Test Likert 1-5 to 0-100 scale conversion."""
        scores = {
            "extroversion": 1,  # 1 → 0
            "structured": 2,    # 2 → 25
            "openness": 3,      # 3 → 50
            "empathy": 4,       # 4 → 75
            "calm": 5,          # 5 → (reversed) 0
            "focus": 3,
            "creative": 1,      # 1 → (reversed) 100
            "logical": 5,
        }

        personality = SurveyResponseToProfile._map_personality(scores)

        assert personality.extraversion == 0
        assert personality.conscientiousness == 25
        assert personality.openness == 50
        assert personality.agreeableness == 75
        assert personality.neuroticism == 0  # Reversed from calm=5
        assert personality.analytical_vs_intuitive == 100  # Reversed from creative=1

    def test_map_personality_default_neutral_for_missing_scores(self):
        """Test that missing personality scores default to neutral (50)."""
        scores = {}  # Empty scores

        personality = SurveyResponseToProfile._map_personality(scores)

        # All should default to 50 (neutral)
        assert personality.extraversion == 50
        assert personality.conscientiousness == 50
        assert personality.openness == 50

    def test_map_role_valid_roles(self):
        """Test role mapping for valid role strings."""
        assert SurveyResponseToProfile._map_role("student") == Role.STUDENT
        assert SurveyResponseToProfile._map_role("office_worker") == Role.OFFICE_WORKER
        assert SurveyResponseToProfile._map_role("freelancer") == Role.FREELANCER
        assert SurveyResponseToProfile._map_role("STUDENT") == Role.STUDENT  # Case insensitive
        assert SurveyResponseToProfile._map_role(" student ") == Role.STUDENT  # Whitespace trimmed

    def test_map_role_invalid_role_raises_error(self):
        """Test that invalid role raises ValueError."""
        with pytest.raises(ValueError, match="Unknown role: invalid_role"):
            SurveyResponseToProfile._map_role("invalid_role")

    def test_extract_activity_preferences_student(self):
        """Test extracting student activity preferences."""
        activities = {
            "study_type": ["시험 준비", "프로젝트"],
            "student_exercise_type": ["러닝"],
            "student_social_type": ["스터디그룹"],
        }

        result = SurveyResponseToProfile._extract_activity_preferences(activities, "student")

        assert result["study"] == ["시험 준비", "프로젝트"]
        assert result["exercise"] == ["러닝"]
        assert result["social"] == ["스터디그룹"]

    def test_extract_activity_preferences_office_worker(self):
        """Test extracting office worker activity preferences."""
        activities = {
            "work_type": ["보고서/기획"],
            "worker_exercise_type": ["헬스", "등산"],
            "worker_social_type": ["팀빌딩"],
        }

        result = SurveyResponseToProfile._extract_activity_preferences(activities, "office_worker")

        assert result["work"] == ["보고서/기획"]
        assert result["exercise"] == ["헬스", "등산"]
        assert result["social"] == ["팀빌딩"]

    def test_extract_activity_preferences_handles_single_string(self):
        """Test that single string values are converted to list."""
        activities = {
            "study_type": "시험 준비",  # String instead of list
        }

        result = SurveyResponseToProfile._extract_activity_preferences(activities, "student")

        assert result["study"] == ["시험 준비"]

    def test_extract_activity_preferences_empty_for_unknown_role(self):
        """Test that unknown role returns empty preferences."""
        activities = {
            "work_type": ["보고서/기획"],
        }

        result = SurveyResponseToProfile._extract_activity_preferences(activities, "unknown_role")

        assert result == {}

    def test_map_interests_with_topics_and_activities(self):
        """Test mapping interests from topics and activities."""
        topics = ["독서", "영화"]
        activities = {
            "study_type": ["시험 준비", "프로젝트"],
            "exercise_type": ["러닝"],
        }

        interests = SurveyResponseToProfile._map_interests(topics, activities)

        assert interests.primary_interests == ["독서", "영화"]
        assert "시험 준비" in interests.secondary_interests
        assert "프로젝트" in interests.secondary_interests
        assert "러닝" in interests.secondary_interests

    def test_map_interests_empty_topics(self):
        """Test mapping interests with no topics."""
        topics = []
        activities = {
            "study_type": ["시험 준비"],
        }

        interests = SurveyResponseToProfile._map_interests(topics, activities)

        assert interests.primary_interests == []
        assert "시험 준비" in interests.secondary_interests

    def test_map_interests_limits_secondary_to_10(self):
        """Test that secondary interests are limited to 10."""
        topics = ["독서"]
        activities = {
            "many_activities": [f"activity_{i}" for i in range(20)],
        }

        interests = SurveyResponseToProfile._map_interests(topics, activities)

        assert len(interests.secondary_interests) == 10

    def test_convert_profile_without_activities(self):
        """Test converting profile when activities section is empty."""
        normalized_data = {
            "profile": {
                "name": "최미니",
                "email": "minimal@example.com",
                "birth_date": "1995-01-01",
                "gender": "female",
                "role": "student",
            },
            "personality": {
                "extroversion": 3,
                "structured": 3,
                "openness": 3,
                "empathy": 3,
                "calm": 3,
                "focus": 3,
                "creative": 3,
                "logical": 3,
            },
            "interests": {
                "topics": ["독서"],
            },
            "activities": {},  # Empty activities
        }

        profile = SurveyResponseToProfile.convert(normalized_data)

        assert profile.name == "최미니"
        assert profile.activity_preferences == {}

    def test_convert_uses_name_for_id_when_no_email(self):
        """Test that profile ID is generated from name when email is missing."""
        normalized_data = {
            "profile": {
                "name": "Kim Test User",
                "birth_date": "2000-01-01",
                "role": "student",
            },
            "personality": {},
            "interests": {},
            "activities": {},
        }

        profile = SurveyResponseToProfile.convert(normalized_data)

        assert profile.id == "kim_test_user"

    def test_convert_defaults_to_office_worker_for_invalid_role(self):
        """Test that invalid role defaults to OFFICE_WORKER."""
        normalized_data = {
            "profile": {
                "name": "Test User",
                "email": "test@example.com",
                "birth_date": "2000-01-01",
                "role": "invalid_role",
            },
            "personality": {},
            "interests": {},
            "activities": {},
        }

        profile = SurveyResponseToProfile.convert(normalized_data)

        # Should default to OFFICE_WORKER instead of raising error
        assert profile.primary_role == Role.OFFICE_WORKER
