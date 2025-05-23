import cv2
from deepface import DeepFace
import numpy as np

def analyze_video_emotions(video_path: str, max_frames: int = 100):
    video = cv2.VideoCapture(video_path)
    emotions_summary = []
    frame_count = 0

    while video.isOpened() and frame_count < max_frames:
        ret, frame = video.read()
        if not ret:
            break
        try:
            result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
            if isinstance(result, list):
                emotions_summary.append(result[0]["emotion"])
        except Exception:
            pass
        frame_count += 1

    video.release()

    if not emotions_summary:
        return {"error": "No face detected or analysis failed."}

    keys = emotions_summary[0].keys()
    avg_emotions = {k: np.mean([emo[k] for emo in emotions_summary]) for k in keys}
    dominant_emotion = max(avg_emotions, key=avg_emotions.get)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_scores": avg_emotions,
        "frame_count": frame_count
    }