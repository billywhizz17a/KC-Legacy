"""
Upload files to PythonAnywhere via their API.
Reads credentials from .env file.
Run: python upload_to_pa.py
"""
import os
import sys
import time
import requests

# Read .env
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if not os.path.exists(env_path):
    print("ERROR: .env file not found.")
    sys.exit(1)

config = {}
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            config[key.strip()] = val.strip()

username = config.get('PA_USERNAME', 'kclegeacy')
api_key = config.get('API_KEY', '')

if not api_key:
    print("ERROR: Set API_KEY in .env file")
    sys.exit(1)

base = os.path.dirname(os.path.abspath(__file__))
www_dir = os.path.join(base, 'pythonanywhere_server', 'www')
server_dir = os.path.join(base, 'pythonanywhere_server')

API = f"https://www.pythonanywhere.com/api/v0/user/{username}"
headers = {"Authorization": f"Token {api_key}"}

uploads = [
    (os.path.join(www_dir, 'site.html'), f'/home/{username}/www/site.html'),
    (os.path.join(www_dir, 'site.css'), f'/home/{username}/www/site.css'),
    (os.path.join(www_dir, 'site.js'), f'/home/{username}/www/site.js'),
    (os.path.join(server_dir, 'api_server.py'), f'/home/{username}/kc_legacy_valeting/pythonanywhere_server/api_server.py'),
    (os.path.join(base, 'pythonanywhere_wsgi.py'), f'/var/www/{username}_pythonanywhere_com_wsgi.py'),
]

print("=" * 55)
print(" Uploading to PythonAnywhere via API")
print("=" * 55)

for local_path, remote_path in uploads:
    fname = os.path.basename(local_path)
    if not os.path.exists(local_path):
        print(f"  SKIP {fname} (not found locally)")
        continue

    with open(local_path, 'rb') as f:
        content = f.read()

    print(f"  Uploading {fname} -> {remote_path}...")

    # PA API uses files= for multipart upload, path format: files/path/home/...
    api_path = f"files/path{remote_path}"
    resp = requests.post(
        f"{API}/{api_path}/",
        headers=headers,
        files={"content": content}
    )

    if resp.status_code in (200, 201):
        print(f"  OK {fname} ({len(content)} bytes)")
    else:
        print(f"  ERROR {fname}: HTTP {resp.status_code} - {resp.text[:200]}")

# Install qrcode and pillow via console
print("\n  Installing qrcode and pillow...")
resp = requests.post(
    f"{API}/consoles/",
    headers=headers,
    json={"executable": "bash", "arguments": ""}
)
if resp.status_code in (200, 201):
    try:
        console_data = resp.json()
        console_id = console_data.get("id")
        print(f"  Console created: {console_id}")

        requests.post(
            f"{API}/consoles/{console_id}/send_input/",
            headers=headers,
            json={"input": "pip install --user qrcode pillow\n"}
        )
        time.sleep(15)

        resp = requests.get(
            f"{API}/consoles/{console_id}/read_output/",
            headers=headers
        )
        if resp.status_code == 200:
            output = resp.json().get("content", "")
            print(f"  pip: {output[-200:]}")

        requests.delete(f"{API}/consoles/{console_id}/", headers=headers)
    except Exception as e:
        print(f"  Console error: {e}")
        print("  Install manually via Bash console: pip install --user qrcode pillow")
else:
    print(f"  Could not create console: HTTP {resp.status_code}")
    print("  Install manually via Bash console: pip install --user qrcode pillow")

# Reload web app
print("\n  Reloading web app...")
resp = requests.post(f"{API}/webapps/{username}.pythonanywhere.com/reload/", headers=headers)
if resp.status_code in (200, 202):
    print("  Reload OK!")
else:
    print(f"  Reload: HTTP {resp.status_code} - {resp.text[:200]}")

print("\nDone! Check https://kclegeacy.pythonanywhere.com")
