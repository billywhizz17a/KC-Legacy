"""Upload large APK to PythonAnywhere via chunked file API + console reassembly."""
import requests
import os
import time
import math

TOKEN = "b707bdfd18e76cfc4c1dc30db6e3abc03153755a"
USER = "KCLegacy"
APK_LOCAL = "customer_app/android/app/build/outputs/apk/debug/app-debug.apk"
REMOTE_DIR = f"/home/{USER}/www"
CHUNK_SIZE = 2 * 1024 * 1024  # 2MB

headers = {"Authorization": f"Token {TOKEN}"}
base_url = f"https://www.pythonanywhere.com/api/v0/user/{USER}"


def upload_chunk(path, remote_path):
    with open(path, "rb") as f:
        r = requests.post(
            f"{base_url}/files/path{remote_path}",
            headers=headers,
            files={"content": f},
            timeout=60,
        )
    return r.status_code, r.text


def create_console():
    r = requests.post(
        f"{base_url}/consoles/",
        headers={**headers, "Content-Type": "application/json"},
        json={"executable": "bash", "working_directory": REMOTE_DIR},
    )
    if r.status_code in (200, 201):
        return r.json()["id"]
    raise Exception(f"Console create failed: {r.status_code} {r.text}")


def send_console(cid, text):
    r = requests.post(
        f"{base_url}/consoles/{cid}/send_input/",
        headers={**headers, "Content-Type": "application/json"},
        json={"input": text},
    )
    return r.status_code


def get_output(cid):
    r = requests.get(
        f"{base_url}/consoles/{cid}/get_latest_output/",
        headers=headers,
    )
    if r.status_code == 200:
        return r.json().get("output", "")
    return ""


def main():
    total = os.path.getsize(APK_LOCAL)
    chunks = math.ceil(total / CHUNK_SIZE)
    print(f"Uploading {total} bytes in {chunks} chunks")

    # Ensure parts directory exists
    os.makedirs("apk_parts", exist_ok=True)
    part_files = []
    with open(APK_LOCAL, "rb") as src:
        for i in range(chunks):
            part = f"apk_parts/Booking.apk.part{i:03d}"
            data = src.read(CHUNK_SIZE)
            with open(part, "wb") as dst:
                dst.write(data)
            part_files.append(part)

    # Upload chunks
    remote_parts_dir = f"{REMOTE_DIR}/apk_parts"
    for i, part in enumerate(part_files):
        remote = f"{remote_parts_dir}/Booking.apk.part{i:03d}"
        sc, text = upload_chunk(part, remote)
        print(f"Part {i}: {sc} {text[:50]}")
        if sc not in (200, 201):
            print("Upload failed, aborting")
            return

    # Reassemble via console
    # Trigger webapp reload; api_server.py reassembles chunks on startup
    r = requests.post(
        f"{base_url}/webapps/KCLegacy.pythonanywhere.com/reload/",
        headers=headers,
    )
    print("Reload:", r.status_code, r.text[:100])
    time.sleep(10)
    r3 = requests.get(
        f"https://{USER}.pythonanywhere.com/Booking.apk",
        timeout=20,
    )
    print("APK live:", r3.status_code, r3.headers.get("Content-Length"), "bytes")



if __name__ == "__main__":
    main()
