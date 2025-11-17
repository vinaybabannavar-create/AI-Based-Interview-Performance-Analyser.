import cv2
import mediapipe as mp

# This module gives simple metrics:
# - eye_contact_percent (0-100)
# - avg_blink_rate (blinks per minute)
# - emotion_counts (dummy mapping)

mp_face_mesh = mp.solutions.face_mesh

def analyze_video_eye_and_expression(video_path, sample_seconds=30):
    """
    A lightweight analysis that returns:
    {
      "eye_contact": 78,
      "blink_count": 10,
      "estimated_attention_percent": 72,
      "emotion_counts": {"neutral": 20, "happy": 5, ...}  # placeholder
    }
    Replace emotion_counts code with a proper CNN model for emotion detection.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    frames_to_check = int(min(total_frames, fps * sample_seconds))

    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
    eye_contact_hits = 0
    frames_checked = 0
    blink_count = 0
    prev_eye_open = None

    for i in range(frames_to_check):
        ret, frame = cap.read()
        if not ret:
            break
        frames_checked += 1
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            # naive eye-contact check: face orientation -> presence indicates looking toward camera
            eye_contact_hits += 1

            # blink detection placeholder: compare vertical distance between eyelid landmarks
            # (This is only a placeholder; replace with proper blink detection)
            # We'll just simulate occasional blinks:
            import random
            if random.random() < 0.02:
                blink_count += 1

    cap.release()
    face_mesh.close()

    eye_contact_percent = int((eye_contact_hits / frames_checked) * 100) if frames_checked else 0
    estimated_attention = eye_contact_percent

    return {
        "eye_contact_percent": eye_contact_percent,
        "blink_count": blink_count,
        "estimated_attention_percent": estimated_attention,
        "emotion_counts": {"neutral": frames_checked - blink_count, "happy": blink_count}
    }
