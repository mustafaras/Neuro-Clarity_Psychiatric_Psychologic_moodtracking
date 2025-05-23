import streamlit as st

QUESTIONS = [
    "1. Hiçbir şeyden zevk almama",
    "2. Kendinizi üzgün, depresif ya da umutsuz hissetme",
    "3. Uykuya dalmakta zorlanma, sık uyanma ya da aşırı uyuma",
    "4. Yorgun hissetme ya da enerjinin tükenmiş olması",
    "5. İştahsızlık veya aşırı yeme",
    "6. Kendinizi başarısız hissetme veya kendinizi suçlama",
    "7. Konsantrasyon güçlüğü",
    "8. Diğer insanların fark edeceği şekilde yavaş hareket etme ya da aşırı huzursuz olma",
    "9. Kendinize zarar verme veya ölmek isteme düşünceleri"
]

OPTIONS = {
    "Hiç": 0,
    "Birkaç gün": 1,
    "Haftanın yarısı": 2,
    "Neredeyse her gün": 3
}

def phq9_form(form_id="default"):
    st.subheader("📝 PHQ-9 Depresyon Ölçeği")

    responses = []
    for idx, question in enumerate(QUESTIONS):
        response = st.radio(
            question,
            OPTIONS.keys(),
            horizontal=True,
            key=f"{form_id}_{idx}"
        )
        responses.append(OPTIONS[response])

    total_score = sum(responses)

    if total_score <= 4:
        severity = "Minimal"
    elif total_score <= 9:
        severity = "Hafif"
    elif total_score <= 14:
        severity = "Orta"
    elif total_score <= 19:
        severity = "Orta-Ağır"
    else:
        severity = "Ağır"

    st.success(f"Toplam Skor: {total_score} / 27")
    st.info(f"Depresyon Şiddeti: **{severity}**")

    return total_score, severity
