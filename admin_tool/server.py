"""
KC Legacy Admin Tool - Local web app for managing valet packages & pricing.
Run: python admin_tool/server.py
Open: http://localhost:5001
"""
import os
import sys
import json
import subprocess
import requests as req
from flask import Flask, jsonify, request, send_file, send_from_directory

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WWW_DIR = os.path.join(BASE_DIR, "pythonanywhere_server", "www")
PACKAGES_FILE = os.path.join(WWW_DIR, "packages.json")
ADMIN_DIR = os.path.dirname(os.path.abspath(__file__))

# ── PythonAnywhere Config ──
PA_TOKEN = None
PA_USERNAME = "KCLegacy"

# Try to load from .env
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("API_KEY="):
                PA_TOKEN = line.split("=", 1)[1].strip()
            elif line.startswith("PA_USERNAME="):
                PA_USERNAME = line.split("=", 1)[1].strip()

app = Flask(__name__, static_folder=".")

# ── Routes ──

@app.route("/")
def index():
    return send_file(os.path.join(ADMIN_DIR, "index.html"))

@app.route("/api/current", methods=["GET"])
def get_current():
    """Return current packages.json content."""
    if not os.path.exists(PACKAGES_FILE):
        return jsonify({"error": "packages.json not found"}), 404
    with open(PACKAGES_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/api/save", methods=["POST"])
def save_packages():
    """Save packages.json locally."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        with open(PACKAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return jsonify({"status": "ok", "message": "Saved locally"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/publish", methods=["POST"])
def publish():
    """Save, git commit+push, upload to PythonAnywhere, and reload."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    results = []

    # 1. Save locally
    try:
        with open(PACKAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        results.append({"step": "save", "status": "ok"})
    except Exception as e:
        return jsonify({"error": f"Save failed: {e}"}), 500

    # 2. Git commit + push
    try:
        subprocess.run(["git", "add", "pythonanywhere_server/www/packages.json"],
                       cwd=BASE_DIR, check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Update packages & pricing via admin tool"],
                       cwd=BASE_DIR, check=True, capture_output=True, text=True)
        subprocess.run(["git", "push", "origin", "main"],
                       cwd=BASE_DIR, check=True, capture_output=True, text=True)
        results.append({"step": "git", "status": "ok"})
    except subprocess.CalledProcessError as e:
        # Maybe nothing to commit
        if "nothing to commit" in (e.stdout or "") + (e.stderr or ""):
            results.append({"step": "git", "status": "ok", "note": "Nothing to commit"})
        else:
            results.append({"step": "git", "status": "error", "error": e.stderr or e.stdout or str(e)})

    # 3. Upload to PythonAnywhere
    if not PA_TOKEN:
        results.append({"step": "upload", "status": "error", "error": "No API token found in .env"})
    else:
        try:
            headers = {"Authorization": f"Token {PA_TOKEN}"}
            remote_path = f"/home/{PA_USERNAME}/www/packages.json"
            with open(PACKAGES_FILE, "rb") as f:
                file_content = f.read()
            r = req.post(
                f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/files/path{remote_path}",
                headers=headers,
                files={"content": file_content}
            )
            if r.status_code in (200, 201):
                results.append({"step": "upload", "status": "ok"})
            else:
                results.append({"step": "upload", "status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"})
        except Exception as e:
            results.append({"step": "upload", "status": "error", "error": str(e)})

    # 4. Reload web app
    if PA_TOKEN:
        try:
            headers = {"Authorization": f"Token {PA_TOKEN}"}
            r = req.post(
                f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/webapps/{PA_USERNAME}.pythonanywhere.com/reload/",
                headers=headers
            )
            if r.status_code == 200:
                results.append({"step": "reload", "status": "ok"})
            else:
                results.append({"step": "reload", "status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"})
        except Exception as e:
            results.append({"step": "reload", "status": "error", "error": str(e)})

    # 5. Verify
    try:
        import time
        time.sleep(3)
        r = req.get(f"https://{PA_USERNAME}.pythonanywhere.com/api/packages", timeout=10)
        if r.status_code == 200:
            remote = r.json()
            local_pkgs = len(data.get("packages", []))
            remote_pkgs = len(remote.get("packages", []))
            local_addons = len(data.get("addons", []))
            remote_addons = len(remote.get("addons", []))
            if local_pkgs == remote_pkgs and local_addons == remote_addons:
                results.append({"step": "verify", "status": "ok", "message": f"Site live: {remote_pkgs} packages, {remote_addons} add-ons"})
            else:
                results.append({"step": "verify", "status": "warning", "message": f"Counts differ: local {local_pkgs}/{local_addons}, remote {remote_pkgs}/{remote_addons}"})
        else:
            results.append({"step": "verify", "status": "error", "error": f"HTTP {r.status_code}"})
    except Exception as e:
        results.append({"step": "verify", "status": "error", "error": str(e)})

    return jsonify({"results": results})

@app.route("/api/test-site", methods=["GET"])
def test_site():
    """Quick test of the live site."""
    try:
        r = req.get(f"https://{PA_USERNAME}.pythonanywhere.com/api/packages", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return jsonify({
                "status": "ok",
                "packages": len(data.get("packages", [])),
                "addons": len(data.get("addons", [])),
                "raw": data
            })
        return jsonify({"status": "error", "code": r.status_code}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route("/api/rebuild-apk", methods=["POST"])
def rebuild_apk():
    """Rebuild the Android APK and upload to PythonAnywhere.
    Steps: npm install -> cap sync android -> gradlew assembleDebug -> upload APK
    """
    results = []
    customer_app = os.path.join(BASE_DIR, "customer_app")
    android_dir = os.path.join(customer_app, "android")
    apk_path = os.path.join(android_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")

    # 1. npm install
    try:
        r = subprocess.run(["npm", "install"], cwd=customer_app, check=True,
                           capture_output=True, text=True, timeout=60)
        results.append({"step": "npm_install", "status": "ok"})
    except subprocess.CalledProcessError as e:
        return jsonify({"results": results + [{"step": "npm_install", "status": "error", "error": e.stderr or e.stdout[:300]}]})
    except subprocess.TimeoutExpired:
        return jsonify({"results": results + [{"step": "npm_install", "status": "error", "error": "Timeout"}]})

    # 2. cap sync android
    try:
        r = subprocess.run(["npx", "cap", "sync", "android"], cwd=customer_app, check=True,
                           capture_output=True, text=True, timeout=60)
        results.append({"step": "cap_sync", "status": "ok"})
    except subprocess.CalledProcessError as e:
        return jsonify({"results": results + [{"step": "cap_sync", "status": "error", "error": e.stderr or e.stdout[:300]}]})
    except subprocess.TimeoutExpired:
        return jsonify({"results": results + [{"step": "cap_sync", "status": "error", "error": "Timeout"}]})

    # 3. gradlew assembleDebug
    try:
        gradlew = os.path.join(android_dir, "gradlew.bat") if os.name == "nt" else os.path.join(android_dir, "gradlew")
        r = subprocess.run([gradlew, "assembleDebug"], cwd=android_dir, check=True,
                           capture_output=True, text=True, timeout=180)
        results.append({"step": "gradle_build", "status": "ok"})
    except subprocess.CalledProcessError as e:
        error_msg = (e.stderr or "")[-500:] if e.stderr else (e.stdout or "")[-500:]
        return jsonify({"results": results + [{"step": "gradle_build", "status": "error", "error": error_msg}]})
    except subprocess.TimeoutExpired:
        return jsonify({"results": results + [{"step": "gradle_build", "status": "error", "error": "Timeout (3 min)"}]})

    # 4. Upload APK to PythonAnywhere
    if not os.path.exists(apk_path):
        return jsonify({"results": results + [{"step": "upload_apk", "status": "error", "error": "APK not found at expected path"}]})

    if not PA_TOKEN:
        results.append({"step": "upload_apk", "status": "error", "error": "No API token"})
    else:
        try:
            headers = {"Authorization": f"Token {PA_TOKEN}"}
            remote_path = f"/home/{PA_USERNAME}/www/Booking.apk"
            with open(apk_path, "rb") as f:
                apk_content = f.read()
            r = req.post(
                f"https://www.pythonanywhere.com/api/v0/user/{PA_USERNAME}/files/path{remote_path}",
                headers=headers,
                files={"content": apk_content}
            )
            if r.status_code in (200, 201):
                results.append({"step": "upload_apk", "status": "ok", "message": f"Uploaded {len(apk_content)//1024}KB"})
            else:
                results.append({"step": "upload_apk", "status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"})
        except Exception as e:
            results.append({"step": "upload_apk", "status": "error", "error": str(e)})

    # 5. Verify APK is accessible
    try:
        import time
        time.sleep(2)
        r = req.get(f"https://{PA_USERNAME}.pythonanywhere.com/Booking.apk", timeout=15, stream=True)
        if r.status_code == 200:
            results.append({"step": "verify_apk", "status": "ok", "message": "APK live and downloadable"})
        else:
            results.append({"step": "verify_apk", "status": "error", "error": f"HTTP {r.status_code}"})
    except Exception as e:
        results.append({"step": "verify_apk", "status": "error", "error": str(e)})

    return jsonify({"results": results})


if __name__ == "__main__":
    print("=" * 50)
    print("  KC Legacy Admin Tool")
    print("  Open: http://localhost:5001")
    print("=" * 50)
    if not PA_TOKEN:
        print("\n  WARNING: No API token found in .env")
        print("  Upload/reload will not work without it.")
    print(f"  PythonAnywhere user: {PA_USERNAME}")
    print(f"  Packages file: {PACKAGES_FILE}")
    print()
    app.run(host="localhost", port=5001, debug=False)
