import streamlit as st

def journal_input():
    # Subheader for the journal entry section
    st.subheader("📔 Journal Entry")
    
    # Text area for users to enter their thoughts
    journal_text = st.text_area("Share your thoughts of today with us...", height=200)
    
    return journal_text