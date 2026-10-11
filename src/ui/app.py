"""
DoCare AI - Streamlit Web Application
Antarmuka pengguna interaktif untuk konsultasi kesehatan, panduan darurat, dan pencari RS terdekat.
"""
import sys
from pathlib import Path

# Daftarkan root path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from src.core.config import settings
from src.rag.engine import rag_engine
from src.triage.emergency import triage_service
from src.services.hospital_service import hospital_service

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="DoCare AI - Digital Health Companion",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f766e;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b5563;
        margin-bottom: 20px;
    }
    .emergency-card {
        background-color: #fee2e2;
        border-left: 5px solid #dc2626;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .info-card {
        background-color: #f0fdf4;
        border-left: 5px solid #16a34a;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .hospital-card {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Session State Chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Halo! Saya **DoCare AI**, asisten pendamping kesehatan digital Anda. 🩺\n\n"
                "Anda dapat menanyakan gejala kesehatan, meminta panduan pertolongan pertama, "
                "atau mencari fasilitas kesehatan terdekat. Ada yang bisa saya bantu hari ini?"
            )
        }
    ]

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/caduceus.png", width=64)
    st.title("DoCare AI")
    st.caption("Your Reliable Health Companion")
    st.divider()

    st.subheader("⚙️ Pengaturan Konsultasi")
    tone_option = st.selectbox(
        "Gaya Respon (Tone):",
        ["professional and friendly", "empathetic and warm", "concise and direct"],
        index=0
    )

    st.divider()
    st.subheader("🚨 Kontak Darurat Indonesia")
    st.markdown(f"""
    - **Ambulans / Kemenkes**: `{settings.EMERGENCY_HOTLINE}`
    - **Panggilan Darurat Nasional**: `{settings.NATIONAL_EMERGENCY}`
    - **Polisi**: `110`
    - **Pemadam Kebakaran**: `113`
    """)

    st.divider()
    if st.button("🗑️ Reset Riwayat Chat", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Riwayat obrolan telah dibersihkan. Silakan ajukan pertanyaan kesehatan Anda!"
            }
        ]
        st.rerun()

# Header Utama
st.markdown('<p class="main-header">🩺 DoCare AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Platform Konsultasi Awal Gejala, Respon Darurat Medis & Informasi Rumah Sakit</p>', unsafe_allow_html=True)

# Tabs
tab_chat, tab_first_aid, tab_hospital, tab_about = st.tabs([
    "💬 Konsultasi & Gejala",
    "🚨 Pertolongan Pertama (First Aid)",
    "🏥 Fasilitas Medis Terdekat",
    "ℹ️ Tentang & Metodologi"
])

# ----------------- TAB 1: KONSULTASI & CHAT -----------------
with tab_chat:
    col_chat, col_sources = st.columns([2.2, 1])

    with col_chat:
        # Tampilkan Riwayat Chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input Chat Pengguna
        user_query = st.chat_input("Ceritakan keluhan atau pertanyaan kesehatan Anda...")
        if user_query:
            # Tampilkan pesan user
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            # Proses dengan RAG Engine
            with st.chat_message("assistant"):
                with st.spinner("Menganalisis gejala dan mencari rujukan medis terverifikasi..."):
                    result = rag_engine.ask(
                        query=user_query,
                        history=st.session_state.messages,
                        tone=tone_option
                    )

                response_text = result["response"]
                st.markdown(response_text)

                # Simpan sumber rujukan terakhir di session state
                st.session_state["last_sources"] = result.get("sources", [])
                st.session_state["last_triage"] = result.get("triage")
                st.session_state.messages.append({"role": "assistant", "content": response_text})

    with col_sources:
        st.subheader("📚 Rujukan & Status Medis")
        
        last_triage = st.session_state.get("last_triage")
        if last_triage and last_triage.is_emergency:
            st.markdown(f"""
            <div class="emergency-card">
                <b>Status: {last_triage.level}</b><br>
                Kategori: {last_triage.category}<br>
                Gejala Terdeteksi: {', '.join(last_triage.detected_symptoms)}
            </div>
            """, unsafe_allow_html=True)

        sources = st.session_state.get("last_sources", [])
        if sources:
            st.write(f"Ditemukan **{len(sources)}** rujukan MedQuAD:")
            for idx, src in enumerate(sources, 1):
                with st.expander(f"📖 Rujukan #{idx} (Score: {src.get('score')})"):
                    st.caption(f"**Fokus**: {src.get('focus_area')} | **Sumber**: {src.get('source')}")
                    st.write(f"**Q:** {src.get('question')}")
                    st.write(f"**A:** {src.get('answer')[:300]}...")
        else:
            st.info("Kutipan rujukan dokumen medis akan tampil di sini setelah Anda bertanya.")

        st.caption("⚠️ **Disclaimer Hukum**: DoCare AI merupakan media edukasi dan triase awal. Selalu verifikasi kondisi dengan dokter profesional.")

# ----------------- TAB 2: PANDUAN FIRST AID -----------------
with tab_first_aid:
    st.subheader("🚨 Panduan Tindakan Pertama Kondisi Gawat Darurat")
    st.write("Langkah-langkah terstandar untuk situasi kritis sebelum tenaga medis tiba.")

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🫀 1. Nyeri Dada / Dugaan Serangan Jantung", expanded=True):
            st.markdown("""
            - **Segera panggil ambulans (119 / 112).**
            - Dudukkan penderita dengan posisi setengah tegak, punggung tersangga bantal.
            - Longgarkan pakaian di leher dan dada agar pernapasan lebih leluasa.
            - Bantu konsumsi obat resep darurat jantung (misal Nitrogliserin) jika penderita memilikinya.
            - Pantau kesadaran penderita. Bila pingsan dan tidak bernapas, lakukan CPR segera.
            """)

        with st.expander("👤 2. Korban Pingsan / Hilang Kesadaran", expanded=False):
            st.markdown("""
            - Cek respon (tepuk bahu dan panggil nama dengan suara keras).
            - Periksa napas dan nadi leher.
            - Bila bernapas normal: miringkan tubuh ke samping (**Recovery Position**) agar lidah tidak menutup jalan napas.
            - Bila tidak sadar > 1 menit atau setelah benturan kepala, bawa ke IGD.
            """)

    with col2:
        with st.expander("👄 3. Wajah / Bibir Membiru & Henti Napas (Hypoxia)", expanded=True):
            st.markdown("""
            - **Panggilan darurat kritis:** Menandakan kekurangan oksigen berat.
            - Bebaskan jalan napas dari sumbatan (benda asing, muntahan).
            - Bila tidak bernapas atau megap-megap: **Lakukan CPR segera** (100-120 tekanan/menit di dada tengah).
            - Jangan tinggalkan korban sendirian tanpa pengawasan.
            """)

        with st.expander("🧠 4. Gejala Stroke Akut (Protokol FAST)", expanded=False):
            st.markdown("""
            - **F (Face)**: Minta tersenyum; apakah satu sisi wajah turun/miring?
            - **A (Arms)**: Minta angkat kedua tangan; apakah satu tangan terkulai lemah?
            - **S (Speech)**: Minta bicara kalimat sederhana; apakah pelo atau tidak jelas?
            - **T (Time)**: Bila ada 1 tanda saja, **segera ke IGD dengan CT-Scan** (Golden Period < 4,5 jam).
            """)

# ----------------- TAB 3: FASILITAS KESEHATAN TERDEKAT -----------------
with tab_hospital:
    st.subheader("🏥 Cari Rumah Sakit & Fasilitas Medis Terdekat")
    st.write("Gunakan fitur ini untuk mencari rumah sakit, klinik, atau IGD terdekat berdasarkan koordinat GPS Anda.")

    col_loc1, col_loc2, col_loc3 = st.columns([1.5, 1.5, 1])
    with col_loc1:
        # Default Bandung (Telkom University / Buah Batu area)
        user_lat = st.number_input("Latitude:", value=-6.9740, format="%.5f")
    with col_loc2:
        user_lon = st.number_input("Longitude:", value=107.6303, format="%.5f")
    with col_loc3:
        search_radius = st.slider("Radius (km):", min_value=1.0, max_value=15.0, value=5.0, step=0.5)

    if st.button("🔍 Temukan Fasilitas Kesehatan Terdekat", type="primary"):
        with st.spinner("Menghubungi layanan peta OpenStreetMap..."):
            facilities = hospital_service.find_nearby_facilities(
                latitude=user_lat,
                longitude=user_lon,
                radius_km=search_radius
            )

        st.success(f"Ditemukan {len(facilities)} fasilitas medis di sekitar koordinat Anda:")
        for fac in facilities:
            st.markdown(f"""
            <div class="hospital-card">
                <h4 style="margin: 0; color: #0369a1;">🏥 {fac.name}</h4>
                <p style="margin: 4px 0; color: #475569;"><b>Kategori:</b> {fac.facility_type} | <b>Jarak:</b> ~{fac.distance_km} km</p>
                <p style="margin: 4px 0; color: #64748b;">📍 <i>{fac.address}</i></p>
                {"<p style='margin: 4px 0;'>📞 Telepon: " + fac.phone + "</p>" if fac.phone else ""}
                <a href="{fac.maps_url}" target="_blank" style="display: inline-block; margin-top: 8px; padding: 6px 14px; background-color: #0284c7; color: white; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">🗺️ Buka Navigasi di Google Maps</a>
            </div>
            """, unsafe_allow_html=True)

# ----------------- TAB 4: TENTANG & METODOLOGI -----------------
with tab_about:
    st.subheader("ℹ️ Tentang DoCare AI")
    st.markdown("""
    **DoCare AI** adalah platform asisten kesehatan digital (*health companion*) yang dirancang untuk:
    1. **Triase Awal Gejala (*Symptom Diagnosis Assistance*)**: Memberikan pemahaman awal mengenai potensi penyakit dan gejala umum.
    2. **Panduan Pertolongan Pertama (*Emergency Response Guidance*)**: Respon cepat instruksi P3K ketika terjadi kondisi kritis.
    3. **Navigasi Fasilitas Kesehatan (*Nearby Medical Services*)**: Menemukan IGD dan RS rujukan terdekat secara instan.

    ### Arsitektur Teknologi:
    - **Dataset**: MedQuAD (*Medical Question Answering Dataset*) dari NIH, GARD, GHR dengan 16.345 pasangan tanya-jawab medis terverifikasi.
    - **Vektor & Semantik**: Embedding multilingual berbasis transformer (`paraphrase-multilingual-MiniLM-L12-v2`) disimpan di **Qdrant Vector Database**.
    - **Generator LLM**: Orkestrasi LLM (Ollama Meta Llama 3.2 / Fallback RAG Engine) dengan *guardrails* medis empatik.
    - **Geolokasi**: OpenStreetMap Overpass API untuk pencarian fasilitas publik tanpa ketergantungan API berbayar.
    """)
