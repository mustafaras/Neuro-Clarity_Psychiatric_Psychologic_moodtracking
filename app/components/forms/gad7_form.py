import streamlit as st

def gad7_form():
    st.markdown("📝 **GAD-7 – Yaygın Anksiyete Bozukluğu Ölçeği**")
    st.markdown("_Geçtiğimiz 2 hafta içinde aşağıdaki durumları ne sıklıkta yaşadınız?_")

    questions = [
        "Sinirli, endişeli ya da gergin hissetme",
        "Kontrol edemeyeceğiniz kadar endişelenme",
        "Çok fazla şey hakkında endişelenme",
        "Rahatlayamama",
        "Huzursuzluk nedeniyle yerinde duramama",
        "Kolayca sinirlenme ya da rahatsız olma",
        "Felaket olabileceği duygusu"
    ]

    options = {
        "Hiç": 0,
        "Birkaç gün": 1,
        "Haftanın yarısından fazla": 2,
        "Neredeyse her gün": 3
    }

    total_score = 0
    for q in questions:
        answer = st.radio(q, list(options.keys()), key=q)
        total_score += options[answer]

    # Şiddet düzeyi
    if total_score <= 4:
        severity = "Minimal Anksiyete"
    elif total_score <= 9:
        severity = "Hafif Anksiyete"
    elif total_score <= 14:
        severity = "Orta Düzey Anksiyete"
    else:
        severity = "Şiddetli Anksiyete"

    st.markdown(f"**Toplam Skor:** {total_score} / 21")
    st.markdown(f"**Anksiyete Şiddeti:** {severity}")

    return total_score, severity
