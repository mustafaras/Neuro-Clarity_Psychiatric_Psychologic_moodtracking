import streamlit as st

def psqi_form():
    st.markdown("🛌 **PSQI – Pittsburgh Uyku Kalitesi İndeksi** _(Son 1 haftayı değerlendirin)_")

    components = {
        "Uykuya dalma süresi": "Ne kadar sürede uykuya dalabildiniz?",
        "Toplam uyku süresi": "Gecelik toplam ortalama uyku süreniz nasıldı?",
        "Uyku verimliliği": "Gece yatağa yattığınız süreye göre gerçekten ne kadar uyudunuz?",
        "Uyku bozuklukları": "Gece boyunca uyanma, horlama, huzursuzluk yaşadınız mı?",
        "Uyku ilacı kullanımı": "Uyumak için ilaç kullanma ihtiyacınız oldu mu?",
        "Gündüz uykululuk": "Gün içinde uykulu hissettiniz mi?",
        "Genel uyku kalitesi": "Genel uyku kalitenizi nasıl değerlendirirsiniz?"
    }

    scores = {}
    for key, question in components.items():
        scores[key] = st.radio(
            question,
            ["0 - Hiç", "1 - Hafif", "2 - Orta", "3 - Şiddetli"],
            horizontal=True,
            key=f"psqi_{key}"
        )

    total_score = sum(int(s[0]) for s in scores.values())

    if total_score <= 5:
        severity = "Normal Uyku Kalitesi"
    elif total_score <= 10:
        severity = "Orta Derecede Uyku Problemi"
    else:
        severity = "Ciddi Uyku Bozukluğu"

    st.markdown(f"**Toplam Skor:** {total_score} / 21")
    st.markdown(f"**Değerlendirme:** {severity}")

    return total_score, severity
