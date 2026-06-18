"""Upload Booking.apk to PythonAnywhere."""
import requests

config = {}
for line in open('.env'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        config[k] = v

username = config['PA_USERNAME']
api_key = config['API_KEY']
API = f'https://www.pythonanywhere.com/api/v0/user/{username}'
headers = {'Authorization': f'Token {api_key}'}

with open('pythonanywhere_server/www/Booking.apk', 'rb') as f:
    resp = requests.post(f'{API}/files/path/home/{username}/www/Booking.apk', headers=headers, files={'content': f.read()})
print(f'APK upload: {resp.status_code}')
