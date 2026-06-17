import urllib.request, json

API = 'https://kclegeacy.pythonanywhere.com'

# 1. Create a booking
data = {
    'name': 'Ref Test',
    'phone': '07900000000',
    'carMake': 'Audi A4',
    'carReg': 'REF123',
    'email': 'ref@test.com',
    'package': 'Express Mini Valet',
    'packagePrice': 35,
    'date': '2026-07-01',
    'addons': [],
    'totalPrice': '35',
    'specialRequests': ''
}
req = urllib.request.Request(API + '/api/bookings',
    data=json.dumps(data).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=15) as r:
    res = json.loads(r.read().decode())
print('CREATE RESPONSE:', json.dumps(res, indent=2))

bid = res.get('bookingId')
fn = res.get('filename')

# 2. Admin sends a message
msg = {'status': 'confirmed', 'message': 'Your booking is confirmed!'}
req2 = urllib.request.Request(API + '/api/bookings/' + urllib.parse.quote(fn) + '/response',
    data=json.dumps(msg).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
import urllib.parse
with urllib.request.urlopen(req2, timeout=15) as r2:
    print('ADMIN MSG:', r2.read().decode())

# 3. Customer looks up by ref
req3 = urllib.request.Request(API + '/api/bookings/ref/' + bid)
with urllib.request.urlopen(req3, timeout=15) as r3:
    look = json.loads(r3.read().decode())
print('LOOKUP found:', look.get('found'), '| responses:', len(look.get('responses', [])))
print('\nBOOKING REFERENCE:', bid)
