"""Survey Response to CustomerProfile conversion pipeline."""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from ..skills.personalization_engine.models import (
    CustomerProfile,
    PersonalityProfile,
    InterestsProfile,
    Role,
)


class SurveyResponseToProfile:
    """Convert survey response data to CustomerProfile."""

    @staticmethod
    def convert(normalized_data: Dict[str, Any]) -> CustomerProfile:
        """
        Convert normalized survey response to CustomerProfile.

        Args:
            normalized_data: Normalized survey response with structure:
                {
                    "profile": {"name", "email", "birth_date", "gender", "role"},
                    "personality": {"extroversion", "structured", ...},
                    "interests": {"topics", "tone_preference"},
                    "activities": {"study_type", "work_type", ...},
                    "format": {...},
                    "communication": {...},
                }

        Returns:
            CustomerProfile instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required sections
        if "profile" not in normalized_data:
            raise ValueError("Missing 'profile' section in normalized data")

        profile_data = normalized_data.get("profile", {})
        personality_data = normalized_data.get("personality", {})
        interests_data = normalized_data.get("interests", {})
        activities_data = normalized_data.get("activities", {})

        # Extract profile fields
        name = profile_data.get("name", "")
        if not name:
            raise ValueError("Missing required field: 'name'")

        birth_date_str = profile_data.get("birth_date")
        if not birth_date_str:
            raise ValueError("Missing required field: 'birth_date'")

        # Parse birth date
        try:
            birth_date = SurveyResponseToProfile._parse_birth_date(birth_date_str)
        except Exception as e:
            raise ValueError(f"Invalid birth_date format: {birth_date_str}. Error: {e}")

        gender = profile_data.get("gender", "other")
        role_str = profile_data.get("role", "office_worker")

        # Map personality
        personality_profile = SurveyResponseToProfile._map_personality(personality_data)

        # Map interests
        interests_profile = SurveyResponseToProfile._map_interests(
            interests_data.get("topics", []),
            activities_data
        )

        # Map role
        try:
            primary_role = SurveyResponseToProfile._map_role(role_str)
        except ValueError:
            # Fallback to OFFICE_WORKER if role mapping fails
            primary_role = Role.OFFICE_WORKER

        # Extract activity preferences
        activity_preferences = SurveyResponseToProfile._extract_activity_preferences(
            activities_data,
            role_str
        )

        # Generate profile ID from email or name
        profile_id = profile_data.get("email", "").replace("@", "_").replace(".", "_")
        if not profile_id:
            profile_id = name.replace(" ", "_").lower()

        # Build CustomerProfile
        return CustomerProfile(
            id=profile_id,
            name=name,
            birth_date=birth_date,
            birth_time=None,  # Not collected in survey
            gender=gender,
            birth_place="",  # Not collected in survey
            primary_role=primary_role,
            personality=personality_profile,
            interests=interests_profile,
            activity_preferences=activity_preferences,
        )

    @staticmethod
    def _parse_birth_date(birth_date_str: str) -> date:
        """
        Parse birth date string to date object.

        Supports formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY

        Args:
            birth_date_str: Birth date string

        Returns:
            date object

        Raises:
            ValueError: If format is invalid
        """
        # Try ISO format first (YYYY-MM-DD)
        try:
            return datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        except ValueError:
            pass

        # Try MM/DD/YYYY
        try:
            return datetime.strptime(birth_date_str, "%m/%d/%Y").date()
        except ValueError:
            pass

        # Try DD/MM/YYYY
        try:
            return datetime.strptime(birth_date_str, "%d/%m/%Y").date()
        except ValueError:
            raise ValueError(
                f"Unsupported date format: {birth_date_str}. "
                "Expected YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY"
            )

    @staticmethod
    def _map_personality(scores: Dict[str, int]) -> PersonalityProfile:
        """
        Map personality Likert scores (1-5) to 0-100 scale.

        Survey uses 1-5 Likert scale:
        - 1 = Strongly disagree (0)
        - 2 = Disagree (25)
        - 3 = Neutral (50)
        - 4 = Agree (75)
        - 5 = Strongly agree (100)

        Args:
            scores: Dict with keys like "extroversion", "structured", etc.
                   Values are 1-5 Likert scores

        Returns:
            PersonalityProfile with 0-100 scaled values
        """
        def scale_likert(likert_score: int) -> int:
            """Convert 1-5 Likert to 0-100 scale."""
            if likert_score < 1 or likert_score > 5:
                return 50  # Default to neutral if out of range
            return (likert_score - 1) * 25

        # Map survey field names to PersonalityProfile field names
        field_mapping = {
            "extroversion": "extraversion",  # Note: survey uses "extroversion"
            "structured": "conscientiousness",
            "openness": "openness",
            "empathy": "agreeableness",
            "calm": "neuroticism",  # Reverse: calm = low neuroticism
            "focus": "detail_vs_big_picture",
            "creative": "analytical_vs_intuitive",  # Reverse: creative = low analytical
            "logical": "proactive_vs_reactive",
        }

        personality_values = {}

        for survey_key, profile_key in field_mapping.items():
            raw_score = scores.get(survey_key, 3)  # Default to neutral (3)

            # Handle reverse scales
            if survey_key == "calm":
                # High calm = low neuroticism
                scaled = 100 - scale_likert(raw_score)
            elif survey_key == "creative":
                # High creative = low analytical
                scaled = 100 - scale_likert(raw_score)
            else:
                scaled = scale_likert(raw_score)

            personality_values[profile_key] = scaled

        return PersonalityProfile(**personality_values)

    @staticmethod
    def _map_interests(topics: List[str], activities: Dict[str, Any]) -> InterestsProfile:
        """
        Map survey interests to InterestsProfile.

        Args:
            topics: List of interest topics from survey
            activities: Dict of activity preferences

        Returns:
            InterestsProfile
        """
        # Primary interests come from survey topics
        primary_interests = topics if topics else []

        # Secondary interests derived from activities
        secondary_interests = []
        for activity_type, activity_values in activities.items():
            if isinstance(activity_values, list):
                secondary_interests.extend(activity_values)
            elif isinstance(activity_values, str):
                secondary_interests.append(activity_values)

        return InterestsProfile(
            primary_interests=primary_interests,
            secondary_interests=secondary_interests[:10]  # Limit to top 10
        )

    @staticmethod
    def _map_role(role_str: str) -> Role:
        """
        Map role string to Role enum.

        Args:
            role_str: Role string from survey (e.g., "student", "office_worker")

        Returns:
            Role enum value

        Raises:
            ValueError: If role is not recognized
        """
        role_mapping = {
            "student": Role.STUDENT,
            "office_worker": Role.OFFICE_WORKER,
            "freelancer": Role.FREELANCER,
        }

        role_lower = role_str.lower().strip()
        if role_lower not in role_mapping:
            raise ValueError(
                f"Unknown role: {role_str}. "
                f"Expected one of: {list(role_mapping.keys())}"
            )

        return role_mapping[role_lower]

    @staticmethod
    def _extract_activity_preferences(
        activities: Dict[str, Any],
        role: str
    ) -> Dict[str, List[str]]:
        """
        Extract and organize activity preferences by category.

        Args:
            activities: Raw activity data from survey
            role: User's role (student, office_worker, etc.)

        Returns:
            Dict mapping category names to selected activities
            Example: {"study": ["시험 준비", "프로젝트"], "exercise": ["러닝", "헬스"]}
        """
        preferences = {}

        # Define role-specific activity field mappings
        role_activity_map = {
            "student": {
                "study": "study_type",
                "exercise": "student_exercise_type",
                "social": "student_social_type",
            },
            "office_worker": {
                "work": "work_type",
                "exercise": "worker_exercise_type",
                "social": "worker_social_type",
            },
            "freelancer": {
                "work": "freelance_work_type",
                "exercise": "freelancer_exercise_type",
                "social": "freelancer_social_type",
            },
            "parent": {
                "daily": "parent_activity_type",
                "exercise": "parent_exercise_type",
                "social": "parent_social_type",
            },
        }

        role_lower = role.lower().strip()
        if role_lower not in role_activity_map:
            return preferences

        # Extract activities for this role
        for category, field_name in role_activity_map[role_lower].items():
            if field_name in activities:
                activity_value = activities[field_name]

                # Handle both list and single string values
                if isinstance(activity_value, list):
                    preferences[category] = activity_value
                elif isinstance(activity_value, str) and activity_value:
                    preferences[category] = [activity_value]

        return preferences
