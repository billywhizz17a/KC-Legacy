"""
KC Legacy Valeting - Backend API Server
Provides REST endpoints for bookings and images so external clients
(admin program, social media app, etc.) can connect independently.

Run: python api_server.py
The API will start on http://localhost:5000
"""

import os
import json
import uuid
import datetime
import io
from flask import Flask, jsonify, send_file, request, send_from_directory, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the desktop clients

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_UPLOADS_DIR = os.path.join(BASE_DIR, "uploads", "text")
IMAGE_UPLOADS_DIR = os.path.join(BASE_DIR, "uploads", "images")
RESPONSES_DIR = os.path.join(BASE_DIR, "uploads", "responses")
# Static customer website files (index.html, app.js, style.css, site.html, etc.)
# On PythonAnywhere: /home/KCLegacy/www
# Locally: use the www folder in this directory
if os.path.exists("/home/KCLegacy/www"):
    WWW_DIR = "/home/KCLegacy/www"
else:
    WWW_DIR = os.path.join(BASE_DIR, "www")

os.makedirs(TEXT_UPLOADS_DIR, exist_ok=True)
os.makedirs(IMAGE_UPLOADS_DIR, exist_ok=True)
os.makedirs(RESPONSES_DIR, exist_ok=True)


# ── Large file chunk reassembly (e.g. Booking.apk uploaded in parts) ──
def _reassemble_large_files():
    """Combine split file parts (e.g. Booking.apk.part*) into a single file on startup."""
    parts_dir = os.path.join(WWW_DIR, "apk_parts")
    if not os.path.isdir(parts_dir):
        return
    parts = sorted([f for f in os.listdir(parts_dir) if f.startswith("Booking.apk.part")])
    if not parts:
        return
    target = os.path.join(WWW_DIR, "Booking.apk")
    try:
        with open(target, "wb") as out:
            for part in parts:
                part_path = os.path.join(parts_dir, part)
                with open(part_path, "rb") as p:
                    out.write(p.read())
        # Clean up parts once successfully reassembled
        for part in parts:
            os.remove(os.path.join(parts_dir, part))
        os.rmdir(parts_dir)
        print(f"Reassembled {target} from {len(parts)} parts")
    except Exception as e:
        print(f"Failed to reassemble APK chunks: {e}")

_reassemble_large_files()


# ── Main Website (Flask-served, replaces Streamlit) ──
@app.route("/", methods=["GET"])
def home():
    """Serve the main KC Legacy website (gallery, packages, booking)."""
    site_path = os.path.join(WWW_DIR, "site.html")
    if os.path.exists(site_path):
        return send_from_directory(WWW_DIR, "site.html")
    return jsonify({
        "service": "KC Legacy Valeting",
        "message": "Website not found. Upload site.html to the www folder."
    }), 404


@app.route("/booking", methods=["GET"])
def booking_page():
    """Serve the mobile booking page at /booking"""
    index_path = os.path.join(WWW_DIR, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(WWW_DIR, "index.html")
    return jsonify({
        "service": "KC Legacy Valeting",
        "message": "Booking page not found. Upload www files."
    }), 404


@app.route("/<path:filename>", methods=["GET"])
def serve_static(filename):
    """Serve website assets (site.js, site.css, app.js, style.css, images, APK, etc.)."""
    # Never hijack API routes
    if filename.startswith("api/"):
        abort(404)
    file_path = os.path.join(WWW_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Serve APK with correct MIME type for auto-install on Android
        if filename.endswith('.apk'):
            return send_from_directory(WWW_DIR, filename, mimetype='application/vnd.android.package-archive', as_attachment=True)
        return send_from_directory(WWW_DIR, filename)
    abort(404)


# ── Packages & Pricing (Live Config) ──
@app.route("/api/packages", methods=["GET"])
def get_packages():
    """Serve package and add-on configuration from packages.json.
    This allows live updates to prices/features without rebuilding the app."""
    packages_file = os.path.join(WWW_DIR, "packages.json")
    if not os.path.exists(packages_file):
        return jsonify({"error": "packages.json not found"}), 404
    try:
        with open(packages_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── OTA Updates (push code updates to existing customer apps) ──
@app.route("/api/ota/customer-app.js", methods=["GET"])
def ota_customer_app_js():
    """Serve the latest customer app.js for OTA updates."""
    # On PythonAnywhere: look in the repo's customer_app/www folder
    candidates = [
        os.path.join(os.path.dirname(BASE_DIR), "kc_legacy_valeting", "customer_app", "www", "app.js"),
        os.path.join(BASE_DIR, "..", "customer_app", "www", "app.js"),
        os.path.join(os.path.dirname(BASE_DIR), "customer_app", "www", "app.js"),
    ]
    # Also check a dedicated OTA folder in WWW_DIR
    ota_file = os.path.join(WWW_DIR, "ota", "customer-app.js")
    if os.path.exists(ota_file):
        candidates.insert(0, ota_file)
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return content, 200, {"Content-Type": "text/javascript", "Cache-Control": "no-cache"}
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    return jsonify({"error": "OTA app.js not found"}), 404


@app.route("/api/ota/customer-style.css", methods=["GET"])
def ota_customer_style_css():
    """Serve the latest customer app style.css for OTA updates."""
    candidates = [
        os.path.join(os.path.dirname(BASE_DIR), "kc_legacy_valeting", "customer_app", "www", "style.css"),
        os.path.join(BASE_DIR, "..", "customer_app", "www", "style.css"),
        os.path.join(os.path.dirname(BASE_DIR), "customer_app", "www", "style.css"),
    ]
    ota_file = os.path.join(WWW_DIR, "ota", "customer-style.css")
    if os.path.exists(ota_file):
        candidates.insert(0, ota_file)
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return content, 200, {"Content-Type": "text/css", "Cache-Control": "no-cache"}
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    return jsonify({"error": "OTA style.css not found"}), 404


# ── Health Check ──
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "KC Legacy Valeting API"})


# ── Bookings ──
@app.route("/api/bookings", methods=["GET"])
def list_bookings():
    files = sorted([f for f in os.listdir(TEXT_UPLOADS_DIR) if f.endswith(".txt")])
    bookings = []
    for f in files:
        filepath = os.path.join(TEXT_UPLOADS_DIR, f)
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            content = f"Error reading file: {e}"
        bookings.append({
            "filename": f,
            "size": os.path.getsize(filepath),
            "content": content
        })
    return jsonify({"count": len(bookings), "bookings": bookings})


@app.route("/api/bookings/<filename>", methods=["GET"])
def get_booking(filename):
    filepath = os.path.join(TEXT_UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Booking not found"}), 404
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"filename": filename, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    try:
        data = request.get_json() or {}

        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        car_make = data.get("carMake", "").strip()
        car_reg = data.get("carReg", "").strip()
        booking_date = data.get("date", "").strip()
        package = data.get("package", "")
        package_price = data.get("packagePrice", 0)
        addons = data.get("addons", [])
        special_requests = data.get("specialRequests", "")
        total_price = data.get("totalPrice", package_price)

        if not name or not phone or not car_make:
            return jsonify({"error": "Name, phone and car details are required"}), 400

        booking_id = str(uuid.uuid4())[:8]
        filename = f"booking_{booking_id}_{name.replace(' ', '_')}.txt"
        file_path = os.path.join(TEXT_UPLOADS_DIR, filename)

        # Handle both formats: list of dicts ({name, price}) from the customer
        # app, and list of plain strings from the Streamlit app.
        def _format_addon(a):
            if isinstance(a, dict):
                return f"  - {a.get('name', 'Add-on')} (+£{a.get('price', 0)})"
            return f"  - {a}"
        addons_str = "\n".join([_format_addon(a) for a in addons]) if addons else "  None"

        booking_content = f"""=============================================
             KC LEGACY VALETING BOOKING
=============================================
Booking ID: {booking_id}
Submission Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
----------------------------------------------
CUSTOMER INFORMATION:
Name: {name}
Phone: {phone}
Email: {email}

VEHICLE & PACKAGE DETAILS:
Vehicle: {car_make}
Registration: {car_reg or 'N/A'}
Selected Package: {package} (From £{package_price})
Scheduled Date: {booking_date}

ADD-ONS INCLUDED:
{addons_str}

SPECIAL REQUESTS:
{special_requests or 'None'}

ESTIMATED TOTAL: £{total_price}
=============================================
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(booking_content)

        return jsonify({
            "success": True,
            "bookingId": booking_id,
            "filename": filename,
            "message": "Booking confirmed"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Quote Request ──
@app.route("/api/quote", methods=["POST"])
def create_quote_request():
    try:
        data = request.get_json() or {}

        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        car_make = data.get("carMake", "").strip()
        package = data.get("package", "")
        package_price = data.get("packagePrice", 0)
        addons = data.get("addons", [])
        estimated_total = data.get("totalPrice", package_price)

        if not name or not phone:
            return jsonify({"error": "Name and phone are required for a quote"}), 400

        booking_id = str(uuid.uuid4())[:8]
        filename = f"quote_{booking_id}_{name.replace(' ', '_')}.txt"
        file_path = os.path.join(TEXT_UPLOADS_DIR, filename)

        def _format_addon(a):
            if isinstance(a, dict):
                return f"  - {a.get('name', 'Add-on')} (+£{a.get('price', 0)})"
            return f"  - {a}"
        addons_str = "\n".join([_format_addon(a) for a in addons]) if addons else "  None"

        quote_content = f"""=============================================
             KC LEGACY VALETING - QUOTE REQUEST
=============================================
Booking ID: {booking_id}
Request Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
----------------------------------------------
CUSTOMER INFORMATION:
Name: {name}
Phone: {phone}

VEHICLE & PACKAGE DETAILS:
Vehicle: {car_make or 'Not specified'}
Selected Package: {package} (From £{package_price})

ADD-ONS SELECTED:
{addons_str}

ESTIMATED TOTAL: £{estimated_total}
----------------------------------------------
STATUS: QUOTE REQUEST - Awaiting admin response with final price
=============================================
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(quote_content)

        return jsonify({
            "success": True,
            "bookingId": booking_id,
            "filename": filename,
            "message": "Quote request submitted"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings/<filename>", methods=["DELETE"])
def delete_booking(filename):
    filepath = os.path.join(TEXT_UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Booking not found"}), 404
    try:
        os.remove(filepath)
        return jsonify({"message": f"{filename} deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Booking Responses ──
@app.route("/api/bookings/<filename>/response", methods=["POST"])
def save_response(filename):
    """Save an admin response + status update for a booking."""
    filepath = os.path.join(TEXT_UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Booking not found"}), 404
    try:
        data = request.get_json() or {}
        status = data.get("status", "pending")
        message = data.get("message", "").strip()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Responses stored in a JSON file keyed by booking filename
        resp_file = os.path.join(RESPONSES_DIR, f"{filename}.json")
        responses = []
        if os.path.exists(resp_file):
            with open(resp_file, "r", encoding="utf-8") as f:
                responses = json.load(f)

        responses.append({
            "timestamp": timestamp,
            "status": status,
            "message": message
        })

        with open(resp_file, "w", encoding="utf-8") as f:
            json.dump(responses, f, indent=2)

        return jsonify({"success": True, "message": "Response saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings/<filename>/response", methods=["GET"])
def get_response(filename):
    """Fetch all admin responses for a booking."""
    resp_file = os.path.join(RESPONSES_DIR, f"{filename}.json")
    if not os.path.exists(resp_file):
        return jsonify({"responses": []})
    try:
        with open(resp_file, "r", encoding="utf-8") as f:
            responses = json.load(f)
        return jsonify({"responses": responses})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings/ref/<booking_id>", methods=["GET"])
def get_booking_by_ref(booking_id):
    """Look up a booking by its reference ID (e.g. abc12345)."""
    files = [f for f in os.listdir(TEXT_UPLOADS_DIR) if f.endswith(".txt")]
    for f in files:
        # Booking IDs are in filenames like booking_abc12345_Name.txt
        if booking_id in f:
            filepath = os.path.join(TEXT_UPLOADS_DIR, f)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                content = f"Error: {e}"

            # Also fetch any responses
            resp_file = os.path.join(RESPONSES_DIR, f"{f}.json")
            responses = []
            if os.path.exists(resp_file):
                try:
                    with open(resp_file, "r", encoding="utf-8") as rf:
                        responses = json.load(rf)
                except Exception:
                    pass

            return jsonify({
                "found": True,
                "filename": f,
                "bookingId": booking_id,
                "content": content,
                "responses": responses
            })
    return jsonify({"found": False, "message": "Booking not found"}), 404


# ── Images ──
@app.route("/api/images", methods=["GET"])
def list_images():
    files = sorted([f for f in os.listdir(IMAGE_UPLOADS_DIR)
                    if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    images = []
    for f in files:
        filepath = os.path.join(IMAGE_UPLOADS_DIR, f)
        images.append({
            "filename": f,
            "size": os.path.getsize(filepath),
            "url": f"/api/images/{f}"
        })
    return jsonify({"count": len(images), "images": images})


@app.route("/api/images/<filename>", methods=["GET"])
def get_image(filename):
    filepath = os.path.join(IMAGE_UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404
    return send_file(filepath)


@app.route("/api/images/<filename>", methods=["DELETE"])
def delete_image(filename):
    filepath = os.path.join(IMAGE_UPLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404
    try:
        os.remove(filepath)
        return jsonify({"message": f"{filename} deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Banner ──
@app.route("/api/banner", methods=["GET"])
def get_banner():
    candidates = [
        os.path.join(IMAGE_UPLOADS_DIR, "hero", "hero.png"),
        os.path.join(IMAGE_UPLOADS_DIR, "header2.jpg"),
        os.path.join(IMAGE_UPLOADS_DIR, "favicon.png"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return send_file(path)
    return jsonify({"error": "No banner image found"}), 404


# ── QR Codes ──
@app.route("/api/qr/<target>", methods=["GET"])
def get_qr_code(target):
    """Generate QR code for Android APK or website URL."""
    try:
        import qrcode
        if target == "android":
            url = "https://KCLegacy.pythonanywhere.com/Booking.apk"
        elif target == "web":
            url = "https://KCLegacy.pythonanywhere.com"
        elif target == "ios":
            url = "https://KCLegacy.pythonanywhere.com"
        else:
            return jsonify({"error": "Invalid QR target. Use 'android', 'ios', or 'web'."}), 400
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")
    except ImportError:
        return jsonify({"error": "qrcode library not installed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 55)
    print(" KC Legacy Valeting API Server")
    print("=" * 55)
    print("Base URL: http://localhost:5000")
    print("Endpoints:")
    print("  GET    /api/health")
    print("  GET    /api/packages")
    print("  GET    /api/bookings")
    print("  GET    /api/bookings/<filename>")
    print("  DELETE /api/bookings/<filename>")
    print("  GET    /api/bookings/ref/<booking_id>")
    print("  POST   /api/bookings/<filename>/response")
    print("  GET    /api/bookings/<filename>/response")
    print("  GET    /api/images")
    print("  GET    /api/images/<filename>")
    print("  DELETE /api/images/<filename>")
    print("  GET    /api/banner")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=False)
