import os
import json
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Turkish character support
pdfmetrics.registerFont(TTFont('DejaVu', 'assets/fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVu-Bold', 'assets/fonts/DejaVuSans-Bold.ttf'))

def export_report(patient_id, output_path="output.pdf"):
    # Fetch or define your data retrieval functions here
    journal_text = get_latest_journal_text(patient_id)
    analysis = get_latest_nlp_analysis(patient_id)
    transcript = get_latest_transcript(patient_id)
    video_analysis = get_latest_video_analysis(patient_id)
    emotional_consistency_result = get_emotional_consistency(patient_id)
    daily_analysis = get_daily_analysis(patient_id)
    weekly_analysis = get_weekly_analysis(patient_id)
    monthly_analysis = get_monthly_analysis(patient_id)
    mood_data = get_mood_data(patient_id)
    weekly_forms = get_weekly_forms(patient_id)
    monthly_forms = get_monthly_forms(patient_id)
    lab_results = get_latest_lab_results(patient_id)

    # Load most recent audio transcript if missing
    audio_path = f"data/records/{patient_id}/audio_entries"
    if not transcript and os.path.exists(audio_path):
        files = sorted(os.listdir(audio_path), reverse=True)
        for f in files:
            if f.endswith(".txt"):
                transcript = get_latest_file_text(os.path.join(audio_path, f))
                break

    # PDF creation
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []

    # Styles
    normal = ParagraphStyle('Normal', fontName='DejaVu', fontSize=10, leading=14)
    bold = ParagraphStyle('Bold', fontName='DejaVu-Bold', fontSize=12, leading=16)

    def add_section(title, content):
        story.append(Spacer(1, 12))
        story.append(Paragraph(title, bold))
        story.append(Spacer(1, 6))
        if content:
            if isinstance(content, str):
                story.append(Paragraph(content.replace("\n", " "), normal))
            else:
                story.append(Paragraph(str(content), normal))
        else:
            story.append(Paragraph("No data found.", normal))

    def add_table_from_dict(data_dict):
        if data_dict:
            table = Table([list(data_dict.keys()), list(data_dict.values())])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No data found.", normal))

    # Title and date
    story.append(Paragraph("🧠 NeuroClarity Mental Health Report", bold))
    story.append(Paragraph(f"Patient ID: {patient_id}", normal))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal))

    # Sections
    add_section("📔 Daily Written Diary", journal_text)

    add_section("📊 NLP Analysis", (
        f"""
        Emotion Score: {analysis.get('sentiment_score', 'N/A')}<br/>
        Subjectivity: {analysis.get('subjectivity_score', 'N/A')}<br/>
        Emotion: {analysis.get('emotion', 'N/A')}
        """ if analysis else None
    ))

    add_section("🎤 Transcript of Audio Diary", transcript)

    add_section("🎥 Video Analysis Results", (
        f"""
        Dominant Emotion: {video_analysis.get('dominant_emotion', 'N/A')}<br/>
        {"<br/>".join([f"{k}: {v:.2f}" for k, v in video_analysis.get("emotion_scores", {}).items()])}
        """ if video_analysis else None
    ))

    add_section("🔄 Emotional Consistency Analysis", emotional_consistency_result)
    add_section("📅 Daily Analysis Results", daily_analysis)
    add_section("📈 Weekly Analysis Results", weekly_analysis)
    add_section("📈 Monthly Analysis Results", monthly_analysis)

    # Mood data
    story.append(Spacer(1, 12))
    story.append(Paragraph("📊 Daily Emotional State", bold))
    add_table_from_dict(mood_data)

    # Psychometric forms
    for form_type, form_data in (weekly_forms or {}).items():
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"📋 {form_type} Results", bold))
        if isinstance(form_data, pd.DataFrame) and not form_data.empty:
            table = Table([form_data.columns.to_list()] + form_data.values.tolist())
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No data found.", normal))

    for form_type, form_data in (monthly_forms or {}).items():
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"📋 {form_type} Results", bold))
        if isinstance(form_data, pd.DataFrame) and not form_data.empty:
            table = Table([form_data.columns.to_list()] + form_data.values.tolist())
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No data found.", normal))

    # Lab results
    add_section("🧪 Lab Test Results", lab_results)

    # Build PDF
    doc.build(story)
