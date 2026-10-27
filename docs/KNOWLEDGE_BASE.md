# 📘 KNOWLEDGE BASE: DoCare AI (Bangkit Capstone Project)

Dokumen ini merupakan hasil sintesis pengetahuan, arsitektur teknis, catatan percakapan, dan inventaris berkas yang diekstraksi dari server Discord **Capstooooooooooooone Bangkit**.

---

## 1. 📌 Ringkasan Proyek (Executive Summary)
* **Nama Proyek:** **DoCare AI**
* **Program:** Bangkit Academy Capstone Project
* **Tujuan Proyek:** Mengembangkan asisten medis berbasis kecerdasan buatan (*AI Medical Assistant*) dengan kapabilitas tanya jawab seputar kesehatan menggunakan pendekatan **Retrieval-Augmented Generation (RAG)** untuk meminimalisir halusinasi dan meningkatkan akurasi jawaban berbasis literatur medis.
* **Mentor:**
  * Bu Vina ([Dicoding Mentor #1491316](https://www.dicoding.com/mentoring/mentors/1491316))
  * Pak Aidil ([Dicoding Mentor #3670753](https://www.dicoding.com/mentoring/mentors/3670753))

---

## 2. 👥 Pembagian Tim & Kontributor

| Nama Akun Discord / Identitas | Path / Peran | Kontribusi Utama yang Terekam |
| :--- | :--- | :--- |
| **Josta (@joanoestalin)** / **Steven Harun** | Machine Learning (Lead/Core Research) | **Riset Fondasi Healthcare LLM & Fine-Tuning**: Memberikan literatur kunci pemilihan open-source LLM, panduan fine-tuning data medis (*healthcare data*), transfer learning Keras/TensorFlow, serta pengembangan pipeline fine-tuning QLoRA & DDP Kaggle dual-T4 |
| **alpaai** | Machine Learning & MD | Inisiasi arsitektur LangChain, integrasi Flask API, riset literatur medis, koordinasi antar-path |
| **mshidayat66** | Machine Learning | Pengembangan embedding TensorFlow/PyTorch, evaluasi output LLM, eksperimen Qdrant Vector DB |
| **Naufal Eka** | Cloud Computing / Team Lead | Perancangan Dockerfile (CUDA 12.5), manajemen Project Plan & Google Sheets, setup GitHub repository |
| **Rahma** | Cloud Computing | Deployment Qdrant ke Google Cloud Platform (GCP), pembuatan diagram `ML_Architecture.png` & `kerja_per_path_learning.png` |
| **yava** | Cloud Computing | Troubleshooting submodule & symlinks Git |

---

## 3. 🏗️ Arsitektur Sistem & Tech Stack

### A. Machine Learning (ML) & RAG Pipeline
* **Framework:** LangChain
* **LLM Engine:** Ollama / HuggingFace Transformers
* **Embedding Model:** Eksperimen awal menggunakan PyTorch pre-trained model dan Sentence Transformers, kemudian dikonversi/diuji menggunakan model embedding berbasis TensorFlow.
* **Vector Database:** **Qdrant** (Vector Search Engine).
  * Digunakan untuk menyimpan embeddings dari dokumen pengetahuan medis.
  * Disinkronkan melalui Google Colab dan server cloud.
* **API Serving:**
  * `Flask.py` untuk prototipe lokal awal.
  * **FastAPI** (`uvicorn app.main:app --host 0.0.0.0 --port 8002`) untuk inferensi skala produksi.

### B. Cloud Computing (CC) & Infrastruktur
* **Platform:** Google Cloud Platform (GCP) Compute Engine.
* **Containerization:** Docker dengan akselerasi GPU NVIDIA.
  * Base Image: `nvidia/cuda:12.5.0-base-ubuntu22.04`
  * Dependensi OS: `python3-pip`, `libglib2.0-0`, `iputils-ping`, `cron`, `curl`
* **Qdrant Server:**
  * Host: `http://34.101.137.149:6333/dashboard`
* **Port Layanan:**
  * Port `6333`: Qdrant REST API / Dashboard
  * Port `8002`: FastAPI ML Serving Engine

### C. Mobile Development (MD)
* **Platform:** Android Application (Kotlin/Java)
* Menghubungkan antarmuka obrolan pengguna mobile ke endpoint REST API cloud untuk mendapatkan respons medis secara interaktif.

---

## 4. 📚 Referensi Akademis & Dokumen Kunci
Berdasarkan catatan diskusi tim di `#ml-get-post-ipynb`:
1. *Rendahnya kesadaran kesehatan:* [Cureus Journal (PMC10309079)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10309079/pdf/cureus-0015-00000039706.pdf)
2. *Dampak positif AI dalam dunia medis:* [NCBI Books (NBK602381)](https://www.ncbi.nlm.nih.gov/books/NBK602381/)
3. *Tantangan adopsi Chatbot oleh praktisi medis:* [PMC6473203](https://pmc.ncbi.nlm.nih.gov/articles/PMC6473203/)
4. *Referensi implementasi kode:* Tutorial RAG & LLM YouTube (`F0GQ0l2NfHA`).

---

## 5. 📂 Struktur Arsip Berkas yang Tersimpan

Seluruh berkas telah diunduh dan diarsipkan di direktori:
`C:\Users\steve\OneDrive\Documents\1_1_Self Project\DoCareAi_Discord_Archive\`

```text
DoCareAi_Discord_Archive/
├── KNOWLEDGE_BASE.md                  # Dokumentasi sintesis proyek (file ini)
├── AUDIT_SUMMARY.md                   # Ringkasan statistik pesan dan berkas
├── files_manifest.json                # Metadata JSON lengkap seluruh berkas
├── transcripts/                       # Transkrip percakapan markdown per channel
│   ├── discussion_transcript.md
│   ├── ml-get-post-ipynb_transcript.md
│   ├── dokumentasi_transcript.md
│   ├── ml-stuffs_transcript.md
│   ├── md-stuffs_transcript.md
│   └── cc-stuffs_transcript.md
├── raw_json/                          # Data pesan mentah format JSON
│   ├── discussion_messages.json
│   ├── ml-get-post-ipynb_messages.json
│   └── ...
└── attachments/                       # 39 Berkas lampiran asli per channel
    ├── discussion/                    # Foto & screenshot pembahasan
    ├── ml-get-post-ipynb/             # File kode arsip ZIP:
    │   ├── DoCare_AI.zip (9.72 MB)
    │   ├── Capstone_Project_2.zip (9.69 MB)
    │   ├── Capstone_Project.zip (9.72 MB)
    │   ├── Capstone_Bangkit.zip (4.98 MB)
    │   ├── LLM.zip (12.74 KB)
    │   └── requirements.txt (146 B)
    ├── dokumentasi/                   # Foto mentoring resmi Bangkit
    ├── ml-stuffs/                     # RAG.png & diagram model
    ├── md-stuffs/                     # Screenshot mobile app
    └── cc-stuffs/                     # ML_Architecture.png & kerja_per_path_learning.png
```

---

## 6. 💡 Riwayat Solusi & Troubleshooting Tim yang Terekam
1. **Konflik Dependensi Library Python:**
   * Ditemukan oleh `mshidayat66` saat menginstal pustaka LangChain & Transformers. Diselesaikan dengan membuat file `requirements.txt` khusus versi teruji.
2. **Kualitas Embedding:**
   * Model embedding buatan sendiri sempat menghasilkan repetisi output pada LLM. Solusinya beralih ke Sentence Transformers pre-trained yang dikonversi ke format TensorFlow untuk kompatibilitas.
3. **Konektivitas Ollama / Timeout:**
   * Sempat mengalami kendala *connection refused* pada saat *invoke chain*. Dialihkan menggunakan API Qdrant Cloud dan containerized FastAPI di VM GCP.
4. **Git Symlinks & Submodules:**
   * Saat melakukan push ke repository utama, folder subproject sempat tidak dapat dibuka di GitHub. Diselesaikan dengan membersihkan pointer submodule `.git` yang bertumpuk.
