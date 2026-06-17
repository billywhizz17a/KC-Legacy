#!/usr/bin/env python3
"""
Diagnostic script for PythonAnywhere deployment.
Run this in a Bash console on PythonAnywhere:
    cd ~/kc_legacy_valeting
    python pythonanywhere_diagnose.py
"""

import os
import sys

PROJECT_PATH = '/home/kclegeacy/kc_legacy_valeting'

print("=" * 55)
print(" KC Legacy Valeting - PythonAnywhere Diagnostics")
print("=" * 55)

# Check project directory
print(f"\n[1] Project path: {PROJECT_PATH}")
if os.path.exists(PROJECT_PATH):
    print("    Status: EXISTS")
else:
    print("    Status: NOT FOUND")
    print("    Fix: Make sure you unzipped kc_legacy_valeting.zip")
    sys.exit(1)

# Check key files
print(f"\n[2] Key files:")
files = ['api_server.py', 'requirements.txt', 'pythonanywhere_wsgi.py']
for f in files:
    path = os.path.join(PROJECT_PATH, f)
    status = "OK" if os.path.exists(path) else "MISSING"
    print(f"    {f}: {status}")

# Check uploads directory
print(f"\n[3] Uploads directory:")
for sub in ['text', 'images']:
    path = os.path.join(PROJECT_PATH, 'uploads', sub)
    status = "OK" if os.path.exists(path) else "MISSING"
    print(f"    uploads/{sub}: {status}")

# Check Python dependencies
print(f"\n[4] Python dependencies:")
try:
    import flask
    print(f"    flask: OK (v{flask.__version__})")
except ImportError:
    print(f"    flask: MISSING - Run: pip install -r requirements.txt")

try:
    import flask_cors
    print(f"    flask_cors: OK")
except ImportError:
    print(f"    flask_cors: MISSING - Run: pip install -r requirements.txt")

# Check WSGI file content
print(f"\n[5] WSGI file check:")
wsgi_path = '/var/www/kclegeacy_pythonanywhere_com_wsgi.py'
if os.path.exists(wsgi_path):
    with open(wsgi_path, 'r') as f:
        content = f.read()
    if 'kclegeacy' in content and 'kc_legacy_valeting' in content:
        print("    WSGI file: Looks correct")
    else:
        print("    WSGI file: May have wrong paths - re-upload from project")
else:
    print("    WSGI file: NOT FOUND at expected path")

print(f"\n{'=' * 55}")
print(" If all checks show OK, click Reload on the Web tab.")
print("=" * 55)
