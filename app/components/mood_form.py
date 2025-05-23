import streamlit as st

def daily_mood_form():
    # Subheader for the daily mood tracking survey
    st.subheader("📅 Daily Mood Tracking Survey")
    
    mood = {}
    
    # Slider for energy level
    mood["Energy"] = st.slider("⚡ How high was your energy?", 0, 10, 5)
    
    # Slider for happiness level
    mood["Happiness"] = st.slider("😊 How happy did you feel?", 0, 10, 5)
    
    # Slider for stress level
    mood["Stress"] = st.slider("😣 What was your stress level?", 0, 10, 5)
    
    # Slider for anxiety level
    mood["Anxiety"] = st.slider("😟 How high was your anxiety?", 0, 10, 5)
    
    # Slider for self-confidence
    mood["Self-Confidence"] = st.slider("💪 How confident did you feel?", 0, 10, 5)
    
    # Calculate the average mood score
    avg_mood = sum(mood.values()) / len(mood)
    
    # Display the overall mood score
    st.metric("📈 Overall Mood Score", f"{avg_mood:.2f} / 10")
    
    return mood, avg_mood