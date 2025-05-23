![image](https://github.com/user-attachments/assets/ece41f6f-6f2c-4036-a596-94460c7d2134)
# 🧠 Neuro-Clarity: Psychology, Psychiatry & Multimodal Mental Health Dashboard

**Neuro-Clarity** is an AI-powered, multimodal mental health monitoring system built with Streamlit. It allows clinicians, researchers, and digital health developers to collect and analyze diverse patient data (text, audio, video, health metrics) to gain structured insight into mood, psychiatric risk, and emotional congruence across modalities.

---

## 📌 Core Capabilities

### 👤 Patient Management
- Patient registry system with persistent session tracking
- View and select historical records for each patient

### 🧠 Daily & Weekly Evaluation Tools
- **Mood Tracker**: Quantitative daily mood input with CSV export
- **Diary NLP**: Sentiment, subjectivity, and emotion extraction via GPT-4
- **Voice Diary**: Audio transcription + emotion profiling
- **Facial Emotion**: Video upload and recognition of dominant emotion
- **Emotional Consistency**: Text vs voice vs face emotion alignment score

### 🧪 Clinical Instruments
- ✅ PHQ-9 – Depression
- ✅ GAD-7 – Anxiety
- ✅ PSS-10 – Stress
- ✅ PSQI – Sleep Quality
- ✅ IES-R – Trauma Impact
- Submission locking logic (weekly/monthly frequency enforced)

### 📊 Health Integration
- 🔄 Apple HealthKit data via `.zip`: Steps & Sleep visualized
- ⌨️ Manual entry for sleep/step counts
- 📑 PDF / Image lab results OCR + GPT-based summary interpretation

### 📄 Reporting & Export
- Patient records summary with CSV export
- Full diagnostic session export to structured PDF
- Daily/weekly/monthly AI analysis results

---

## 📂 Folder Structure

```
neuro-clarity/
├── main.py                       # Entry point
├── components/                   # UI logic for forms, chatbot, etc.
├── utils/                        # NLP, emotion analysis, lab OCR, export
├── data/                         # Patient data files (text, audio, video)
│   └── records/                  # Per-patient structured logs
├── assets/                       # UI banners
├── .env                          # Your OpenAI API key
└── requirements.txt              # Python dependencies
```

---
https://github.com/user-attachments/assets/0acf4a4f-ca4e-4cb8-b61a-ab5683ecb2ab

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/mustafaras/Neuro-Clarity_Psychiatric_Psychologic_moodtracking.git
cd Neuro-Clarity_Psychiatric_Psychologic_moodtracking
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your OpenAI API Key:

Create a `.env` file:

```env
OPENAI_API_KEY=your-key-here
```

4. Run the app:

```bash
streamlit run main.py
```

---

## 💡 Tech Stack

- **Streamlit** – App interface
- **OpenAI API** – Sentiment & semantic analysis
- **PyTesseract / OCR** – Lab results interpretation
- **Pandas, Matplotlib, Plotly** – Analysis & plotting
- **WebRTC, AV** – Real-time webcam/video integration
- **Custom NLP & Emotion Models** – GPT + facial/audio emotion

---

## 🔐 Privacy

All data is stored locally and saved **only upon explicit user action**. No remote storage or automatic cloud sync. Intended for **clinical prototyping**, **academic projects**, and **ethical digital psychiatry tools**.

---

## 📜 License

Licensed under the MIT License © 2025 [mustafaras](https://github.com/mustafaras)  
See [`LICENSE`](LICENSE) for full terms.

---

## 🙏 Acknowledgments

- Powered by GPT-4 from OpenAI
- Clinical logic aligned with DSM-5 and ICD-11 standards
- Emotional analysis inspired by state-of-the-art multimodal AI

MIT License

Copyright (c) 2025 [mustafaras](https://github.com/mustafaras)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
