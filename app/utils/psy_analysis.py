import openai
import os
import glob
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def generate_daily_analysis(patient_id: str, mood_data: dict = None, journal_text: str = "", transcript: str = "") -> str:
    sections = []

    # 📊 Mood Data
    if mood_data and isinstance(mood_data, dict) and any(mood_data.values()):
        mood_text = "📊 Daily Emotional Status:\n"
        for k, v in mood_data.items():
            mood_text += f"- {k.capitalize()}: {v}/10\n"
        sections.append(mood_text)

    # 📔 Written Journal
    if journal_text and journal_text.strip():
        sections.append(f"📔 Written Journal:\n{journal_text.strip()}")

    # 🗣️ Speech Transcript
    if transcript and transcript.strip():
        sections.append(f"🗣️ Voice Journal Transcript:\n{transcript.strip()}")

    # If no data is provided, return a warning
    if not sections:
        return (
            "No information is available regarding the patient's energy, happiness, stress, anxiety, "
            "or self-confidence levels. Neither a written nor voice journal is present. "
            "This may be due to a lack of communication with the patient or insufficient data submission. "
            "More information is needed for a healthy assessment."
        )

    # GPT prompt
    prompt = (
        "Below are daily psychological records of a patient. Based on this data, please create a brief medical evaluation that includes:"
        "\n- Mood, emotional tone, and stress condition"
        "\n- Signs of depression and anxiety"
        "\n- Clinically significant concerns"
        "\n- Observations and recommendations"
        "\n\n--- Patient Data ---\n\n" + "\n\n".join(sections)
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced clinical psychiatrist and mental health researcher."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"🚫 GPT analysis error: {str(e)}"


def generate_weekly_analysis(patient_id: str) -> str:
    folder = f"data/records/{patient_id}/full_reports"
    files = sorted(glob.glob(f"{folder}/full_entry_*.txt"), reverse=True)

    if not files:
        return "🗂️ No recorded data available yet."

    entries = []
    today = datetime.today()

    for file in files:
        try:
            date_str = os.path.basename(file).split("full_entry_")[1].replace(".txt", "")
            file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
        except:
            continue

        if (today - file_date).days <= 7:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                entries.append(f"📅 {file_date.strftime('%Y-%m-%d')}:\n{content}\n")

    if not entries:
        return "📅 Not enough data for the past 7 days."

    combined_data = "\n\n".join(entries)

    prompt = f"""
    Below are the daily reports of a patient from the past 7 days.
    Please provide a clinical weekly summary and evaluation based on this content.
    Pay attention to emotional fluctuations, depression, anxiety, sleep issues, stress patterns, etc.
    Use clear and clinically appropriate language. Include recommendations if needed.

    --- Records ---
    {combined_data}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced clinical psychiatrist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Weekly analysis error: {str(e)}"