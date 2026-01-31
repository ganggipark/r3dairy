"""
Data Processor Orchestrator

Main processing pipeline that coordinates normalization, enrichment,
validation, and database persistence.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid
import logging

from .models import CustomerProfile
from .normalizer import SurveyResponseNormalizer
from .enricher import ProfileEnricher
from .validator import ProfileValidator

logger = logging.getLogger(__name__)


class DataProcessor:
    """Main processor orchestrating normalization, enrichment, and validation."""

    def __init__(self):
        self.normalizer = SurveyResponseNormalizer
        self.enricher = ProfileEnricher
        self.validator = ProfileValidator

    async def process_survey_response(
        self,
        survey_response: Dict,
        survey_id: Optional[str] = None,
        source: str = "web",
    ) -> Tuple[bool, Optional[CustomerProfile], List[str]]:
        """
        Main processing pipeline:
        1. Normalize raw response -> CustomerProfile
        2. Validate basic structure
        3. Enrich with calculated attributes
        4. Final validation
        5. Return (success, profile, errors)
        """
        errors: List[str] = []

        # Step 1: Normalize
        try:
            profile = self.normalizer.normalize_response(survey_response)
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            return (False, None, [f"Normalization error: {str(e)}"])

        # Step 2: Enrich
        try:
            profile = self.enricher.enrich_profile(profile)
        except Exception as e:
            logger.error(f"Enrichment failed: {e}")
            errors.append(f"Enrichment warning: {str(e)}")

        # Step 3: Validate
        is_valid, validation_errors = self.validator.validate_customer_profile(profile)
        errors.extend(validation_errors)

        # Step 4: Detect anomalies (non-blocking)
        anomalies = self.validator.detect_anomalies(profile)
        if anomalies:
            logger.info(f"Profile anomalies detected: {anomalies}")

        if not is_valid:
            return (False, profile, errors)

        return (True, profile, errors)

    async def create_customer_in_db(
        self,
        profile: CustomerProfile,
        supabase_client,
    ) -> str:
        """
        Create customer record in Supabase.

        Steps:
        1. Check for duplicate email
        2. Create customer record
        3. Create personality record
        4. Create interests record
        5. Create preferences record
        6. Return customer_id
        """
        # Check duplicate
        existing = (
            supabase_client.table("customers")
            .select("id")
            .eq("email", profile.email)
            .execute()
        )
        if existing.data:
            raise ValueError(f"Customer with email {profile.email} already exists")

        customer_id = profile.id or str(uuid.uuid4())
        now_iso = datetime.utcnow().isoformat()

        # Insert customer
        supabase_client.table("customers").insert({
            "id": customer_id,
            "name": profile.name,
            "email": profile.email,
            "birth_date": profile.birth_date.isoformat(),
            "gender": profile.gender,
            "age": profile.age,
            "zodiac_sign": profile.zodiac_sign,
            "korean_zodiac": profile.korean_zodiac,
            "primary_role": profile.primary_role.value,
            "secondary_roles": [r.value for r in profile.secondary_roles],
            "created_at": now_iso,
            "updated_at": now_iso,
            "active": True,
        }).execute()

        # Insert personality
        supabase_client.table("customer_personalities").insert({
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "extraversion": profile.personality.extraversion,
            "conscientiousness": profile.personality.conscientiousness,
            "openness": profile.personality.openness,
            "agreeableness": profile.personality.agreeableness,
            "neuroticism": profile.personality.neuroticism,
            "analytical_vs_intuitive": profile.personality.analytical_vs_intuitive,
            "proactive_vs_reactive": profile.personality.proactive_vs_reactive,
            "detail_vs_big_picture": profile.personality.detail_vs_big_picture,
            "dominant_trait": profile.personality.dominant_trait,
            "secondary_traits": profile.personality.secondary_traits,
            "personality_type": profile.personality.personality_type,
            "raw_scores": profile.personality.raw_scores,
            "created_at": now_iso,
        }).execute()

        # Insert interests
        supabase_client.table("customer_interests").insert({
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "primary_interests": profile.interests.primary_interests,
            "all_interests": profile.interests.all_interests,
            "interest_categories": profile.interests.interest_categories,
            "is_growth_focused": profile.interests.is_growth_focused,
            "is_career_focused": profile.interests.is_career_focused,
            "is_lifestyle_focused": profile.interests.is_lifestyle_focused,
            "is_creative_focused": profile.interests.is_creative_focused,
            "created_at": now_iso,
        }).execute()

        # Insert preferences
        supabase_client.table("customer_preferences").insert({
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "subscription_type": profile.preferences.subscription_type.value,
            "paper_size": profile.preferences.paper_size.value if profile.preferences.paper_size else None,
            "delivery_frequency": profile.preferences.delivery_frequency,
            "delivery_address": profile.preferences.delivery_address,
            "email_frequency": profile.preferences.email_frequency,
            "consent_privacy": profile.preferences.consent_privacy,
            "consent_marketing": profile.preferences.consent_marketing,
            "consent_research": profile.preferences.consent_research,
            "preferred_tone": profile.preferences.preferred_tone,
            "content_depth": profile.preferences.content_depth,
            "created_at": now_iso,
        }).execute()

        logger.info(f"Customer created: {customer_id}")
        return customer_id

    async def update_customer_profile(
        self,
        customer_id: str,
        updated_data: Dict,
        supabase_client,
    ) -> CustomerProfile:
        """Update existing customer profile fields."""
        now_iso = datetime.utcnow().isoformat()

        # Fetch existing
        result = (
            supabase_client.table("customers")
            .select("*")
            .eq("id", customer_id)
            .execute()
        )
        if not result.data:
            raise ValueError(f"Customer {customer_id} not found")

        # Update allowed fields
        update_fields = {}
        allowed = {"name", "gender", "primary_role", "secondary_roles"}
        for key in allowed:
            if key in updated_data:
                update_fields[key] = updated_data[key]

        if update_fields:
            update_fields["updated_at"] = now_iso
            supabase_client.table("customers").update(
                update_fields
            ).eq("id", customer_id).execute()

        # Re-fetch and return
        result = (
            supabase_client.table("customers")
            .select("*")
            .eq("id", customer_id)
            .execute()
        )
        return result.data[0]
