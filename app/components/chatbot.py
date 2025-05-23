import streamlit as st
import openai
from textblob import TextBlob  # For sentiment analysis

openai.api_key = "YOUR_API_KEY"  # Set your OpenAI API key

def chatbot_interface():
    st.subheader("💬 Advanced Chat Panel")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": (
                "You are a mental health support chatbot. "
                "Respond empathically, ethically, and based on psychoeducation. "
                "Do not diagnose. Suggest support hotlines in crisis when needed."
            )}
        ]
    # Display chat history (excluding the system prompt)
    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        elif msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
    user_input = st.chat_input("Would you like to ask or share something?")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        # Sentiment analysis
        sentiment = TextBlob(user_input).sentiment
        if sentiment.polarity < -0.5:
            st.warning("You seem upset. Would you like some help?")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=st.session_state.chat_history,
                temperature=0.7
            )
            reply = response.choices[0].message["content"]
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)
        except Exception as e:
            st.error(f"Chatbot error: {str(e)}")