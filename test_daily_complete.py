import requests
import json
from datetime import date
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("Testing Complete Daily Content Generation Flow")
print("=" * 70)

# Step 1: Login
print("\n[Step 1] Login...")
login_response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "quicktest@example.com", "password": "test123456"}
)

if login_response.status_code != 200:
    print(f"[X] Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()['access_token']
print(f"[OK] Login successful, token: {token[:30]}...")

headers = {"Authorization": f"Bearer {token}"}
today = date.today().strftime("%Y-%m-%d")

# Step 2: Get daily content (JSON)
print(f"\n[Step 2] Requesting daily content JSON for {today}...")
daily_response = requests.get(
    f"http://localhost:8000/api/daily/{today}",
    headers=headers
)

print(f"Status Code: {daily_response.status_code}")

if daily_response.status_code == 200:
    print("[OK] Daily content JSON generated successfully")
    content = daily_response.json()
    print(f"Response keys: {list(content.keys())}")

    if 'content' in content and isinstance(content['content'], dict):
        content_keys = list(content['content'].keys())
        print(f"Content has {len(content_keys)} fields")
        print(f"Sample fields: {content_keys[:5]}")

        # Show some sample content
        if 'summary' in content['content']:
            summary = content['content']['summary']
            print(f"\nSummary: {summary[:100]}...")
        if 'keywords' in content['content']:
            keywords = content['content']['keywords']
            print(f"Keywords: {keywords[:5]}")
else:
    print(f"[X] Failed with status {daily_response.status_code}")
    print(daily_response.text[:500])
    exit(1)

# Step 3: Get markdown
print(f"\n[Step 3] Requesting markdown for {today}...")
markdown_response = requests.get(
    f"http://localhost:8000/api/daily/{today}/markdown",
    headers=headers
)

print(f"Status Code: {markdown_response.status_code}")

if markdown_response.status_code == 200:
    markdown_text = markdown_response.text
    print(f"[OK] Markdown generated, length: {len(markdown_text)} chars")
    print(f"First 200 chars:\n{markdown_text[:200]}...")
elif markdown_response.status_code == 404:
    print("[INFO] No markdown file found (expected - files need to be pre-generated)")
else:
    print(f"[X] Failed with status {markdown_response.status_code}")
    print(markdown_response.text[:500])

# Step 4: Get markdown-html
print(f"\n[Step 4] Requesting markdown-html for {today}...")
html_response = requests.get(
    f"http://localhost:8000/api/daily/{today}/markdown-html",
    headers=headers
)

print(f"Status Code: {html_response.status_code}")

if html_response.status_code == 200:
    html_data = html_response.json()
    print(f"[OK] HTML generated, length: {len(html_data.get('html', ''))} chars")
    print(f"First 200 chars:\n{html_data.get('html', '')[:200]}...")
elif html_response.status_code == 404:
    print("[INFO] No markdown file found (expected - files need to be pre-generated)")
else:
    print(f"[X] Failed with status {html_response.status_code}")
    print(html_response.text[:500])

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"[{'OK' if daily_response.status_code == 200 else 'X'}] JSON API: {daily_response.status_code}")
print(f"[{'OK' if markdown_response.status_code in [200, 404] else 'X'}] Markdown API: {markdown_response.status_code}")
print(f"[{'OK' if html_response.status_code in [200, 404] else 'X'}] HTML API: {html_response.status_code}")

if daily_response.status_code == 200:
    print("\n[OK] SAJU CALCULATION AND CONTENT GENERATION WORKING!")
else:
    print("\n[X] SAJU CALCULATION FAILED!")

print("=" * 70)
