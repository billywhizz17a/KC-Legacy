"""Configure the web app on PythonAnywhere."""
import requests, json

config = {}
for line in open('.env'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        config[k] = v

username = config['PA_USERNAME']  # KCLegacy
api_key = config['API_KEY']
API = f'https://www.pythonanywhere.com/api/v0/user/{username}'
headers = {'Authorization': f'Token {api_key}'}
domain = f'{username}.pythonanywhere.com'

# 1. Update web app source/working directory
print('Updating web app configuration...')
resp = requests.patch(
    f'{API}/webapps/{domain}/',
    headers=headers,
    data={
        'source_directory': f'/home/{username}/kc_legacy_valeting/pythonanywhere_server',
        'working_directory': f'/home/{username}/kc_legacy_valeting/pythonanywhere_server',
    }
)
print(f'  Update webapp: {resp.status_code} {resp.text[:200]}')

# 2. Update WSGI file
print('\nUpdating WSGI file...')
wsgi_content = open('pythonanywhere_wsgi.py').read()
resp = requests.post(
    f'{API}/files/path/var/www/{username}_pythonanywhere_com_wsgi.py',
    headers=headers,
    files={'content': wsgi_content.encode()}
)
print(f'  WSGI upload: {resp.status_code} {resp.text[:200]}')

# 3. Check if static mapping exists, add if not
print('\nChecking static mappings...')
resp = requests.get(f'{API}/webapps/{domain}/static_files/', headers=headers)
print(f'  Current static files: {resp.status_code}')
if resp.status_code == 200:
    statics = resp.json()
    print(f'  Existing: {json.dumps(statics, indent=2)}')
    
    # Add static mapping for / -> www
    resp = requests.post(
        f'{API}/webapps/{domain}/static_files/',
        headers=headers,
        data={
            'url': '/',
            'directory': f'/home/{username}/www',
        }
    )
    print(f'  Add / -> www: {resp.status_code} {resp.text[:200]}')

# 4. Install requirements via console
print('\nInstalling Python packages...')
# Create and run a console command
console_code = 'pip install flask flask-cors pillow qrcode 2>&1'
resp = requests.post(
    f'{API}/consoles/{username}/shells/',
    headers=headers,
    data={'executable': 'bash'}
)
print(f'  Create console: {resp.status_code}')

# 5. Reload
print('\nReloading web app...')
resp = requests.post(f'{API}/webapps/{domain}/reload/', headers=headers)
print(f'  Reload: {resp.status_code}')

# 6. Test the site
print('\nTesting the site...')
import time
time.sleep(3)
resp = requests.get(f'https://{domain}/')
print(f'  Site response: {resp.status_code}')
if resp.status_code == 200:
    print(f'  Content length: {len(resp.text)} chars')
    if 'KC Legacy' in resp.text:
        print('  KC Legacy content found!')
    else:
        print(f'  First 200 chars: {resp.text[:200]}')
else:
    print(f'  Error: {resp.text[:300]}')

# Test API
resp = requests.get(f'https://{domain}/api/bookings')
print(f'\n  API /api/bookings: {resp.status_code} {resp.text[:200]}')
