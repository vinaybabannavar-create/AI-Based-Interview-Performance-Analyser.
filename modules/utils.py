import os
from werkzeug.utils import secure_filename
from config import Config
import subprocess

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.AUDIO_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_uploaded_file(file_storage):
    filename = secure_filename(file_storage.filename)
    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file_storage.save(save_path)
    return save_path

def extract_audio_from_video(video_path, out_audio_path):
    """
    Extracts audio using ffmpeg (must be installed)
    """
    # Ensure ffmpeg available; using pydub or ffmpeg command
    # Simpler: use ffmpeg command line
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        out_audio_path
    ]
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_audio_path
    except Exception as e:
        # fallback: return None
        print("ffmpeg audio extraction failed:", e)
        return None
