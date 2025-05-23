import streamlit as st

def psqi_form():
    # Markdown header for PQSI title
    st.markdown("🛌 **PSQI – Pittsburgh Sleep Quality Index** _(Assess the last month)_")
    
    # Section 1: Sleep habits
    st.markdown("### 1️⃣ Sleep Habits")
    sleep_time = st.time_input("What time did you usually go to bed in the last month?", key="psqi_sleep_time")
    sleep_latency = st.number_input("How long did it typically take you to fall asleep in the last month? (minutes)", min_value=0, step=1, key="psqi_sleep_latency")
    wake_time = st.time_input("What time did you usually wake up in the last month?", key="psqi_wake_time")
    actual_sleep_hours = st.number_input("How many hours of sleep did you get per night on average in the last month (hours)", min_value=0.0, step=0.5, format="%.1f", key="psqi_actual_sleep_hours")
    
    # Section 2: Sleep problems
    st.markdown("### 2️⃣ Sleep Problems")
    problems = {
        "Difficulty falling asleep within 30 minutes": "Never",
        "Waking up during the night or early morning": "Never",
        "Getting out of bed due to needing to urinate": "Never",
        "Having difficulty breathing (such as sleep apnea)": "Never",
        "Restless, restlessness, or tossing and turning": "Never",
        "Hot flashes or night sweats": "Never",
        "Vivid dreams or nightmares": "Never",
        "Pain or discomfort": "Never",
        "Other issues": "Never"
    }
    
    # Frequency mapping for scores conversion
    frequency_mapping = {
        "Never": 0,
        "Once a week or less": 1,
        "2-3 times per week": 2,
        "Nearly every night": 3
    }
    
    problem_scores = {}
    for idx, (problem, default) in enumerate(problems.items()):
        problem_scores[problem] = st.radio(
            f"How often did this problem occur in the last month?",
            list(frequency_mapping.keys()),
            horizontal=True,
            key=f"psqi_problem_{idx}"  # Unique key for each problem
        )
    
    # Section 3: Sleep medication use
    st.markdown("### 3️⃣ Sleep Medication Use")
    sleep_medication = st.radio(
        "How often did you take any medication to help you sleep in the last month?",
        list(frequency_mapping.keys()),
        horizontal=True,
        key="psqi_sleep_medication"
    )
    
    # Section 4: Daytime functioning
    st.markdown("### 4️⃣ Daytime Functioning")
    daytime_drowsiness = st.radio(
        "How often did you feel excessively sleepy or drowsy during the day in the last month?",
        list(frequency_mapping.keys()),
        horizontal=True,
        key="psqi_daytime_drowsiness"
    )
    daytime_functioning = st.radio(
        "How difficult was it for you to perform your usual daily activities during the last month due to excessive sleepiness or drowsiness?",
        ["Not at all", "Slightly", "Moderately", "Markedly"],
        horizontal=True,
        key="psqi_daytime_functioning"
    )
    
    # Section 5: Overall sleep quality
    st.markdown("### 5️⃣ Overall Sleep Quality")
    overall_sleep_quality = st.radio(
        "Overall, how would you rate the quality of your sleep in the last month?",
        ["Very Good", "Good", "Fair", "Poor"],
        horizontal=True,
        key="psqi_overall_quality"
    )
    
    # Calculate total score and severity level
    total_score = sum([frequency_mapping[problem_scores[problem]] for problem in problems]) + frequency_mapping[sleep_medication] + frequency_mapping[daytime_drowsiness]

    if total_score <= 5:
        severity = "Normal Sleep Quality"
    elif total_score <= 10:
        severity = "Mild Sleep Problem"
    else:
        severity = "Moderate to Severe Sleep Problem"

    st.markdown(f"**Total Score:** {total_score} / 21")
    st.markdown(f"**Assessment:** {severity}")

    return total_score, severity