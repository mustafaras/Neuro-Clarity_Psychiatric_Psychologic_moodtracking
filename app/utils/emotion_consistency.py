def compute_consistency(phq_score, text_emotion, voice_emotion, face_emotion):
    def emotion_val(label):
        if label and label.lower() in ["happy", "surprise"]:
            return 1
        elif label and label.lower() in ["neutral"]:
            return 0
        else:
            return -1
    # If phq_score is None, set to 0
    phq_score = phq_score if phq_score is not None else 0
    phq_val = -1 if phq_score >= 10 else (0 if phq_score >= 5 else 1)
    text_val = emotion_val(text_emotion)
    voice_val = emotion_val(voice_emotion)
    face_val = emotion_val(face_emotion)
    values = [v for v in [phq_val, text_val, voice_val, face_val] if v is not None]
    if len(values) < 3:
        return None, "Insufficient data."
    variance = max(values) - min(values)
    if variance <= 1:
        return "High Consistency", "The emotional indicators generally show high consistency."
    elif variance == 2:
        return "Medium Consistency", "There are some differences in emotional indicators. Pay attention."
    else:
        return "Low Consistency", (
            "There are clear differences between the emotional indicators. This may indicate deception, denial or emotional masking."
        )