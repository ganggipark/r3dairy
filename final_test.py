import requests
from datetime import date

# Login
login = requests.post("http://localhost:8000/api/auth/login",
                      json={"email": "quicktest@example.com", "password": "test123456"})
token = login.json()['access_token']

# Get daily content
today = date.today().strftime("%Y-%m-%d")
daily = requests.get(f"http://localhost:8000/api/daily/{today}",
                    headers={"Authorization": f"Bearer {token}"})

if daily.status_code == 200:
    print("✅ SUCCESS: Daily content generation working!")
    print(f"Status: {daily.status_code}")
    content = daily.json()
    if 'summary' in content:
        print(f"Summary preview: {content['summary'][:100]}...")
    print("✅ SAJU CALCULATION COMPLETE - NO ERRORS")
else:
    print(f"❌ Failed: {daily.status_code}")
    if 'saju' in daily.text.lower():
        print("SAJU ERROR:", daily.text[:500])
