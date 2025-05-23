import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
from datetime import datetime

def display_healthkit_insights(steps_df, sleep_df, patient_id="anonymous"):
    st.header("📊 Apple Health Data Analysis")
    # Health data folder
    folder = f"data/records/{patient_id}/healthkit"
    # If manual CSVs exist, include them
    if os.path.exists(folder):
        manual_files = [f for f in os.listdir(folder) if f.startswith("manual_entry")]
        manual_data = []
        for file in manual_files:
            path = os.path.join(folder, file)
            df = pd.read_csv(path)
            manual_data.append(df)
        if manual_data:
            manual_df = pd.concat(manual_data)
            steps_df = pd.concat([steps_df, manual_df[["date", "steps"]]])
            sleep_df = pd.concat([sleep_df, manual_df[["date", "hours"]]])
            # It is assumed that "hours" is the column for sleep duration

    # Filter for the last 7 days
    recent_days = pd.Timestamp.today().normalize() - pd.Timedelta(days=7)
    steps_recent = steps_df[steps_df["date"] >= recent_days]
    sleep_recent = sleep_df[sleep_df["date"] >= recent_days]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚶‍♂️ Daily Step Count (Last 7 Days)")
        fig1, ax1 = plt.subplots()
        ax1.bar(steps_recent["date"], steps_recent["steps"], color="green")
        ax1.set_ylabel("Steps")
        ax1.set_xticklabels(steps_recent["date"], rotation=45)
        st.pyplot(fig1)
    with col2:
        st.subheader("🛌 Sleep Duration (Hours, Last 7 Days)")
        fig2, ax2 = plt.subplots()
        ax2.plot(sleep_recent["date"], sleep_recent["hours"], marker='o', color="blue")
        ax2.set_ylabel("Sleep (hours)")
        ax2.set_xticklabels(sleep_recent["date"], rotation=45)
        st.pyplot(fig2)
    # Average sleep duration
    if not sleep_recent.empty:
        avg_sleep = sleep_recent["hours"].mean()
        st.metric("🌙 Avg Sleep (7d)", f"{avg_sleep:.2f} hours")
    # Correlation
    merged = pd.merge(steps_df, sleep_df, on="date", how="inner")
    if not merged.empty:
        st.subheader("📈 Step – Sleep Correlation")
        corr = merged.corr()
        fig3, ax3 = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax3)
        st.pyplot(fig3)
    else:
        st.info("Not enough matching data found (steps & sleep).")
    # 🔸 Save Data Button
    if st.button("💾 Save Health Data"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(folder, exist_ok=True)
        steps_df.to_csv(f"{folder}/steps_{timestamp}.csv", index=False)
        sleep_df.to_csv(f"{folder}/sleep_{timestamp}.csv", index=False)
        st.success(f"Data saved: `{folder}`")