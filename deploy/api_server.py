"""
KC Legacy Valeting - Backend API Server (Minimal)
"""
import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_DIR = os.path.join(BASE_DIR, "uploads", "text")
os.makedirs(TEXT_DIR, exist_ok=True)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "KC Legacy API"})

@app.route("/api/bookings", methods=["GET", "POST"])
def bookings():
    if request.method == "POST":
        data = request.get_json() or {}
        booking_id = data.get("bookingId", "unknown")
        filename = f"booking_{booking_id}.txt"
        filepath = os.path.join(TEXT_DIR, filename)
        lines = []
        lines.append("=" * 45)
        lines.append("KC LEGACY VALETING BOOKING")
        lines.append("=" * 45)
        for key, val in data.items():
            lines.append(f"{key}: {val}")
        lines.append("=" * 45)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return jsonify({"success": True, "bookingId": booking_id})

    files = sorted([f for f in os.listdir(TEXT_DIR) if f.endswith(".txt")], reverse=True)
    result = []
    for f in files:
        path = os.path.join(TEXT_DIR, f)
        try:
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception as e:
            content = str(e)
        result.append({"filename": f, "size": os.path.getsize(path), "content": content})
    return jsonify({"count": len(result), "bookings": result})

@app.route("/api/bookings/<filename>", methods=["GET", "DELETE"])
def booking_detail(filename):
    path = os.path.join(TEXT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    if request.method == "DELETE":
        os.remove(path)
        # Also remove response if exists
        resp_path = os.path.join(TEXT_DIR, filename.replace('.txt', '_response.txt'))
        if os.path.exists(resp_path):
            os.remove(resp_path)
        return jsonify({"success": True})
    with open(path, "r", encoding="utf-8") as f:
        return jsonify({"content": f.read()})


@app.route("/api/bookings/<filename>/response", methods=["GET", "POST"])
def booking_response(filename):
    resp_filename = filename.replace('.txt', '_response.txt')
    resp_path = os.path.join(TEXT_DIR, resp_filename)
    booking_path = os.path.join(TEXT_DIR, filename)

    if not os.path.exists(booking_path):
        return jsonify({"error": "Booking not found"}), 404

    if request.method == "POST":
        data = request.get_json() or {}
        response_data = {
            "status": data.get("status", "pending"),
            "response": data.get("response", ""),
            "updatedAt": datetime.datetime.now().isoformat()
        }
        with open(resp_path, "w", encoding="utf-8") as f:
            json.dump(response_data, f)
        return jsonify({"success": True})

    # GET
    if os.path.exists(resp_path):
        with open(resp_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"status": "pending", "response": "", "updatedAt": None})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
