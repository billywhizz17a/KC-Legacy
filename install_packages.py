"""Install packages and check error logs on PythonAnywhere."""
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

# Try to create a console and run pip install
print('Creating console...')
resp = requests.post(
    f'{API}/consoles/',
    headers=headers,
    json={
        'executable': 'bash',
        'arguments': [],
    }
)
print(f'  Create console: {resp.status_code} {resp.text[:300]}')

if resp.status_code in (200, 201):
    console_data = resp.json()
    console_id = console_data.get('id')
    print(f'  Console ID: {console_id}')
    
    # Send pip install command
    print('\nInstalling packages...')
    resp = requests.post(
        f'{API}/consoles/{console_id}/send_input/',
        headers=headers,
        data={'input': 'pip3.11 install --user flask flask-cors pillow qrcode\n'}
    )
    print(f'  Send input: {resp.status_code}')
    
    # Wait for it to finish
    time.sleep(30)
    
    # Get output
    resp = requests.get(
        f'{API}/consoles/{console_id}/read_output/',
        headers=headers,
    )
    print(f'  Output: {resp.status_code}')
    print(resp.text[:1000] if resp.text else '(no output)')

# Also try the system API for installing packages
print('\n\nTrying alternative: checking if packages are already available...')
# Let's just reload and check the error log
print('\nReloading...')
resp = requests.post(f'{API}/webapps/{domain}/reload/', headers=headers)
print(f'  Reload: {resp.status_code}')
time.sleep(5)

# Test
print('\nTesting site...')
resp = requests.get(f'https://{domain}/api/bookings')
print(f'  /api/bookings: {resp.status_code}')
if resp.status_code == 200:
    print(f'  SUCCESS! {resp.text[:200]}')
else:
    print(f'  Still failing: {resp.text[:300]}')
    
# Check if it's a dependency issue by looking at the response
resp2 = requests.get(f'https://{domain}/')
print(f'  /: {resp2.status_code} - {resp2.text[:200]}')
