"""Check and fix WSGI configuration on PythonAnywhere."""
import requests, json, time

config = {}
for line in open('.env'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        config[k] = v

username = config['PA_USERNAME']
api_key = config['API_KEY']
API = f'https://www.pythonanywhere.com/api/v0/user/{username}'
headers = {'Authorization': f'Token {api_key}'}
domain = f'{username}.pythonanywhere.com'

# Check webapp details
resp = requests.get(f'{API}/webapps/{domain}/', headers=headers)
webapp = resp.json()
print(f'Webapp details: {json.dumps(webapp, indent=2)}')

# The WSGI file path on PythonAnywhere is typically:
# /var/www/<username>_pythonanywhere_com_wsgi.py
# But the case might matter - let's try different paths
wsgi_paths = [
    f'/var/www/{username}_pythonanywhere_com_wsgi.py',
    f'/var/www/{username.lower()}_pythonanywhere_com_wsgi.py',
    f'/var/www/KCLegacy_pythonanywhere_com_wsgi.py',
]

wsgi_content = open('pythonanywhere_wsgi.py').read()

for path in wsgi_paths:
    print(f'\nTrying WSGI path: {path}')
    resp = requests.post(
        f'{API}/files/path{path}',
        headers=headers,
        files={'content': wsgi_content.encode()}
    )
    print(f'  Upload: {resp.status_code} {resp.text[:200]}')
    if resp.status_code in (200, 201):
        print(f'  SUCCESS - WSGI uploaded to {path}')
        break

# Also try to read the current WSGI file
for path in wsgi_paths:
    resp = requests.get(f'{API}/files/path{path}', headers=headers)
    if resp.status_code == 200:
        print(f'\nCurrent WSGI content at {path} (first 300 chars):')
        print(resp.text[:300])
        break

# Reload
print('\nReloading...')
resp = requests.post(f'{API}/webapps/{domain}/reload/', headers=headers)
print(f'Reload: {resp.status_code}')
time.sleep(3)

# Test
print('\nTesting site...')
resp = requests.get(f'https://{domain}/')
print(f'  /: {resp.status_code} - {resp.text[:200]}')

resp = requests.get(f'https://{domain}/api/bookings')
print(f'  /api/bookings: {resp.status_code} - {resp.text[:200]}')
