"""Upload site.css to PythonAnywhere."""
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

with open('pythonanywhere_server/www/site.css', 'rb') as f:
    resp = requests.post(f'{API}/files/path/home/{username}/www/site.css', headers=headers, files={'content': f.read()})
print(f'site.css upload: {resp.status_code}')

# Reload
resp = requests.post(f'{API}/webapps/{username}.pythonanywhere.com/reload/', headers=headers)
print(f'Reload: {resp.status_code}')
