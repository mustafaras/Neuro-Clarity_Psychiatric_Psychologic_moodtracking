import streamlit as st
import openai
import os
import base64
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import json
from dotenv import load_dotenv
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from components.mood_form import daily_mood_form
from components.forms.phq9_form import phq9_form
from components.journal_input import journal_input
from components.chatbot import chatbot_interface
from components.audio_input import audio_input
from utils.pdf_export import export_report
from utils.audio_transcribe import transcribe_audio
from utils import record_loader
from utils.record_loader import list_patient_ids
from components.healthkit_parser import parse_healthkit_zip
from components.apple_health_analysis import display_healthkit_insights
from utils.psy_analysis import generate_daily_analysis, generate_weekly_analysis
from utils.pdf_parser import extract_text_from_pdf
from utils.lab_analysis import interpret_lab_results
from utils.form_tracker import save_form_score, load_form_history
from components.psqi_form import psqi_form
from utils.emotion_consistency import compute_consistency
from utils.nlp_analysis import analyze_journal
from utils.video_emotion import analyze_video_emotions
import av
from PIL import Image
import pytesseract

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initial variables
weekly_forms = {}
monthly_forms = {}
daily_analysis = None
weekly_analysis = None
monthly_analysis = None
lab_summary = None
steps_df = None
sleep_df = None
result = None
if result is None:
    result = {}
transcript = None
manual_steps = None
manual_sleep = None
emotion_consistency_result = None
analysis = {}
text = ""
mood_data = {}
pdf_path = None

# Initialize page control state
if "screen" not in st.session_state:
    st.session_state.screen = "selection"

# Page configuration
st.set_page_config(
    page_title="NeuroClarity",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Patient selection screen
if st.session_state.screen == "selection":
    st.markdown("<h1 style='text-align: center; font-size: 48px;'>✨ NeuroClarity AI</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style='text-align: center; font-size: 20px;'>
        <b>NeuroClarity</b> offers a comprehensive monitoring and early warning system through personalized psychometric tests, daily analyses, emotion recognition, and health data integration.<br><br>
        </p>
        """,
        unsafe_allow_html=True
    )
    st.subheader("🧬 Select Existing Patient or Register New")
    all_patients = list_patient_ids()
    if all_patients:
        selected_patient = st.selectbox("🔎 Select an existing patient:", all_patients)
        if selected_patient:
            st.session_state.patient_id = selected_patient
            st.session_state.screen = "main"
    else:
        st.info("No registered patients yet.")
    st.markdown("---")
    st.subheader("🆕 Register New Patient")
    new_patient_id = st.text_input("Enter new Patient ID:", placeholder="e.g., 00123")
    if "new_patient_id" not in st.session_state:
        st.session_state["new_patient_id"] = ""
    if new_patient_id:
        st.session_state["new_patient_id"] = new_patient_id
    if st.button("🧾 Continue"):
        if st.session_state["new_patient_id"].strip():
            st.session_state.patient_id = st.session_state["new_patient_id"].strip()
            st.session_state.screen = "main"
            st.rerun()
        else:
            st.warning("Please enter a valid patient ID.")

elif st.session_state.screen == "main":
    st.success(f"📋 Selected Patient ID: {st.session_state.patient_id}")
    # 🏠 Change Patient Button
    if st.button("🚪 Change Patient"):
        del st.session_state["patient_id"]
        st.session_state.screen = "selection"
        st.rerun()

    # 🎥 Video Analysis (Facial & Emotion Recognition)
    st.header("🎥 Video Analysis (Facial and Emotion)")
    st.markdown("_In this section, the uploaded video will be processed for facial expressions and emotion analysis. The analysis is performed using a specialized AI model. Please upload a video in MP4, MOV, or 3GP format._")
    uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "3gp"])
    if uploaded_video:
        st.success("🎬 Video uploaded. Click the button for analysis.")
        if st.button("🔍 Analyze Video"):
            try:
                # Save temporarily in memory
                video_bytes = uploaded_video.read()
                st.session_state.video_bytes = video_bytes
                st.session_state.video_filename = uploaded_video.name
                # Save temp file to disk
                with open("temp_video.mp4", "wb") as f:
                    f.write(video_bytes)
                video_result = analyze_video_emotions("temp_video.mp4")
                if "error" in video_result:
                    st.error(video_result["error"])
                else:
                    st.success(f"🏷️ Dominant Emotion: {video_result['dominant_emotion']}")
                    st.json(video_result["emotion_scores"])
                    st.session_state.video_result = video_result
                    st.session_state.video_saved = False
            except Exception as e:
                st.error(f"Error during video analysis: {str(e)}")
    # If analysis is done, offer save option
    if "video_result" in st.session_state:
        today_date_str = datetime.now().strftime("%Y%m%d")
        save_folder = f"data/records/{st.session_state.patient_id}/video_analysis"
        os.makedirs(save_folder, exist_ok=True)
        existing_files = os.listdir(save_folder)
        today_already_saved = any(today_date_str in filename for filename in existing_files)
        if today_already_saved:
            st.info("📅 Video analysis for today already saved. Cannot save again.")
        else:
            if not st.session_state.get("video_saved", False):
                if st.button("💾 Save Analysis and Video"):
                    try:
                        # Save JSON analysis
                        video_folder = f"data/video/{st.session_state.patient_id}"
                        os.makedirs(video_folder, exist_ok=True)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        save_json_path = f"{save_folder}/video_analysis_{timestamp}.json"
                        with open(save_json_path, "w", encoding="utf-8") as f:
                            json.dump(st.session_state.video_result, f, ensure_ascii=False, indent=4)
                        # Save video file
                        file_ext = st.session_state.video_filename.split('.')[-1]
                        save_video_path = f"{video_folder}/uploaded_{timestamp}.{file_ext}"
                        with open(save_video_path, "wb") as f:
                            f.write(st.session_state.video_bytes)
                        st.success(f"🎬 Analysis and video saved successfully!\n\n📄 Analysis: `{save_json_path}`\n🎥 Video: `{save_video_path}`")
                        st.session_state.video_saved = True
                        # Remove temp file
                        if os.path.exists("temp_video.mp4"):
                            os.remove("temp_video.mp4")
                    except Exception as e:
                        st.error(f"Error during saving: {str(e)}")
            else:
                st.info("📅 Analysis already saved for today.")
    # Written Daily Diary & NLP Analysis
    st.header("📔 Written Diary & NLP Analysis")
    st.markdown("_In this section, your written diary entries will be processed for sentiment and emotional analysis. The analysis is performed using GPT-4. Please enter at least 10 words._")
    text = journal_input()
    if "text_analysis_saved" not in st.session_state:
        st.session_state["text_analysis_saved"] = False
    if text.strip():
        if st.button("🔍 Analyze Diary Text"):
            with st.spinner("🔎 Analyzing..."):
                try:
                    analysis = analyze_journal(text)
                    if not analysis or "error" in analysis:
                        st.error(f"Error during NLP analysis: {analysis.get('error', 'Unknown error')}")
                    elif all(k in analysis for k in ['sentiment_score', 'subjectivity_score', 'emotion']):
                        st.subheader("📊 Diary Analysis Results")
                        st.markdown(f"1. **Sentiment Score**: {analysis['sentiment_score']:.2f}")
                        st.markdown(f"2. **Subjectivity Score**: {analysis['subjectivity_score']:.2f}")
                        st.markdown(f"3. **Overall Emotional Tone:** {analysis['emotion']}")
                        st.session_state["text_analysis"] = {
                            "text": text,
                            "analysis": analysis
                        }
                    else:
                        st.warning("⚠️ Incomplete analysis results received. Please try again.")
                except Exception as e:
                    st.error(f"Error during NLP analysis: {str(e)}")
        if "text_analysis" in st.session_state:
            if not st.session_state["text_analysis_saved"]:
                if st.button("💾 Save Diary Entry"):
                    try:
                        today_date_str = datetime.now().strftime("%Y%m%d")
                        folder = f"data/records/{st.session_state.patient_id}/journal_entries"
                        os.makedirs(folder, exist_ok=True)
                        today_filename = f"{folder}/journal_{today_date_str}.txt"
                        with open(today_filename, "w", encoding="utf-8") as f:
                            f.write(f"Patient ID: {st.session_state.patient_id}\n")
                            f.write(f"Date: {today_date_str}\n\n")
                            f.write("📔 Diary Entry:\n")
                            f.write(st.session_state["text_analysis"]['text'] + "\n\n")
                            f.write("📊 NLP Analysis:\n")
                            f.write(f"1. Sentiment Score: {st.session_state['text_analysis']['analysis']['sentiment_score']:.2f}\n")
                            f.write(f"2. Subjectivity Score: {st.session_state['text_analysis']['analysis']['subjectivity_score']:.2f}\n")
                            f.write(f"3. Overall Emotional Tone: {st.session_state['text_analysis']['analysis']['emotion']}\n")
                        st.success(f"📔 Diary entry successfully saved: `{today_filename}`")
                        st.session_state["text_analysis_saved"] = True
                    except Exception as e:
                        st.error(f"Error saving diary: {str(e)}")
            else:
                st.info("📅 Diary for today already saved.")
    else:
        st.info("✍️ Please enter your diary text and click analyze.")

    # 🎙️ Voice Diary Entry
    st.header("🎙️ Record or Upload Voice Diary")
    st.markdown("_Upload your voice diary recording. Transcription and emotion analysis will be performed._")
    uploaded_audio = st.file_uploader("Upload an audio file (.mp3, .wav)", type=["mp3", "wav"])
    if uploaded_audio:
        st.success("✅ File uploaded. Click to analyze.")
        if st.button("🔍 Analyze Audio"):
            result = transcribe_audio(uploaded_audio.read())
            if "error" in result:
                st.error(result["error"])
            else:
                # Save in session state
                st.session_state.transcript = result["transcript"]
                st.session_state.audio_analysis = analyze_journal(result["transcript"])
                st.session_state.audio_bytes = uploaded_audio.read()
                st.session_state.audio_filename = uploaded_audio.name
                st.session_state.audio_saved = False
                # Show analysis
                st.subheader("📋 Transcript & Emotion Analysis")
                st.text_area("📝 Transcript", result["transcript"], height=200, key="audio_transcript_text")
                sentiment_score = st.session_state.audio_analysis.get("sentiment_score", 0)
                emotion_value = st.session_state.audio_analysis.get("emotion", "Undetermined")
                subjectivity_score = st.session_state.audio_analysis.get("subjectivity_score", 0)
                intensity = "High" if abs(sentiment_score) > 0.6 else "Medium" if abs(sentiment_score) > 0.3 else "Low"
                positive_ratio = f"{(1 + sentiment_score) * 50:.0f}%"
                negative_ratio = f"{(1 - sentiment_score) * 50:.0f}%"
                st.subheader("🎭 Voice Emotion Analysis")
                st.text_area("Emotion Analysis", f"""
        1. Overall Mood: {emotion_value}
        2. Emotional Intensity: {intensity}
        3. Approximate positive sentence ratio: {positive_ratio}
        4. Approximate negative sentence ratio: {negative_ratio}
        """.strip(), height=160)

    # Check if today's voice diary is already saved
    if "audio_analysis" in st.session_state and "transcript" in st.session_state and not st.session_state.get("audio_saved", False):
        today_str = datetime.now().strftime("%Y%m%d")
        folder = f"data/records/{st.session_state.patient_id}/audio_entries"
        os.makedirs(folder, exist_ok=True)
        already_saved = any(today_str in fname for fname in os.listdir(folder))
        if already_saved:
            st.info("📅 Voice diary for today already saved. Cannot save again.")
        else:
            if st.button("💾 Save Voice Diary & Analysis"):
                try:
                    save_path = f"{folder}/audio_{today_str}.txt"
                    with open(save_path, "w", encoding="utf-8") as f:
                        f.write(f"Hasta ID: {st.session_state.patient_id}\n")
                        f.write(f"Tarih: {today_str}\n\n")
                        f.write("📝 Transcript:\n")
                        f.write(st.session_state["transcript"] + "\n\n")
                        f.write("📊 NLP Analysis:\n")
                        f.write(f"1. Sentiment Score: {st.session_state['audio_analysis']['sentiment_score']:.2f}\n")
                        f.write(f"2. Subjectivity Score: {st.session_state['audio_analysis']['subjectivity_score']:.2f}\n")
                        f.write(f"3. Emotion: {st.session_state['audio_analysis']['emotion']}\n")
                    # Save audio file
                    audio_folder = f"data/audio/{st.session_state.patient_id}"
                    os.makedirs(audio_folder, exist_ok=True)
                    audio_path = f"{audio_folder}/uploaded_{today_str}_{datetime.now().strftime('%H%M%S')}.wav"
                    with open(audio_path, "wb") as f:
                        f.write(st.session_state.audio_bytes)
                    st.success(f"🎵 Voice diary and analysis saved: `{save_path}`")
                    st.session_state.audio_saved = True
                except Exception as e:
                    st.error(f"Error during save: {str(e)}")

    # Emotional Congruence Index
    st.header("🔍 Emotional Compatibility Score")
    st.markdown("_This section assesses the emotional coherence between written, voice, and facial expression analyses._")
    if "emotion_consistency_saved" not in st.session_state:
        st.session_state["emotion_consistency_saved"] = False
    face_emotion = st.session_state.get("video_result", {}).get("dominant_emotion")
    text_emotion = st.session_state.get("text_analysis", {}).get("analysis", {}).get("emotion")
    voice_emotion = st.session_state.get("audio_analysis", {}).get("emotion")
    # Compatibility analysis
    if face_emotion and text_emotion and voice_emotion:
        uyum_durumu, yorum = compute_consistency(None, text_emotion, voice_emotion, face_emotion)
        st.subheader("🧭 Emotional Compatibility Result")
        st.markdown(f"- **Written Text Emotion:** {text_emotion}")
        st.markdown(f"- **Voice Diary Emotion:** {voice_emotion}")
        st.markdown(f"- **Facial Expression Emotion:** {face_emotion}")
        st.success(f"**Compatibility Status:** {uyum_durumu}")
        st.info(f"**Comment:** {yorum}")
        # Save the result
        st.session_state["emotion_consistency_result"] = {
            "uyum_durumu": uyum_durumu,
            "yorum": yorum,
            "text_emotion": text_emotion,
            "voice_emotion": voice_emotion,
            "face_emotion": face_emotion
        }
        # Save button
        if not st.session_state.get("emotion_consistency_saved", False):
            if st.button("💾 Save Emotional Compatibility Result"):
                try:
                    today_date_str = datetime.now().strftime("%Y%m%d")
                    folder = f"data/records/{st.session_state.patient_id}/emotion_consistency"
                    os.makedirs(folder, exist_ok=True)
                    save_path = f"{folder}/emotion_consistency_{today_date_str}.json"
                    with open(save_path, "w", encoding="utf-8") as f:
                        json.dump(st.session_state["emotion_consistency_result"], f, ensure_ascii=False, indent=4)
                    st.success(f"🎯 Emotional coherence analysis saved successfully: `{save_path}`")
                    st.session_state["emotion_consistency_saved"] = True
                except Exception as e:
                    st.error(f"Error during save: {str(e)}")
        else:
            st.info("📅 Emotional coherence data already saved for today.")
    else:
        st.warning("Insufficient data for emotional coherence analysis. Please complete analyses.")

    # Daily Emotional State Tracking
    st.header("Daily Emotional State Monitoring")
    mood_data, mood_avg = daily_mood_form()
    today_date_str = datetime.now().strftime("%Y%m%d")
    folder = f"data/records/{st.session_state.patient_id}/mood_tracking"
    os.makedirs(folder, exist_ok=True)
    today_filename = f"{folder}/mood_{today_date_str}.csv"
    if os.path.exists(today_filename):
        st.info("📅 Today's emotional state already recorded.")
    else:
        if st.button("💾 Save Daily Emotional State"):
            mood_df = pd.DataFrame([mood_data])
            mood_df["average"] = mood_avg
            mood_df.to_csv(today_filename, index=False)
            st.success(f"Daily emotional state saved successfully: `{today_filename}`")

    # Patient Records Panel
    def display_patient_records():
        st.header("🗂️ Clinical Records")
        all_patients = list_patient_ids()
        if all_patients:
            selected_patient = st.selectbox("🔎 Select Patient", all_patients, key="sidebar_patient_selectbox")
            if selected_patient:
                st.subheader(f"📁 {selected_patient} - Clinical Records")
                all_entries = record_loader.load_all_entries(selected_patient)
                if all_entries:
                    records = []
                    for entry in all_entries:
                        lines = entry["content"].splitlines()
                        record = {"File": entry["filename"]}
                        for line in lines:
                            if line.startswith("PHQ-9 Score"):
                                record["PHQ-9"] = line.split(":")[1].strip()
                            elif "Emotion Score" in line:
                                record["Emotion Score"] = line.split(":")[1].strip()
                            elif "Overall Emotional Tone" in line:
                                record["Emotion Tone"] = line.split(":")[1].strip()
                        records.append(record)
                    df = pd.DataFrame(records)
                    st.dataframe(df)
                    csv_data = df.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 Download CSV", csv_data, file_name=f"{selected_patient}_data.csv", mime="text/csv")
                else:
                    st.info("No records found for this patient.")
        else:
            st.info("No registered patients yet.")

    def display_psychometric_tracking(patient_id):
        st.markdown("## 📊 **Weekly Psychometric Monitoring**")
        for form in ["PHQ9", "GAD7", "PSS10"]:
            data = load_form_history(patient_id, form)
            if data is not None and not data.empty:
                st.markdown(f"### 📈 {form}")
                fig, ax = plt.subplots()
                ax.plot(pd.to_datetime(data["date"]), data["score"], marker="o")
                ax.set_title(f"{form} Score Time Series")
                ax.set_xlabel("Date")
                ax.set_ylabel("Score")
                ax.grid(True)
                st.pyplot(fig)
            else:
                st.info(f"{form} data not yet entered.")
        st.markdown("## 📊 **Monthly Psychometric Monitoring**")
        for form in ["PSQI", "IESR"]:
            data = load_form_history(patient_id, form)
            if data is not None and not data.empty:
                st.markdown(f"### 📈 {form}")
                fig, ax = plt.subplots()
                ax.plot(pd.to_datetime(data["date"]), data["score"], marker="o")
                ax.set_title(f"{form} Score Time Series")
                ax.set_xlabel("Date")
                ax.set_ylabel("Score")
                ax.grid(True)
                st.pyplot(fig)
            else:
                st.info(f"{form} data not yet entered.")

    def display_sidebar(patient_id):
        # Banner/Visual
        try:
            st.image("assets/neuroclarity_banner.png", use_container_width=True)
        except:
            st.warning("Banner image failed to load.")
        st.markdown("<h1 style='text-align: center; font-size: 32px;'>🤖 PsyBot – Psychoeducation & Support</h1>", unsafe_allow_html=True)
        chatbot_interface()
        display_patient_records()
        display_psychometric_tracking(patient_id)

    with st.sidebar:
        display_sidebar(st.session_state.patient_id)

    # Load Apple Health Data (Optional)
    st.header("📱 Apple Health Data (Optional)")
    with st.expander("📦 How to Export Your Data from Apple Health?"):
        st.markdown("""
        To export your health data from the iPhone's 'Health' app:
        1. Open the 'Health' app on your iPhone
        2. Tap the profile icon at the bottom right
        3. Select "Export All Health Data"
        4. Confirm with "Export"
        5. The data will be prepared as a `.zip` file  
        6. Send this `.zip` via AirDrop / iCloud / Email to your computer
        7. Upload it to this app ✅
        > 🔒 This process only runs with your permission. The data is processed only temporarily for analysis.
        """)
    st.markdown("""
    This step is optional. If you upload your exported `.zip` file from Apple Health,
    the app can enhance its analyses with steps and sleep data.
    """)
    zip_file = st.file_uploader("Upload HealthKit export (.zip)", type=["zip"])
    if zip_file:
        steps_df, sleep_df, error = parse_healthkit_zip(zip_file)
        if error:
            st.error(f"Error processing file: {error}")
        else:
            display_healthkit_insights(steps_df, sleep_df, patient_id=st.session_state.patient_id)
    else:
        st.info("Health data not uploaded – optional step.")

    # Manual health data entry
    today_date_str = datetime.now().strftime("%Y%m%d")
    folder = f"data/records/{st.session_state.patient_id}/healthkit"
    os.makedirs(folder, exist_ok=True)
    today_filename = f"{folder}/manual_entry_{today_date_str}.csv"
    if os.path.exists(today_filename):
        st.info("📅 Manual step & sleep entry for today already recorded.")
    else:
        st.markdown("---")
        st.subheader("👟 Manual Step & Sleep Entry (Optional)")
        manual_date = st.date_input("Select Date", value=datetime.today())
        manual_steps = st.number_input("Number of Steps", min_value=0, step=100)
        manual_sleep = st.number_input("Sleep Duration (hours)", min_value=0.0, step=0.5, format="%.1f")
        if st.button("📥 Save Data (Manual)"):
            manual_df = pd.DataFrame([{
                "date": manual_date.strftime("%Y-%m-%d"),
                "steps": manual_steps,
                "hours": manual_sleep
            }])
            manual_df.to_csv(today_filename, index=False)
            st.success(f"Manual health data saved: `{today_filename}`")

    # Monthly Lab Test (PDF / JPG / PNG)
    st.sidebar.markdown("## 🧪 Monthly Lab Test (PDF / JPG / PNG)")
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Tesseract path (Windows)
    # 1️⃣ Upload File
    lab_file = st.sidebar.file_uploader("Upload Lab Test File", type=["pdf", "png", "jpg", "jpeg"])
    today_date_str = datetime.now().strftime("%Y%m%d")
    lab_folder = f"data/records/{st.session_state.patient_id}/lab_results"
    os.makedirs(lab_folder, exist_ok=True)
    lab_file_base = f"{lab_folder}/lab_result_{today_date_str}"
    lab_summary_path = f"{lab_file_base}_summary.txt"
    # Check if already exists
    already_exists = any(
        os.path.exists(f"{lab_file_base}.{ext}") for ext in ["pdf", "png", "jpg", "jpeg"]
    ) and os.path.exists(lab_summary_path)
    # If new file uploaded and not already processed
    if lab_file and not already_exists:
        file_ext = lab_file.name.split(".")[-1].lower()
        save_path = f"{lab_file_base}.{file_ext}"
        # Save the uploaded file
        with open(save_path, "wb") as f:
            f.write(lab_file.getbuffer())
        st.sidebar.success(f"✅ File saved: {save_path}")
        # Preview the file
        st.sidebar.markdown("### 📋 File Preview")
        if file_ext == "pdf":
            base64_pdf = base64.b64encode(lab_file.getvalue()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
            st.sidebar.markdown(pdf_display, unsafe_allow_html=True)
        elif file_ext in ["jpg", "jpeg", "png"]:
            st.sidebar.image(lab_file, caption="Lab Test Image", use_container_width=True)
        # Button to analyze
        if st.sidebar.button("🧠 Analyze and Save Lab Test"):
            try:
                # OCR or PDF text extraction
                if file_ext == "pdf":
                    extracted_text = extract_text_from_pdf(save_path)
                else:
                    image = Image.open(save_path)
                    extracted_text = pytesseract.image_to_string(image)
                # Show extracted text
                st.sidebar.markdown("### 📄 OCR Extracted Text")
                st.sidebar.text_area("Extracted OCR Text", extracted_text[:1000])
                # Use GPT for interpretation
                lab_summary = interpret_lab_results(extracted_text)
                st.session_state.lab_summary = lab_summary
                if not lab_summary.strip():
                    st.sidebar.warning("⚠️ Empty response from GPT. The text content may be incompatible.")
                else:
                    # Save interpretation
                    with open(lab_summary_path, "w", encoding="utf-8") as f:
                        f.write(lab_summary)
                    st.sidebar.success("✅ Clinical interpretation generated and saved.")
                    st.sidebar.subheader("📋 Clinical Assessment")
                    st.sidebar.markdown(lab_summary)
            except Exception as e:
                st.sidebar.error(f"Error during analysis: {str(e)}")
    elif already_exists:
        st.sidebar.info("📅 Lab test already recorded this month. Cannot upload again.")

    # Show analysis summary on main page if available
    if "lab_summary" in st.session_state:
        st.subheader("🧪 Lab Test Analysis Summary")
        st.markdown(st.session_state.lab_summary)

    # Forms & Controls
    def can_submit_form(patient_id, form_type, frequency):
        folder = f"data/records/{patient_id}/form_submissions"
        os.makedirs(folder, exist_ok=True)
        file_path = f"{folder}/submission_dates.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                submission_dates = json.load(f)
        else:
            submission_dates = {}
        last_submission = submission_dates.get(form_type)
        if last_submission:
            last_date = datetime.strptime(last_submission, "%Y-%m-%d")
            if frequency == "weekly" and last_date > datetime.now() - timedelta(weeks=1):
                return False
            if frequency == "monthly" and last_date > datetime.now() - timedelta(days=30):
                return False
        return True

    def update_submission_date(patient_id, form_type):
        folder = f"data/records/{patient_id}/form_submissions"
        os.makedirs(folder, exist_ok=True)
        file_path = f"{folder}/submission_dates.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                submission_dates = json.load(f)
        else:
            submission_dates = {}
        submission_dates[form_type] = datetime.now().strftime("%Y-%m-%d")
        with open(file_path, "w") as f:
            json.dump(submission_dates, f)

    st.sidebar.markdown("<span style='font-size:22px; font-weight:bold;'>📋 Select Form</span>", unsafe_allow_html=True)
    selected_form = st.sidebar.selectbox(
        "Select a Form",
        ("None", "GAD-7 – Anxiety (Weekly)", "PSS-10 – Stress (Weekly)",
         "PSQI – Sleep (Monthly)", "PHQ-9 – Depression (Weekly)", "IES-R – Trauma (Monthly)")
    )
    # Save form data
    if selected_form != "None":
        if selected_form.startswith("PSQI"):
            if can_submit_form(st.session_state.patient_id, "PSQI", "monthly"):
                psqi_score, psqi_severity = psqi_form()
                if st.button("💾 Save PSQI Score", key="psqi_save_button"):
                    save_form_score(st.session_state.patient_id, "PSQI", psqi_score, psqi_severity)
                    update_submission_date(st.session_state.patient_id, "PSQI")
                    st.success("PSQI score successfully saved.")
            else:
                st.warning("This form has already been saved this month.")
        elif selected_form.startswith("GAD-7"):
            if can_submit_form(st.session_state.patient_id, "GAD7", "weekly"):
                from components.forms.gad7_form import gad7_form
                gad_score, gad_severity = gad7_form()
                if st.button("💾 Save GAD-7 Score", key="gad7_save_button"):
                    save_form_score(st.session_state.patient_id, "GAD7", gad_score, gad_severity)
                    update_submission_date(st.session_state.patient_id, "GAD7")
                    st.success("GAD-7 score successfully saved.")
            else:
                st.warning("This form has already been saved this week.")
        elif selected_form.startswith("PSS-10"):
            if can_submit_form(st.session_state.patient_id, "PSS10", "weekly"):
                from components.forms.pss10_form import pss10_form
                pss_score, pss_severity = pss10_form()
                if st.button("💾 Save PSS-10 Score", key="pss10_save_button"):
                    save_form_score(st.session_state.patient_id, "PSS10", pss_score, pss_severity)
                    update_submission_date(st.session_state.patient_id, "PSS10")
                    st.success("PSS-10 score successfully saved.")
            else:
                st.warning("This form has already been saved this week.")
        elif selected_form.startswith("PHQ-9"):
            if can_submit_form(st.session_state.patient_id, "PHQ9", "weekly"):
                from components.forms.phq9_form import phq9_form
                phq_score, severity = phq9_form()
                if st.button("💾 Save PHQ-9 Score", key="phq9_save_button"):
                    save_form_score(st.session_state.patient_id, "PHQ9", phq_score, severity)
                    update_submission_date(st.session_state.patient_id, "PHQ9")
                    st.success("PHQ-9 score successfully saved.")
            else:
                st.warning("This form has already been saved this week.")
        elif selected_form.startswith("IES-R"):
            if can_submit_form(st.session_state.patient_id, "IESR", "monthly"):
                from components.forms.iesr_form import iesr_form
                iesr_score, iesr_severity = iesr_form()
                if st.button("💾 Save IES-R Score", key="iesr_save_button"):
                    save_form_score(st.session_state.patient_id, "IESR", iesr_score, iesr_severity)
                    update_submission_date(st.session_state.patient_id, "IESR")
                    st.success("IES-R score successfully saved.")
            else:
                st.warning("This form has already been saved this month.")

    # Analysis Buttons
    st.markdown("---")
    st.subheader("📊 Analysis Options")
    if st.button("📅 Analyze Data Daily"):
        daily_analysis = generate_daily_analysis(
            patient_id=st.session_state.patient_id,
            mood_data=mood_data if mood_data else {},
            journal_text=text.strip() if text else "",
            transcript=st.session_state.get("transcript", "")
        )
        st.markdown("### Daily Analysis Results")
        st.write(daily_analysis)
    if st.button("📅 Analyze Data Weekly"):
        weekly_analysis = generate_weekly_analysis(st.session_state.patient_id)
        st.markdown("### Weekly Analysis Results")
        st.write(weekly_analysis)
    if st.button("📅 Analyze Data Monthly"):
        monthly_analysis = generate_weekly_analysis(st.session_state.patient_id)
        st.markdown("### Monthly Analysis Results")
        st.write(monthly_analysis)

    # Daily report
    st.markdown("---")
    st.subheader("🧾 Patient Daily Report Save")
    if st.button("💾 Save All Inputs as Patient Diary"):
        report_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_folder = f"data/records/{st.session_state.patient_id}/full_reports"
        os.makedirs(report_folder, exist_ok=True)
        pdf_path = f"{report_folder}/full_entry_{report_time_str}.pdf"
        # Load forms data
        weekly_forms = {
            "PHQ9": load_form_history(st.session_state.patient_id, "PHQ9"),
            "GAD7": load_form_history(st.session_state.patient_id, "GAD7"),
            "PSS10": load_form_history(st.session_state.patient_id, "PSS10"),
        }
        monthly_forms = {
            "PSQI": load_form_history(st.session_state.patient_id, "PSQI"),
            "IESR": load_form_history(st.session_state.patient_id, "IESR"),
        }
        # Get analysis data
        daily_analysis_result = generate_daily_analysis(
            patient_id=st.session_state.patient_id,
            mood_data=mood_data if mood_data else {},
            journal_text=text.strip() if text else "",
            transcript=st.session_state.get("transcript", "")
        )
        weekly_analysis_result = generate_weekly_analysis(st.session_state.patient_id)
        monthly_analysis_result = generate_weekly_analysis(st.session_state.patient_id)

        # Compatibility analysis
        if 'analysis' in locals() and 'result' in locals():
            face_emotion_val = result.get("dominant_emotion")
            text_emotion_val = analysis.get("emotion")
            voice_emotion_val = analysis.get("emotion")
            uyum, yorum = compute_consistency(None, text_emotion_val, voice_emotion_val, face_emotion_val)
            emotion_consistency_result = (
                f"Uyum Result: {uyum}\nComment: {yorum}" if uyum and yorum else None
            )

        # Export PDF
        export_full_pdf(
            patient_id=st.session_state.patient_id,
            mood_data="mood_data" in locals() and mood_data or None,
            manual_steps=manual_steps if 'manual_steps' in locals() else None,
            manual_sleep=manual_sleep if 'manual_sleep' in locals() else None,
            weekly_forms=weekly_forms,
            monthly_forms=monthly_forms,
            lab_results=lab_summary,
            apple_health_data={
                "steps": steps_df,
                "sleep": sleep_df,
            },
            daily_analysis=daily_analysis_result,
            weekly_analysis=weekly_analysis_result,
            monthly_analysis=monthly_analysis_result,
            emotion_consistency_result=emotion_consistency_result,
            output_path=pdf_path
        )
        if os.path.exists(pdf_path):
            st.success(f"📄 Saved as PDF: `{pdf_path}`")
            st.session_state.pdf_path = pdf_path
            # Show preview of the PDF
            st.markdown("### 📑 PDF Preview")
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)