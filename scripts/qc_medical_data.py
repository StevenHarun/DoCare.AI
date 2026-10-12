"""
DoCare AI - Medical Dataset Quality Control (QC) & Validation Suite
Menguji kebersihan, kelengkapan, dan format dataset percakapan dokter-pasien terverifikasi.
"""
import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

def validate_chat_doctor_record(input_text: str, output_text: str) -> bool:
    """Memeriksa apakah dialog dokter-pasien memenuhi standar kualitas data klinis."""
    if not input_text or not output_text:
        return False
    if len(input_text.strip()) < 15:  # Terlalu pendek untuk keluhan medis
        return False
    if len(output_text.strip()) < 20:  # Terlalu pendek untuk saran dokter
        return False
    return True

def format_docare_training_prompt(patient_query: str, doctor_response: str) -> str:
    """Mengubah pasangan dialog dokter-pasien ke Llama-3 Chat Template standar DoCare AI."""
    clean_q = patient_query.strip()
    clean_a = doctor_response.strip()
    return (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
        f"Anda adalah DoCare AI, asisten pendamping kesehatan terpercaya berbasis rujukan dokter bersertifikasi. "
        f"Jawab pertanyaan pasien dengan sopan, empatik, jelas, dan akurat secara medis.<|eot_id|>\n"
        f"<|start_header_id|>user<|end_header_id|>\n"
        f"{clean_q}<|eot_id|>\n"
        f"<|start_header_id|>assistant<|end_header_id|>\n"
        f"Terima kasih telah berkonsultasi dengan DoCare AI. {clean_a} "
        f"Semoga informasi ini bermanfaat dan lekas sembuh.<|eot_id|>"
    )

def run_qc_pipeline(sample_records):
    """Menjalankan evaluasi QC pada sekumpulan rekaman dialog medis."""
    valid_count = 0
    total = len(sample_records)
    total_tokens_est = 0

    for item in sample_records:
        inp = item.get("input", "")
        out = item.get("output", "")
        if validate_chat_doctor_record(inp, out):
            valid_count += 1
            prompt = format_docare_training_prompt(inp, out)
            total_tokens_est += len(prompt.split())

    pass_rate = (valid_count / total) * 100 if total > 0 else 0
    avg_tokens = (total_tokens_est / valid_count) if valid_count > 0 else 0

    return {
        "total_checked": total,
        "valid_records": valid_count,
        "pass_rate_pct": round(pass_rate, 2),
        "avg_words_per_sample": round(avg_tokens, 1)
    }

if __name__ == "__main__":
    print("QC Helper Suite DoCare AI siap digunakan.")
