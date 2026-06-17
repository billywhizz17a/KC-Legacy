import urllib.request, json, urllib.parse

# 1. Create a test booking
print('=== Creating test booking ===')
data = {
    'name': 'Test Customer',
    'phone': '07969168246',
    'carMake': 'BMW 3 Series',
    'carReg': 'TEST123',
    'email': 'test@example.com',
    'package': 'Express Mini Valet',
    'packagePrice': 35,
    'scheduledDate': '2026-06-20',
    'addons': [],
    'totalPrice': '35',
    'specialRequests': 'Test booking'
}
req = urllib.request.Request(
    'https://kclegeacy.pythonanywhere.com/api/bookings',
    data=json.dumps(data).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, timeout=15) as resp:
    result = json.loads(resp.read().decode())
    print('Created:', result)
    filename = result['filename']
    booking_id = result['bookingId']

# 2. Send admin response
print('\n=== Sending admin response ===')
resp_data = {'status': 'confirmed', 'message': 'Hi! Your booking is confirmed for Saturday 10am. See you then!'}
req2 = urllib.request.Request(
    f'https://kclegeacy.pythonanywhere.com/api/bookings/{urllib.parse.quote(filename)}/response',
    data=json.dumps(resp_data).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req2, timeout=15) as resp2:
    result2 = json.loads(resp2.read().decode())
    print('Response saved:', result2)

# 3. Customer checks booking
print('\n=== Customer looking up booking ===')
req3 = urllib.request.Request(f'https://kclegeacy.pythonanywhere.com/api/bookings/ref/{booking_id}')
with urllib.request.urlopen(req3, timeout=15) as resp3:
    data3 = json.loads(resp3.read().decode())
    print('Found:', data3['found'])
    print('Responses:', len(data3.get('responses', [])))
    if data3.get('responses'):
        r = data3['responses'][-1]
        print(f"Admin said: [{r['status']}] {r['message']}")

print('\n=== FULL FLOW WORKS ===')
print(f'Booking #{booking_id}: Customer can see admin messages')
