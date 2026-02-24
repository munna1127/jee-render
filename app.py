import cv2
import telebot
import time

# Initialize Telegram bot
TELEGRAM_API_TOKEN = 'your_api_token'
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Replace with your chat ID
CHAT_ID = 'your_chat_id'

# Function to capture photo and send to Telegram
def capture_and_send_photo():
    cap = cv2.VideoCapture(0)  # Open the default camera
    ret, frame = cap.read()  # Capture a frame
    if ret:
        file_path = 'photo.jpg'
        cv2.imwrite(file_path, frame)  # Save the captured frame
        with open(file_path, 'rb') as photo:
            bot.send_photo(CHAT_ID, photo)  # Send the photo to Telegram
    cap.release()  # Release the camera

# Function to capture video frames and send to Telegram
def capture_video_frames():
    cap = cv2.VideoCapture(0)  # Open the default camera
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                file_path = f'frame_{current_time}.jpg'
                cv2.imwrite(file_path, frame)  # Save the Frame
                with open(file_path, 'rb') as video_frame:
                    bot.send_photo(CHAT_ID, video_frame)  # Send frame to Telegram
                time.sleep(3)  # Wait for 3 seconds
    except KeyboardInterrupt:
        cap.release()  # Release the camera when done

if __name__ == '__main__':
    capture_and_send_photo()  # Capture photo
    capture_video_frames()  # Capture video frames