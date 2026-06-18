"""Deploy all files to the new PythonAnywhere KCLegacy account."""
import os, requests, time

config = {}
for line in open('.env'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        config[k] = v

username = config['PA_USERNAME']  # KCLegacy
api_key = config['API_KEY']
API = f'https://www.pythonanywhere.com/api/v0/user/{username}'
headers = {'Authorization': f'Token {api_key}'}

# Test connection
resp = requests.get(f'{API}/cpu/', headers=headers)
print(f'Connection test: HTTP {resp.status_code}')
if resp.status_code != 200:
    print(f'Error: {resp.text[:200]}')
    exit(1)
print(f'Connected to account: {username}')

# Create directories by uploading placeholders
dirs_to_create = [
    f'/home/{username}/www',
    f'/home/{username}/kc_legacy_valeting/pythonanywhere_server/uploads/bookings',
    f'/home/{username}/kc_legacy_valeting/pythonanywhere_server/uploads/images',
    f'/home/{username}/kc_legacy_valeting/pythonanywhere_server/uploads/responses',
]

print('\nCreating directories...')
for d in dirs_to_create:
    parts = d.strip('/').split('/')
    current = ''
    for part in parts:
        current = current + '/' + part
        try:
            requests.post(f'{API}/files/path{current}/.placeholder', headers=headers, files={'content': b''})
        except Exception:
            pass
print('Directories created')

# Upload all www files
www_dir = 'pythonanywhere_server/www'
www_files = [f for f in os.listdir(www_dir) if os.path.isfile(os.path.join(www_dir, f))]
print(f'\nUploading {len(www_files)} www files...')
for f in www_files:
    local = os.path.join(www_dir, f)
    remote = f'/home/{username}/www/{f}'
    with open(local, 'rb') as fh:
        resp = requests.post(f'{API}/files/path{remote}', headers=headers, files={'content': fh.read()})
    status = 'OK' if resp.status_code in (200, 201) else f'HTTP {resp.status_code}'
    print(f'  {f}: {status}')
    time.sleep(0.5)

# Server files
server_dir = 'pythonanywhere_server'
server_files = ['api_server.py', 'requirements.txt']
print(f'\nUploading {len(server_files)} server files...')
for f in server_files:
    local = os.path.join(server_dir, f)
    remote = f'/home/{username}/kc_legacy_valeting/pythonanywhere_server/{f}'
    with open(local, 'rb') as fh:
        resp = requests.post(f'{API}/files/path{remote}', headers=headers, files={'content': fh.read()})
    status = 'OK' if resp.status_code in (200, 201) else f'HTTP {resp.status_code}'
    print(f'  {f}: {status}')
    time.sleep(0.5)

# WSGI file
print('\nUploading WSGI file...')
with open('pythonanywhere_wsgi.py', 'rb') as fh:
    resp = requests.post(f'{API}/files/path/home/{username}/kc_legacy_valeting/pythonanywhere_wsgi.py', headers=headers, files={'content': fh.read()})
print(f'  pythonanywhere_wsgi.py: {"OK" if resp.status_code in (200,201) else f"HTTP {resp.status_code}"}')

# Upload Booking.apk
print('\nUploading Booking.apk...')
apk_path = os.path.join(www_dir, 'Booking.apk')
if os.path.exists(apk_path):
    with open(apk_path, 'rb') as fh:
        resp = requests.post(f'{API}/files/path/home/{username}/www/Booking.apk', headers=headers, files={'content': fh.read()})
    print(f'  Booking.apk: {"OK" if resp.status_code in (200,201) else f"HTTP {resp.status_code}"}')
else:
    print('  Booking.apk not found')

# Try to reload web app
print('\nReloading web app...')
try:
    resp = requests.post(f'{API}/webapps/{username}.pythonanywhere.com/reload/', headers=headers)
    print(f'  Reload: HTTP {resp.status_code}')
except Exception as e:
    print(f'  Reload failed (expected if web app not created yet): {e}')

print('\nAll files uploaded! Now you need to:')
print(f'1. Go to PythonAnywhere → Web tab → Add a new web app')
print(f'2. Choose Manual configuration (Python 3.10)')
print(f'3. Set WSGI file to: /home/{username}/kc_legacy_valeting/pythonanywhere_wsgi.py')
print(f'4. Set working directory to: /home/{username}/kc_legacy_valeting/pythonanywhere_server')
print(f'5. Add static files mapping: URL=/  →  Directory=/home/{username}/www')
print(f'6. Install requirements: pip install flask flask-cors pillow qrcode')
print(f'7. Reload the web app')
