"""
Unit Tests untuk Data Quality Control (QC) & Chat Prompt Formatting
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from scripts.qc_medical_data import (
    validate_chat_doctor_record,
    format_docare_training_prompt,
    run_qc_pipeline
)

def test_validate_record():
    valid_q = "Dokter, saya merasa sesak napas dan batuk berdahak sejak 3 hari lalu."
    valid_a = "Halo, gejala tersebut kemungkinan mengarah pada infeksi saluran napas bawah. Perbanyak minum air hangat dan konsultasikan ke dokter."
    assert validate_chat_doctor_record(valid_q, valid_a) is True

    # Test invalid / corrupt records
    assert validate_chat_doctor_record("", "jawaban") is False
    assert validate_chat_doctor_record("pendek", valid_a) is False
    assert validate_chat_doctor_record(valid_q, "ok") is False

def test_prompt_formatting():
    q = "Bagaimana penanganan awal sakit kepala migrain?"
    a = "Istirahat di ruangan gelap dan hindari paparan layar digital."
    prompt = format_docare_training_prompt(q, a)

    assert "<|begin_of_text|>" in prompt
    assert "<|start_header_id|>system<|end_header_id|>" in prompt
    assert "<|start_header_id|>user<|end_header_id|>" in prompt
    assert "<|start_header_id|>assistant<|end_header_id|>" in prompt
    assert "DoCare AI" in prompt
    assert q in prompt
    assert a in prompt

def test_pipeline_qc():
    samples = [
        {"input": "Gejala demam berdarah apa saja dok?", "output": "Demam tinggi mendadak, nyeri sendi, dan bintik merah."},
        {"input": "bad", "output": "short"},  # Invalid
        {"input": "Apakah aman minum parasetamol saat hamil?", "output": "Parasetamol umumnya aman untuk dosis yang tepat."}
    ]
    report = run_qc_pipeline(samples)
    assert report["total_checked"] == 3
    assert report["valid_records"] == 2
    assert report["pass_rate_pct"] == 66.67

if __name__ == "__main__":
    test_validate_record()
    test_prompt_formatting()
    test_pipeline_qc()
    print("All Data QC Tests PASSED successfully!")
