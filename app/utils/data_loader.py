import os
import json
import re
def load_latest_journal_text(patient_id):
    folder = f"data/records/{patient_id}/journal_entries"
    if not os.path.exists(folder):
        return None
    files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")], reverse=True)
    for filename in files:
        path = os.path.join(folder, filename)
        try:
            with open(path, encoding="utf-8") as file:
                content = file.read()
                if "📔 Günlük:" in content and "📊 NLP Analizi:" in content:
                    return content.split("📔 Günlük:")[1].split("📊 NLP Analizi:")[0].strip()
                elif "📔 Yazı" in content:
                    return content.strip()
        except Exception:
            continue
    return None

def load_latest_nlp_analysis(patient_id):
    folder = f"data/records/{patient_id}/journal_entries"
    if not os.path.exists(folder):
        return None
    files = sorted([f for f in os.listdir(folder) if f.endswith(".txt")], reverse=True)
    for filename in files:
        path = os.path.join(folder, filename)
        try:
            with open(path, encoding="utf-8") as file:
                content = file.read()
                if "📊 NLP Analizi:" in content:
                    section = content.split("📊 NLP Analizi:")[-1]
                    lines = [line.strip() for line in section.strip().splitlines() if line.strip()]
                    sentiment_line = next((l for l in lines if "Sentiment" in l), None)
                    subjectivity_line = next((l for l in lines if "Subjectivity" in l), None)
                    emotion_line = next((l for l in lines if "Genel Duygusal Ton" in l or "Duygu:" in l), None)
                    if sentiment_line and subjectivity_line and emotion_line:
                        sentiment_score = float(re.search(r"[-+]?[0-9]*\.?[0-9]+", sentiment_line).group())
                        subjectivity_score = float(re.search(r"[-+]?[0-9]*\.?[0-9]+", subjectivity_line).group())
                        # If ":" is present, split and get the emotion
                        if ":" in emotion_line:
                            emotion = ":".join(emotion_line.split(":")[1:]).strip()
                        else:
                            emotion = emotion_line.strip()
                        return {
                            "sentiment_score": sentiment_score,
                            "subjectivity_score": subjectivity_score,
                            "emotion": emotion
                        }
        except Exception:
            continue
    return None

def load_latest_video_analysis(patient_id):
    folder = f"data/records/{patient_id}/video_analysis"
    if not os.path.exists(folder):
        return None
    files = sorted([f for f in os.listdir(folder) if f.endswith(".json")], reverse=True)
    for filename in files:
        path = os.path.join(folder, filename)
        try:
            with open(path, encoding="utf-8") as file:
                data = json.load(file)
                if "dominant_emotion" in data:
                    return data
        except Exception:
            continue
    return None