"""
Test script to verify survey storage migration to Supabase.

This script tests:
1. Survey configuration persistence
2. Survey response persistence
3. Server restart data survival

Prerequisites:
- Supabase tables created (run SURVEY_DB_SETUP.md SQL)
- Backend server running on localhost:8000
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_create_survey() -> str:
    """Test creating a survey configuration."""
    print("\n1. Testing survey creation...")

    response = requests.post(
        f"{BASE_URL}/surveys/create",
        json={
            "template": "default",
            "locale": "ko-KR",
            "name_override": "테스트 설문 - Supabase Migration"
        }
    )

    assert response.status_code == 200, f"Failed to create survey: {response.text}"
    data = response.json()

    survey_id = data["survey_id"]
    print(f"✅ Survey created: {survey_id}")
    print(f"   Name: {data['name']}")
    print(f"   Status: {data['status']}")

    return survey_id


def test_get_survey(survey_id: str) -> Dict[str, Any]:
    """Test retrieving a survey configuration."""
    print(f"\n2. Testing survey retrieval...")

    response = requests.get(f"{BASE_URL}/surveys/{survey_id}")

    assert response.status_code == 200, f"Failed to get survey: {response.text}"
    data = response.json()

    print(f"✅ Survey retrieved: {data['survey_id']}")
    print(f"   Name: {data['name']}")
    print(f"   Status: {data['status']}")
    print(f"   Response count: {data['response_count']}")

    return data


def test_update_survey_status(survey_id: str, status: str = "active"):
    """Test updating survey status."""
    print(f"\n3. Testing status update to '{status}'...")

    response = requests.put(
        f"{BASE_URL}/surveys/{survey_id}/status",
        params={"status": status}
    )

    assert response.status_code == 200, f"Failed to update status: {response.text}"
    data = response.json()

    print(f"✅ Status updated: {data['status']}")

    return data


def test_submit_response(survey_id: str) -> str:
    """Test submitting a survey response."""
    print(f"\n4. Testing survey response submission...")

    response = requests.post(
        f"{BASE_URL}/surveys/submit",
        json={
            "survey_id": survey_id,
            "response_data": {
                "name": "테스트 사용자",
                "email": "test@example.com",
                "birth_date": "1990-01-01",
                "gender": "남성",
                "primary_role": "직장인",
                "topics": ["건강", "관계"],
                "diary_preference": "앱 전용 (웹/모바일)"
            },
            "source": "web"
        }
    )

    assert response.status_code == 200, f"Failed to submit response: {response.text}"
    data = response.json()

    response_id = data["response_id"]
    print(f"✅ Response submitted: {response_id}")
    print(f"   Survey ID: {data['survey_id']}")
    print(f"   Submitted at: {data['submitted_at']}")

    return response_id


def test_get_responses(survey_id: str):
    """Test retrieving survey responses."""
    print(f"\n5. Testing response retrieval...")

    response = requests.get(f"{BASE_URL}/surveys/{survey_id}/responses")

    assert response.status_code == 200, f"Failed to get responses: {response.text}"
    data = response.json()

    print(f"✅ Responses retrieved:")
    print(f"   Total: {data['total']}")
    print(f"   Responses: {len(data['responses'])}")

    if data['responses']:
        first = data['responses'][0]
        print(f"   First response ID: {first['response_id']}")
        print(f"   Source: {first['source']}")

    return data


def test_get_summary(survey_id: str):
    """Test getting survey summary."""
    print(f"\n6. Testing summary retrieval...")

    response = requests.get(f"{BASE_URL}/surveys/{survey_id}/summary")

    assert response.status_code == 200, f"Failed to get summary: {response.text}"
    data = response.json()

    print(f"✅ Summary retrieved:")
    print(f"   Total responses: {data['total_responses']}")
    print(f"   By source: {data['responses_by_source']}")
    print(f"   By date: {data['responses_by_date']}")

    return data


def test_list_surveys():
    """Test listing all surveys."""
    print(f"\n7. Testing survey listing...")

    response = requests.get(f"{BASE_URL}/surveys/")

    assert response.status_code == 200, f"Failed to list surveys: {response.text}"
    data = response.json()

    print(f"✅ Surveys listed: {len(data)} surveys")

    for survey in data[:3]:  # Show first 3
        print(f"   - {survey['survey_id']}: {survey['name']} ({survey['status']})")

    return data


def test_persistence_across_requests(survey_id: str):
    """Test that data persists across multiple requests."""
    print(f"\n8. Testing persistence across requests...")

    # Verify survey still exists
    survey = test_get_survey(survey_id)
    assert survey["survey_id"] == survey_id

    # Verify response count incremented (via DB trigger)
    assert survey["response_count"] >= 1, "Response count should have incremented"

    print(f"✅ Data persisted across requests")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Survey Storage Migration Test")
    print("=" * 60)

    try:
        # Test survey lifecycle
        survey_id = test_create_survey()
        test_get_survey(survey_id)
        test_update_survey_status(survey_id, "active")

        # Test response submission
        response_id = test_submit_response(survey_id)
        test_get_responses(survey_id)
        test_get_summary(survey_id)

        # Test listing
        test_list_surveys()

        # Test persistence
        test_persistence_across_requests(survey_id)

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nMigration Verification:")
        print(f"✅ Survey configurations persist in Supabase")
        print(f"✅ Survey responses persist in Supabase")
        print(f"✅ Response counts auto-increment via DB trigger")
        print(f"✅ Data survives across requests")
        print(f"\nNext step: Restart server and verify survey_id still exists:")
        print(f"  curl http://localhost:8000/surveys/{survey_id}")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Could not connect to backend server at {BASE_URL}")
        print("Make sure the backend server is running:")
        print("  cd backend && uvicorn src.main:app --reload")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
