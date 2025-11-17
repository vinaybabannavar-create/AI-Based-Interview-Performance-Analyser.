import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "supersecretkey123"

    DB_PATH = os.path.join(BASE_DIR, "instance", "users.db")


    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, "videos")
    AUDIO_FOLDER = os.path.join(UPLOAD_FOLDER, "audio")


    ALLOWED_EXTENSIONS = {"mp4", "mp3", "wav"}
