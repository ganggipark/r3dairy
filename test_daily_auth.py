import requests
import json
from datetime import date

# Login
login_data = {
    "email": "quicktest@example.com",
    "password": "test123456"
}
response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
print(f"Login Status: {response.status_code}")
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"Token: {access_token[:30]}...")
else:
    print(f"Login failed: {response.text}")
    exit(1)

# Get today's date
today = date.today().strftime("%Y-%m-%d")
print(f"\nTesting daily content for: {today}")

# Request daily content
headers = {"Authorization": f"Bearer {access_token}"}
daily_response = requests.get(f"http://localhost:8000/api/daily/{today}", headers=headers)
print(f"\nDaily Content Status: {daily_response.status_code}")

if daily_response.status_code == 200:
    print("SUCCESS: Daily content generated!")
    content = daily_response.json()
    print(f"Response keys: {list(content.keys())}")
    print(f"First 500 chars: {str(content)[:500]}")
elif 'saju' in daily_response.text.lower():
    print("SAJU ERROR DETECTED:")
    print(daily_response.text[:1000])
else:
    print(f"Response: {daily_response.text[:1000]}")
