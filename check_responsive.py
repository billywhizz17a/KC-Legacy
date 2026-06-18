"""Verify live site CSS responsiveness."""
import requests

r = requests.get('https://KCLegacy.pythonanywhere.com/site.css')
print(f'Status: {r.status_code}')
print(f'Has fluid grids (min(300px, 100%)): {"min(300px, 100%)" in r.text}')
print(f'Has 360px breakpoint: {"max-width: 360px" in r.text}')
print(f'Has 480px breakpoint: {"max-width: 480px" in r.text}')
print(f'Has 768px breakpoint: {"max-width: 768px" in r.text}')
print(f'Has 1024px breakpoint: {"max-width: 1024px" in r.text}')
print(f'Has 1600px breakpoint: {"min-width: 1600px" in r.text}')
print(f'Has check-result-site: {"check-result-site" in r.text}')
print(f'Has clamp() for hero: {"clamp(" in r.text}')
print(f'Total lines: {len(r.text.splitlines())}')

# Also check the viewport meta tag is present
r2 = requests.get('https://KCLegacy.pythonanywhere.com/')
print(f'\nHTML has viewport meta: {"width=device-width" in r2.text}')
print(f'HTML has site.css link: {"site.css" in r2.text}')
