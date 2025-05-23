import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase
from utils.video_emotion import analyze_video_emotions
import cv2
import os
import datetime

def video_input(patient_id: str):
    st.subheader("🎥 Video and Facial Expression Analysis")
    option = st.radio("How would you like to upload the video?", ["Upload File", "Record with Camera"])

    if option == "Upload File":
        video_file = st.file_uploader("Upload video (.mp4)", type=["mp4"])
        if video_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = f"data/video/{patient_id}"
            os.makedirs(folder, exist_ok=True)
            path = f"{folder}/uploaded_{timestamp}.mp4"
            with open(path, "wb") as f:
                f.write(video_file.read())
            st.success(f"🎬 Video uploaded: `{path}`")
            result = analyze_video_emotions(path)
            _show_video_analysis(result)
    else:
        class Recorder(VideoProcessorBase):
            def __init__(self): self.frames = []
            def recv(self, frame):
                self.frames.append(frame.to_ndarray(format="bgr24"))
                return frame
        ctx = webrtc_streamer(
            key="video",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=Recorder,
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            async_processing=True
        )
        if ctx.video_processor:
            if st.button("📹 Stop Recording and Analyze"):
                frames = ctx.video_processor.frames
                if not frames:
                    st.warning("⚠️ Recording failed.")
                    return
                folder = f"data/video/{patient_id}"
                os.makedirs(folder, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = f"{folder}/recorded_{timestamp}.mp4"
                height, width, _ = frames[0].shape
                out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))
                for f in frames:
                    out.write(f)
                out.release()
                st.success(f"📼 Recording saved: `{path}`")
                result = analyze_video_emotions(path)
                _show_video_analysis(result)

def _show_video_analysis(result):
    if "error" in result:
        st.error(result["error"])
    else:
        st.success(f"🏷️ Dominant Emotion: {result['dominant_emotion']}")
        st.json(result["emotion_scores"])