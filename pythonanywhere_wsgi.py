"""
PythonAnywhere WSGI entry point for KC Legacy Valeting API
Username: kclegeacy
"""

import sys
import os

PROJECT_PATH = '/home/kclegeacy/kc_legacy_valeting/pythonanywhere_server'

# Diagnostic: print to error log if path doesn't exist
if not os.path.exists(PROJECT_PATH):
    import logging
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
    logging.error(f"PROJECT_PATH does not exist: {PROJECT_PATH}")
    logging.error(f"Current directory contents: {os.listdir('/home/kclegeacy') if os.path.exists('/home/kclegeacy') else 'N/A'}")
    raise FileNotFoundError(f"Project not found at {PROJECT_PATH}. Did you unzip kc_legacy_valeting.zip?")

if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)

os.chdir(PROJECT_PATH)

# Diagnostic: try importing dependencies
required = ['flask', 'flask_cors']
for module in required:
    try:
        __import__(module)
    except ImportError as e:
        import logging
        logging.basicConfig(stream=sys.stderr, level=logging.ERROR)
        logging.error(f"Missing dependency: {module}. Run: pip install -r requirements.txt")
        raise

from api_server import app as application
