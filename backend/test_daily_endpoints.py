"""
Test script for new daily.py endpoints
Run this after starting the backend server with: uvicorn src.main:app --reload
"""
import requests
from datetime import date

BASE_URL = "http://localhost:8000"

# You'll need to replace this with a real access token after login
# For testing, you can get a token by:
# 1. POST /api/auth/login with valid credentials
# 2. Copy the access_token from the response
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def test_markdown_endpoint():
    """Test GET /api/daily/{date}/markdown"""
    test_date = "2026-01-31"
    url = f"{BASE_URL}/api/daily/{test_date}/markdown"

    print(f"Testing: {url}")
    response = requests.get(url, headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")

    if response.status_code == 200:
        print(f"Content length: {len(response.text)} characters")
        print(f"First 200 chars:\n{response.text[:200]}...")
    else:
        print(f"Error: {response.text}")
    print("\n" + "="*80 + "\n")

def test_markdown_html_endpoint():
    """Test GET /api/daily/{date}/markdown-html"""
    test_date = "2026-01-31"
    url = f"{BASE_URL}/api/daily/{test_date}/markdown-html"

    print(f"Testing: {url}")
    response = requests.get(url, headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys()}")
        print(f"Date: {data.get('date')}")
        print(f"HTML length: {len(data.get('html', ''))} characters")
        print(f"First 200 chars of HTML:\n{data.get('html', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    print("\n" + "="*80 + "\n")

def test_json_endpoint():
    """Test existing GET /api/daily/{date} endpoint"""
    test_date = "2026-01-31"
    url = f"{BASE_URL}/api/daily/{test_date}"

    print(f"Testing: {url}")
    response = requests.get(url, headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys()}")
        print(f"Date: {data.get('date')}")
        print(f"Role: {data.get('role')}")
        print(f"Content keys: {data.get('content', {}).keys()}")
    else:
        print(f"Error: {response.text}")
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("Daily API Endpoints Test")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Access Token: {'SET' if ACCESS_TOKEN != 'YOUR_ACCESS_TOKEN_HERE' else 'NOT SET'}")
    print("="*80 + "\n")

    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("ERROR: Please set ACCESS_TOKEN in this script before running.")
        print("\nTo get an access token:")
        print("1. Start the backend server: uvicorn src.main:app --reload")
        print("2. Login via POST /api/auth/login")
        print("3. Copy the access_token from the response")
        print("4. Update ACCESS_TOKEN in this script")
    else:
        test_markdown_endpoint()
        test_markdown_html_endpoint()
        test_json_endpoint()

        print("All tests completed!")
