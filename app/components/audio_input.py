import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
from utils.audio_transcribe import transcribe_audio
from utils.nlp_analysis import analyze_journal
import os
from datetime import datetime
import wave
import json

def audio_input(patient_id: str):
    st.subheader("🎙️ Audio Journal Entry (Analyzed with Whisper)")
    method = st.radio("📌 How would you like to provide audio?", ["🎤 Record with Microphone", "📂 Upload Audio File"])
    audio_path = None

    if method == "📂 Upload Audio File":
        audio_file = st.file_uploader("Upload an audio file (.mp3, .wav)", type=["mp3", "wav"])
        if audio_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = f"data/audio/{patient_id.strip()}"
            os.makedirs(folder, exist_ok=True)
            audio_path = f"{folder}/uploaded_{timestamp}.wav"
            with open(audio_path, "wb") as f:
                f.write(audio_file.read())
            st.success(f"✅ File saved: `{audio_path}`")
    else:
        class AudioSaver(AudioProcessorBase):
            def __init__(self):
                self.frames = []

            def recv(self, frame):
                self.frames.append(frame)
                return frame

        ctx = webrtc_streamer(
            key="mic",
            mode=WebRtcMode.SENDONLY,
            audio_processor_factory=AudioSaver,
            media_stream_constraints={"audio": True, "video": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            async_processing=True
        )

        if ctx.audio_processor and st.button("💾 Stop Recording and Save"):
            frames = ctx.audio_processor.frames
            if not frames:
                st.warning("⚠️ No audio data captured.")
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder = f"data/audio/{patient_id.strip()}"
                os.makedirs(folder, exist_ok=True)
                audio_path = f"{folder}/mic_{timestamp}.wav"
                with wave.open(audio_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(48000)
                    wf.writeframes(b''.join([f.to_ndarray().tobytes() for f in frames]))
                st.success(f"🎤 Microphone recording saved: `{audio_path}`")

    transcript = None
    if audio_path:
        if st.button("🔍 Analyze Audio"):
            with st.spinner("🔎 Analyzing audio..."):
                try:
                    transcript_result = transcribe_audio(audio_path)
                    if "error" in transcript_result:
                        st.error(transcript_result["error"])
                    else:
                        transcript = transcript_result.get("transcript", "")
                        emotion_text = transcript_result.get("emotion_analysis", "")
                        st.subheader("🖍️ Transcript")
                        st.text_area("Transcript", transcript, height=200)
                        st.subheader("🎭 Audio Emotion Analysis")
                        st.text_area("Emotion Analysis", emotion_text, height=200)
                        st.session_state.audio_transcript_data = {
                            "transcript": transcript,
                            "emotion_analysis": emotion_text
                        }
                except Exception as e:
                    st.error(f"🚫 Error during audio analysis: {str(e)}")

    if "audio_transcript_data" in st.session_state:
        if st.button("💾 Save Audio Journal Analysis"):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder = f"data/records/{patient_id}/audio_analysis"
                os.makedirs(folder, exist_ok=True)
                save_path = f"{folder}/audio_analysis_{timestamp}.json"
                with open(save_path, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.audio_transcript_data, f, ensure_ascii=False, indent=4)
                st.success(f"🎵 Audio journal analysis saved: `{save_path}`")
            except Exception as e:
                st.error(f"Error saving audio analysis: {str(e)}")

    return transcript
