import requests
import json
import os
from dotenv import load_dotenv
# Load .env file API key
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
def analyze_journal(text):
    """
    Analyzes the journal entry using OpenAI Chat API:
    - Sentiment (Sentiment) Score (0-1 range)
    - Subjectivity (Subjectivity) Score (0-1 range)
    - General Emotional Tone (A 4-5 sentence detailed explanation of emotion)

    Returns the result as a dictionary.
    """
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        # 🎯 Now we want JSON format!
        messages = [
            {
                "role": "system",
                "content": "You are an NLP expert. You analyze diary entries for emotional analysis."
            },
            {
                "role": "user",
                "content": f"""
Analyze the following diary entry:
\"{text}\"
Please return the answer in the following JSON format:
{{
  "sentiment_score": (a number between 0 and 1),
  "subjectivity_score": (a number between 0 and 1),
  "general_emotional_tone": "A 4-5 sentence detailed explanation of emotion"
}}
Please return only this JSON data. Do not write anything else.
"""
            }
        ]
        data = {
            "model": "gpt-4",
            "messages": messages,
            "temperature": 0.2
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        if response.status_code != 200:
            return {"error": f"API error: {response.status_code} - {response.text}"}
        result_text = response.json()["choices"][0]["message"]["content"]
        # 🎯 Now we directly parse JSON
        result_json = json.loads(result_text)
        return {
            "sentiment_score": result_json.get("sentiment_score", 0.0),
            "subjectivity_score": result_json.get("subjectivity_score", 0.0),
            "emotion": result_json.get("general_emotional_tone", "Unknown")
        }
    except Exception as e:
        try:
            error_message = response.json().get("error", {}).get("message", str(e))
        except:
            error_message = str(e)
        return {"error": f"NLP analysis encountered an error: {error_message}"}