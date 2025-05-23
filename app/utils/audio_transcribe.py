import tempfile
import openai
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
def transcribe_audio(audio_bytes):
    try:
        # Create a temporary file (e.g., .wav extension)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        # Step 1: Use Whisper API to transcribe the audio
        with open(tmp_file_path, "rb") as audio_file:
            transcript_response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            transcript = transcript_response  # Whisper response is already plain text
        # Step 2: Use ChatGPT to perform emotional analysis
        emotion_prompt = f"""
        The following audio transcript is provided below:
        \"\"\"{transcript}\"\"\"
        Based on the provided transcript, please answer the following questions:
        1. What is the general emotion of the speaker? (happy, sad, angry, anxious, etc.)
        2. How intense are the emotions in the speech (low / medium / high)?
        3. What percentage of positive sentences does the speech contain? (0-100, only provide a number)
        4. What percentage of negative sentences does the speech contain? (0-100, only provide a number)
        Please respond in short and concise format.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an experienced psychotherapist."},
                {"role": "user", "content": emotion_prompt}
            ],
            temperature=0.4
        )
        emotion_analysis = response.choices[0].message.content.strip()
        # Clean up the temporary file
        os.remove(tmp_file_path)
        return {
            "transcript": transcript,
            "emotion_analysis": emotion_analysis
        }
    except Exception as e:
        return {"error": f"An error occurred: {e}"}