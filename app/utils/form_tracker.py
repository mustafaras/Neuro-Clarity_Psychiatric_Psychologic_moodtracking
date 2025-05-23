import os
from datetime import datetime
import pandas as pd
def save_form_score(patient_id, form_name, score, severity):
    folder = f"data/forms/{patient_id}"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{form_name}.csv")
    timestamp = datetime.now().strftime("%Y-%m-%d")
    row = pd.DataFrame([{
        "date": timestamp,
        "score": score,
        "severity": severity
    }])
    if os.path.exists(path):
        existing = pd.read_csv(path)
        existing = existing[existing["date"] != timestamp]  # If same date, update existing data
        new_df = pd.concat([existing, row], ignore_index=True)
    else:
        new_df = row
    new_df.to_csv(path, index=False)
def load_form_history(patient_id, form_name):
    path = f"data/forms/{patient_id}/{form_name}.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return None