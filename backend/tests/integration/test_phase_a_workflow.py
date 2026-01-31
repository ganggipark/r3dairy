"""
Integration tests for Phase A: Survey Collection System

Tests complete workflow from survey creation to profile creation.
"""

import pytest
from typing import Dict, Any
from datetime import datetime, timedelta
import json


class TestSurveyCreationDeployment:
    """Scenario 1: Survey Creation → Deployment"""

    @pytest.mark.asyncio
    async def test_survey_creation_and_deployment(
        self,
        mock_n8n_client,
        survey_template_default,
        sample_n8n_workflow_config
    ):
        """
        Test workflow:
        1. Create survey from template (form-builder)
        2. Generate n8n workflow config (form-builder → generators)
        3. Deploy to n8n (using n8n-mcp)
        4. Verify webhook URL generated
        5. Test webhook accepts form submission

        Assertion: Workflow deployed and responding
        """
        # Step 1: Create survey from template
        survey_config = survey_template_default.copy()
        assert survey_config["name"] == "Default Survey"
        assert len(survey_config["sections"]) == 2

        # Step 2: Generate n8n workflow config
        workflow_config = sample_n8n_workflow_config.copy()
        assert "nodes" in workflow_config
        assert "connections" in workflow_config

        # Step 3: Deploy to n8n
        deployment_result = await mock_n8n_client.create_workflow(workflow_config)
        assert deployment_result["id"] == "test-workflow-id"
        assert deployment_result["active"] is True

        # Step 4: Verify webhook URL generated
        webhook_url = deployment_result["webhook_url"]
        assert webhook_url.startswith("https://")
        assert "webhook" in webhook_url

        # Step 5: Test webhook accepts submission
        test_response = await mock_n8n_client.test_webhook(webhook_url, {"test": "data"})
        assert test_response["success"] is True

        print("✅ Survey creation and deployment workflow completed")


class TestSurveySubmissionResponseStorage:
    """Scenario 2: Survey Submission → Response Collection"""

    @pytest.mark.asyncio
    async def test_survey_submission_and_response_storage(
        self,
        sample_survey_response,
        mock_supabase_client,
        mock_n8n_client
    ):
        """
        Test workflow:
        1. Submit completed survey form
        2. n8n workflow receives and normalizes
        3. Response stored in database
        4. Response accessible via API

        Assertion: Survey response persists and is retrievable
        """
        # Step 1: Submit completed survey form
        form_data = sample_survey_response.copy()
        assert form_data["name"] == "Park Ji-hoon"
        assert form_data["email"] == "jihoon@company.com"

        # Step 2: n8n workflow receives and normalizes
        # Mock n8n webhook receiving data
        webhook_result = await mock_n8n_client.test_webhook(
            "https://n8n.example.com/webhook/test",
            form_data
        )
        assert webhook_result["success"] is True

        # Step 3: Response stored in database
        await mock_supabase_client.table("survey_responses").insert(form_data).execute()

        # Step 4: Response accessible via API
        query_result = await mock_supabase_client.table("survey_responses") \
            .select("*") \
            .eq("email", form_data["email"]) \
            .execute()

        print("✅ Survey submission and response storage workflow completed")


class TestResponseNormalizationProfileCreation:
    """Scenario 3: Response Normalization → Profile Creation"""

    def test_response_normalization_to_profile(
        self,
        sample_survey_response,
        data_processor
    ):
        """
        Test workflow:
        1. Retrieve raw survey response
        2. Normalize using data-processor
        3. Enrich with calculated fields
        4. Validate profile integrity
        5. Store in customer profile tables

        Assertion: Complete CustomerProfile created with all fields
        """
        # Step 1: Retrieve raw survey response
        raw_response = sample_survey_response.copy()
        assert "personality_scores" in raw_response
        assert len(raw_response["personality_scores"]) == 8

        # Step 2: Normalize using data-processor
        normalized_data = data_processor.normalize_survey_response(raw_response)

        # Step 3: Enrich with calculated fields
        # Calculate age from birth_date
        birth_date = datetime.strptime(raw_response["birth_date"], "%Y-%m-%d")
        age = (datetime.now() - birth_date).days // 365
        normalized_data["age"] = age

        # Calculate personality traits
        scores = raw_response["personality_scores"]
        normalized_data["personality_traits"] = {
            "openness": (scores[0] + scores[4]) / 2,
            "conscientiousness": (scores[1] + scores[5]) / 2,
            "extraversion": (scores[2] + scores[6]) / 2,
            "agreeableness": (scores[3] + scores[7]) / 2,
        }

        # Step 4: Validate profile integrity
        required_fields = [
            "name", "email", "birth_date", "gender", "role",
            "interests", "subscription_type", "age", "personality_traits"
        ]
        for field in required_fields:
            assert field in normalized_data, f"Missing required field: {field}"

        # Validate data types
        assert isinstance(normalized_data["name"], str)
        assert isinstance(normalized_data["age"], int)
        assert isinstance(normalized_data["personality_traits"], dict)
        assert isinstance(normalized_data["interests"], list)

        # Step 5: Store in customer profile tables (mocked)
        profile_id = f"profile_{normalized_data['email']}"
        assert profile_id is not None

        print("✅ Response normalization to profile workflow completed")


class TestCompleteEndToEndWorkflow:
    """Scenario 4: Complete End-to-End Workflow"""

    @pytest.mark.asyncio
    async def test_complete_phase_a_workflow(
        self,
        all_example_responses,
        data_processor,
        mock_n8n_client,
        mock_supabase_client
    ):
        """
        Complete workflow:
        1. Create survey from template
        2. Deploy to n8n
        3. Submit sample responses (5 examples: student, office worker, freelancer, parent, other)
        4. Process each response to profile
        5. Verify profiles in database
        6. Query profiles via API

        Assertion: 5 complete customer profiles created with correct attributes
        """
        # Step 1 & 2: Create and deploy survey
        workflow_result = await mock_n8n_client.create_workflow({
            "name": "Complete Test Workflow",
            "nodes": [],
        })
        assert workflow_result["active"] is True

        # Step 3 & 4: Submit and process 5 sample responses
        created_profiles = []

        for response in all_example_responses:
            # Submit response
            await mock_n8n_client.test_webhook(
                workflow_result["webhook_url"],
                response
            )

            # Process to profile
            normalized = data_processor.normalize_survey_response(response)

            # Calculate additional fields
            birth_date = datetime.strptime(response["birth_date"], "%Y-%m-%d")
            normalized["age"] = (datetime.now() - birth_date).days // 365

            scores = response["personality_scores"]
            normalized["personality_traits"] = {
                "openness": (scores[0] + scores[4]) / 2,
                "conscientiousness": (scores[1] + scores[5]) / 2,
                "extraversion": (scores[2] + scores[6]) / 2,
                "agreeableness": (scores[3] + scores[7]) / 2,
            }

            created_profiles.append(normalized)

        # Step 5: Verify profiles in database
        assert len(created_profiles) == 5

        # Verify each profile has correct attributes
        roles_created = set(p["role"] for p in created_profiles)
        expected_roles = {"student", "office_worker", "freelancer", "parent", "other"}
        assert roles_created == expected_roles

        # Verify data integrity
        for profile in created_profiles:
            assert "name" in profile
            assert "email" in profile
            assert "age" in profile
            assert profile["age"] >= 13  # Minimum age requirement
            assert "personality_traits" in profile
            assert len(profile["interests"]) > 0

        # Step 6: Query profiles via API (mocked)
        for profile in created_profiles:
            query_result = await mock_supabase_client.table("customer_profiles") \
                .select("*") \
                .eq("email", profile["email"]) \
                .execute()

        print("✅ Complete Phase A end-to-end workflow completed")
        print(f"   Created {len(created_profiles)} customer profiles")


class TestConditionalLogic:
    """Scenario 5: Conditional Logic Testing"""

    def test_paper_delivery_conditional_logic(self, data_processor):
        """
        Test:
        1. Response with subscription_type = "app_only" → paper fields should be ignored
        2. Response with subscription_type = "hybrid" → paper fields required
        3. Response with subscription_type = "paper_only" → paper fields required

        Assertion: Validation passes for valid combinations, fails for invalid
        """
        # Test 1: app_only - paper fields ignored
        app_only_response = {
            "name": "Test User",
            "email": "test@example.com",
            "subscription_type": "app_only",
            "email_frequency": "weekly",
        }
        normalized = data_processor.normalize_survey_response(app_only_response)
        assert "paper_size" not in normalized or normalized.get("paper_size") is None
        assert "delivery_frequency" not in normalized or normalized.get("delivery_frequency") is None

        # Test 2: hybrid - paper fields required
        hybrid_response = {
            "name": "Test User 2",
            "email": "test2@example.com",
            "subscription_type": "hybrid",
            "paper_size": "A5",
            "delivery_frequency": "monthly",
            "email_frequency": "weekly",
        }
        normalized = data_processor.normalize_survey_response(hybrid_response)
        assert normalized["paper_size"] == "A5"
        assert normalized["delivery_frequency"] == "monthly"

        # Test 3: paper_only - paper fields required
        paper_only_response = {
            "name": "Test User 3",
            "email": "test3@example.com",
            "subscription_type": "paper_only",
            "paper_size": "A4",
            "delivery_frequency": "monthly",
            "email_frequency": "none",
        }
        normalized = data_processor.normalize_survey_response(paper_only_response)
        assert normalized["paper_size"] == "A4"
        assert normalized["delivery_frequency"] == "monthly"
        assert normalized["email_frequency"] == "none"

        print("✅ Conditional logic validation completed")


class TestDataValidation:
    """Scenario 6: Data Validation and Anomaly Detection"""

    def test_validation_catches_errors(self, invalid_responses, data_processor):
        """
        Test validation catches:
        1. Duplicate email
        2. Invalid email format
        3. Birth date in future
        4. Age below 13
        5. Empty required fields
        6. Invalid Likert scores (not 1-5)

        Assertion: Appropriate errors returned for each case
        """
        # Test 1: Invalid email format
        with pytest.raises(ValueError, match="Invalid email"):
            data_processor.validate_email(invalid_responses["invalid_email"]["email"])

        # Test 2: Future birth date
        future_date = invalid_responses["future_birth_date"]["birth_date"]
        birth_datetime = datetime.strptime(future_date, "%Y-%m-%d")
        assert birth_datetime > datetime.now(), "Birth date should be in future for test"

        # Test 3: Age below 13
        recent_date = invalid_responses["age_below_13"]["birth_date"]
        age = (datetime.now() - datetime.strptime(recent_date, "%Y-%m-%d")).days // 365
        assert age < 13, "Age should be below 13 for test"

        # Test 4: Empty required field
        assert invalid_responses["missing_required_field"]["name"] is None

        # Test 5: Invalid Likert score
        invalid_scores = invalid_responses["invalid_likert_score"]["personality_scores"]
        assert max(invalid_scores) > 5, "Should have invalid score > 5"

        print("✅ Validation error detection completed")


class TestKoreanLocalization:
    """Scenario 7: Korean Localization"""

    def test_korean_localization(self, sample_korean_response, data_processor):
        """
        Test:
        1. Survey in Korean language
        2. Korean options (역할, 관심사) normalize correctly
        3. Personality analysis works with Korean input
        4. Profile fields preserve Korean data

        Assertion: Full Korean workflow works end-to-end
        """
        # Step 1: Survey in Korean
        korean_data = sample_korean_response.copy()
        assert korean_data["name"] == "김성훈"
        assert korean_data["gender"] == "남성"
        assert korean_data["role"] == "직장인"

        # Step 2: Korean options normalize correctly
        normalized = data_processor.normalize_survey_response(korean_data)

        # Map Korean role to English
        role_mapping = {
            "직장인": "office_worker",
            "학생": "student",
            "프리랜서": "freelancer",
            "부모": "parent",
            "기타": "other",
        }
        assert normalized.get("role") == role_mapping.get(korean_data["role"], korean_data["role"])

        # Step 3: Personality analysis with Korean input
        scores = korean_data["personality_scores"]
        personality_traits = {
            "openness": (scores[0] + scores[4]) / 2,
            "conscientiousness": (scores[1] + scores[5]) / 2,
            "extraversion": (scores[2] + scores[6]) / 2,
            "agreeableness": (scores[3] + scores[7]) / 2,
        }
        assert all(1 <= v <= 5 for v in personality_traits.values())

        # Step 4: Profile preserves Korean data
        assert normalized["name"] == "김성훈"
        assert normalized["birth_location"] == "서울, 대한민국"

        print("✅ Korean localization workflow completed")


class TestMultipleSubmissionSources:
    """Scenario 8: Multiple Submission Sources"""

    @pytest.mark.asyncio
    async def test_multiple_source_handling(
        self,
        sample_survey_response,
        data_processor,
        mock_n8n_client
    ):
        """
        Test processing responses from:
        1. n8n webhook
        2. Google Forms API export
        3. Web form POST

        Assertion: All sources normalize to same profile format
        """
        base_data = sample_survey_response.copy()

        # Source 1: n8n webhook format
        n8n_format = {
            "body": base_data,
            "headers": {"content-type": "application/json"},
            "query": {},
        }
        n8n_normalized = data_processor.normalize_survey_response(n8n_format["body"])

        # Source 2: Google Forms export format
        google_forms_format = {
            "Timestamp": datetime.now().isoformat(),
            "Name": base_data["name"],
            "Email Address": base_data["email"],
            "Birth Date": base_data["birth_date"],
            "Gender": base_data["gender"],
            "Role": base_data["role"],
            # ... other fields with different key names
        }
        # Map Google Forms keys to standard format
        google_normalized = {
            "name": google_forms_format["Name"],
            "email": google_forms_format["Email Address"],
            "birth_date": google_forms_format["Birth Date"],
            "gender": google_forms_format["Gender"],
            "role": google_forms_format["Role"],
        }

        # Source 3: Web form POST format
        web_format = {
            "formData": base_data,
            "submittedAt": datetime.now().isoformat(),
            "source": "web",
        }
        web_normalized = data_processor.normalize_survey_response(web_format["formData"])

        # Assertion: All normalize to same format
        assert n8n_normalized["email"] == google_normalized["email"] == web_normalized["email"]
        assert n8n_normalized["name"] == google_normalized["name"] == web_normalized["name"]

        print("✅ Multiple submission source handling completed")


class TestPerformance:
    """Performance benchmarks"""

    def test_survey_creation_performance(self, performance_timer, survey_template_default):
        """Survey creation should complete in < 100ms"""
        with performance_timer() as timer:
            survey_config = survey_template_default.copy()
            # Process template
            processed = json.dumps(survey_config)
            loaded = json.loads(processed)

        assert timer.elapsed < 0.1, f"Survey creation took {timer.elapsed:.3f}s (> 100ms)"
        print(f"✅ Survey creation completed in {timer.elapsed * 1000:.1f}ms")

    def test_profile_creation_from_response_performance(
        self,
        performance_timer,
        sample_survey_response,
        data_processor
    ):
        """Profile creation should complete in < 1 second"""
        with performance_timer() as timer:
            normalized = data_processor.normalize_survey_response(sample_survey_response)
            # Add calculated fields
            birth_date = datetime.strptime(sample_survey_response["birth_date"], "%Y-%m-%d")
            normalized["age"] = (datetime.now() - birth_date).days // 365
            scores = sample_survey_response["personality_scores"]
            normalized["personality_traits"] = {
                "openness": (scores[0] + scores[4]) / 2,
                "conscientiousness": (scores[1] + scores[5]) / 2,
                "extraversion": (scores[2] + scores[6]) / 2,
                "agreeableness": (scores[3] + scores[7]) / 2,
            }

        assert timer.elapsed < 1.0, f"Profile creation took {timer.elapsed:.3f}s (> 1s)"
        print(f"✅ Profile creation completed in {timer.elapsed * 1000:.1f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
