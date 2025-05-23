import streamlit as st

def iesr_form():
    st.markdown("🛌 **IES-R – Travma Sonrası Stres Bozukluğu Ölçeği**")
    st.markdown("_Aşağıdaki sorular son 1 ay içindeki deneyimlerinize dayalıdır._")

    questions = [
        "Rahatsız edici anılar veya düşünceler aklınıza geliyor mu?",
        "Rahatsız edici rüyalar görüyor musunuz?",
        "Travmatik olayları hatırlatan şeylerden kaçınıyor musunuz?",
        "Kendinizi gergin veya huzursuz hissediyor musunuz?",
        "Kolayca sinirleniyor veya öfkeleniyor musunuz?",
        "Konsantrasyon güçlüğü yaşıyor musunuz?",
        "Uykusuzluk çekiyor musunuz?",
        "Kendinizi duygusal olarak hissiz hissediyor musunuz?",
        "Travmatik olayları hatırlatan şeylerden rahatsız oluyor musunuz?",
        "Gelecekle ilgili umutsuz hissediyor musunuz?"
    ]

    freq_map = {
        "Hiç": 0,
        "Nadiren": 1,
        "Bazen": 2,
        "Sıkça": 3,
        "Çok Sık": 4
    }

    total_score = 0
    for i, question in enumerate(questions):
        answer = st.selectbox(f"❓ {question}", list(freq_map.keys()), key=f"iesr_{i}")
        total_score += freq_map[answer]

    if total_score <= 24:
        severity = "Düşük Travma Belirtileri"
    elif total_score <= 48:
        severity = "Orta Derecede Travma Belirtileri"
    else:
        severity = "Yüksek Travma Belirtileri"

    st.markdown(f"**Toplam Skor:** {total_score} / 40")
    st.markdown(f"**Travma Seviyesi:** {severity}")

    return total_score, severity
