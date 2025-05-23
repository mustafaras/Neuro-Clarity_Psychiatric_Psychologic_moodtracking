import os
import pandas as pd
from datetime import datetime

def load_phq9_history(patient_id):
    """
    Loads PHQ-9 score history for the given patient.
    """
    folder = f"data/records/{patient_id}"
    if not os.path.exists(folder):
        return []
    
    entries = []
    for fname in os.listdir(folder):
        if fname.endswith(".txt") and "entry_" in fname:
            try:
                with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    date_line = [l for l in lines if "Date:" in l or "Tarih:" in l][0]
                    date_str = date_line.split(":")[1].strip()
                    score_line = [l for l in lines if "PHQ-9 Score" in l or "PHQ-9 Skoru" in l][0]
                    score = int(score_line.split(":")[1].split("|")[0].strip())
                    timestamp = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    entries.append((timestamp, score))
            except:
                continue
    
    return sorted(entries, key=lambda x: x[0])

def list_patient_ids():
    """
    Returns the list of registered patient IDs.
    """
    records_folder = "data/records"
    if not os.path.exists(records_folder):
        return []
    
    return [folder for folder in os.listdir(records_folder) if os.path.isdir(os.path.join(records_folder, folder))]

def load_all_entries(patient_id):
    """
    Loads all journal entries for a specific patient.
    """
    entries_folder = f"data/records/{patient_id}/entries"
    if not os.path.exists(entries_folder):
        return []
    
    entries = []
    for filename in os.listdir(entries_folder):
        file_path = os.path.join(entries_folder, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            entries.append({"filename": filename, "content": content})
    
    return entries

def load_form_history(patient_id, form_name):
    """
    Loads historical data for a specific form filled by the patient.
    """
    forms_folder = f"data/records/{patient_id}/forms"
    file_path = f"{forms_folder}/{form_name}_history.csv"
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None