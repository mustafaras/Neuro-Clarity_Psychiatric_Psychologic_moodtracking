import streamlit as st

def pss10_form():
    st.markdown("📝 **PSS-10 – Algılanan Stres Ölçeği**")
    st.markdown("_Son 1 ay içinde aşağıdaki durumları ne sıklıkla yaşadınız?_")

    questions = [
        ("Günlük yaşamınızdaki önemli şeyleri kontrol edemediğinizi hissettiniz mi?", False),
        ("Önemli konuların üstesinden gelebildiğinizi hissettiniz mi?", True),  # ters puan
        ("Sinirlerinizin gerildiğini ya da stresli hissettiğiniz zamanlar oldu mu?", False),
        ("Kendinize güveninizin yerinde olduğunu hissettiniz mi?", True),  # ters puan
        ("Her şeyin üst üste geldiğini düşündüğünüz zamanlar oldu mu?", False),
        ("Günlük sorumluluklarınızı kontrol edebildiğinizi hissettiniz mi?", True),  # ters puan
        ("Sizi kızdıran şeylerle başa çıkabildiğinizi hissettiniz mi?", True),  # ters puan
        ("Sizi üzen olayların üstesinden gelebildiğinizi hissettiniz mi?", True),  # ters puan
        ("Zorluklar üst üste geldiğinde üstesinden gelebileceğinizi hissettiniz mi?", True),  # ters puan
        ("Durumun kontrolünüz dışında geliştiğini hissettiniz mi?", False)
    ]

    options = {
        "Hiç": 0,
        "Nadiren": 1,
        "Bazen": 2,
        "Sık sık": 3,
        "Her zaman": 4
    }

    total_score = 0
    for idx, (q, is_reversed) in enumerate(questions):
        answer = st.radio(f"{idx + 1}. {q}", list(options.keys()), key=f"pss_{idx}")
        score = options[answer]
        if is_reversed:
            score = 4 - score
        total_score += score

    # Değerlendirme (ortalama birey skoru genellikle 13 civarıdır)
    if total_score <= 13:
        level = "Düşük Stres"
    elif total_score <= 20:
        level = "Orta Düzey Stres"
    else:
        level = "Yüksek Stres"

    st.markdown(f"**Toplam Skor:** {total_score} / 40")
    st.markdown(f"**Stres Düzeyi:** {level}")

    return total_score, level
