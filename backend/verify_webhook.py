"""Quick verification script for webhook endpoint."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from src.main import app

def verify_webhook():
    """Verify webhook endpoint is accessible."""
    client = TestClient(app)

    print("=" * 80)
    print("Webhook Endpoint Verification")
    print("=" * 80)

    # Test 1: Health check
    print("\n1. Testing webhook health endpoint...")
    response = client.get("/webhooks/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   [OK] Health endpoint working")

    # Test 2: Check OpenAPI docs include webhook
    print("\n2. Checking OpenAPI documentation...")
    response = client.get("/openapi.json")
    openapi_spec = response.json()
    webhook_paths = [path for path in openapi_spec.get("paths", {}) if "webhook" in path]
    print(f"   Webhook paths found: {webhook_paths}")
    assert len(webhook_paths) > 0
    print("   [OK] Webhook endpoints registered in OpenAPI")

    # Test 3: Test webhook endpoint structure
    print("\n3. Testing webhook endpoint structure...")
    test_payload = {
        "survey_id": "test_survey",
        "submission_id": "test_submission_123",
        "response_data": {"test": "data"},
        "metadata": {}
    }
    response = client.post("/webhooks/n8n/survey", json=test_payload)
    # Should get 404 (survey not found) not 422 (validation error)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 404
    assert "not found" in response.json().get("detail", "").lower()
    print("   [OK] Webhook endpoint accepts payload and validates survey existence")

    print("\n" + "=" * 80)
    print("[OK] All verifications passed!")
    print("=" * 80)

    return True

if __name__ == "__main__":
    try:
        verify_webhook()
        print("\n[OK] Webhook integration is ready for use!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
