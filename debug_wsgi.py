"""Debug WSGI issue - check various paths and read the actual WSGI file."""
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

# Try reading the WSGI file from various paths
paths_to_check = [
    f'/var/www/{username}_pythonanywhere_com_wsgi.py',
    f'/var/www/{username.lower()}_pythonanywhere_com_wsgi.py',
    f'/home/{username}/mysite/mysite/wsgi.py',
    f'/home/{username}/mysite/flask_app.py',
    f'/home/{username}/mysite/app.py',
]

for path in paths_to_check:
    resp = requests.get(f'{API}/files/path{path}', headers=headers)
    if resp.status_code == 200:
        print(f'\nFound file at {path}:')
        print(resp.text[:500])
    else:
        print(f'{path}: {resp.status_code}')

# List the home directory
print('\n\nListing /home/KCLegacy/:')
resp = requests.get(f'{API}/files/path/home/{username}/', headers=headers)
if resp.status_code == 200:
    print(resp.text[:500])

# List /var/www/
print('\nListing /var/www/:')
resp = requests.get(f'{API}/files/path/var/www/', headers=headers)
if resp.status_code == 200:
    print(resp.text[:500])

# Upload our WSGI to the exact path with lowercase
wsgi_content = open('pythonanywhere_wsgi.py').read()
print('\n\nUploading WSGI to lowercase path...')
resp = requests.post(
    f'{API}/files/path/var/www/{username.lower()}_pythonanywhere_com_wsgi.py',
    headers=headers,
    files={'content': wsgi_content.encode()}
)
print(f'  {resp.status_code} {resp.text[:200]}')

# Also try uploading to the KCLegacy path again
print('Uploading WSGI to KCLegacy path...')
resp = requests.post(
    f'{API}/files/path/var/www/{username}_pythonanywhere_com_wsgi.py',
    headers=headers,
    files={'content': wsgi_content.encode()}
)
print(f'  {resp.status_code} {resp.text[:200]}')

# Reload and test
print('\nReloading...')
requests.post(f'{API}/webapps/{domain}/reload/', headers=headers)
time.sleep(5)

print('\nTesting...')
r = requests.get(f'https://{domain}/api/bookings')
print(f'  /api/bookings: {r.status_code} - {r.text[:200]}')
r2 = requests.get(f'https://{domain}/')
print(f'  /: {r2.status_code} - {r2.text[:200]}')
