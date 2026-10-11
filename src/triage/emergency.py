"""
DoCare AI - Emergency Triage & Medical Guardrails Engine
Mendeteksi gejala darurat medis (Red Flags) dan memberikan instruksi pertolongan pertama (First Aid) instan.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from src.core.config import settings

@dataclass
class TriageResult:
    is_emergency: bool
    level: str  # "CRITICAL", "URGENT", "NON_EMERGENCY"
    category: str
    detected_symptoms: List[str] = field(default_factory=list)
    first_aid_steps: List[str] = field(default_factory=list)
    emergency_contacts: Dict[str, str] = field(default_factory=dict)
    warning_message: str = ""

class EmergencyTriage:
    """
    Sistem Triage Medis Darurat Berbasis Aturan & Deteksi Gejala Kritis.
    Mendukung bahasa Indonesia dan Inggris.
    """

    CRITICAL_RULES = {
        "CYANOSIS_AND_FAINT": {
            "keywords": [
                "face is blue", "muka biru", "bibir biru", "wajah membiru", 
                "cyanosis", "sianosis", "blue lips", "blue skin"
            ],
            "secondary_triggers": ["faint", "pingsan", "unconscious", "tidak sadar", "sesak"],
            "level": "CRITICAL",
            "category": "Hypoxia / Respiratory Arrest",
            "first_aid": [
                "SEGERA hubungi Ambulans (119 / 112) sekarang juga!",
                "Periksa apakah korban masih bernapas dan apakah terdapat denyut nadi.",
                "Bila korban TIDAK BERNAPAS, segera lakukan Resusitasi Jantung Paru (RJP / CPR): tekan dada di tengah sedalam 5-6 cm dengan kecepatan 100-120x per menit.",
                "Bila masih bernapas namun tidak sadar, baringkan dalam posisi pemulihan (miring ke samping) agar jalan napas tidak tersumbat lidah atau muntahan.",
                "Longgarkan pakaian ketat di leher dan dada.",
                "JANGAN berikan makan atau minum pada orang yang tidak sadar."
            ],
            "warning": "PERINGATAN KRITIS: Kondisi wajah/bibir membiru menandakan kekurangan oksigen berat (hipoksia) atau henti napas/jantung yang mengancam nyawa!"
        },
        "CARDIAC_ARREST_OR_CHEST_PAIN": {
            "keywords": [
                "chest pain", "nyeri dada", "sakit dada", "serangan jantung", 
                "heart attack", "dada tertekan", "dada nyeri", "chest hurts"
            ],
            "level": "CRITICAL",
            "category": "Cardiovascular Emergency",
            "first_aid": [
                "SEGERA hubungi nomor darurat 119 atau 112!",
                "Minta penderita untuk berhenti beraktivitas dan duduk dalam posisi setengah duduk dengan punggung disangga bantal.",
                "Longgarkan pakaian ketat di sekitar leher dan pinggang.",
                "Jika penderita memiliki obat serangan jantung dari dokter (seperti Nitrogliserin), bantu mereka meminumnya.",
                "Bila penderita tiba-tiba pingsan dan tidak bernapas, segera lakukan kompresi dada (CPR).",
                "Tetap dampingi penderita dengan tenang hingga bantuan medis tiba."
            ],
            "warning": "PERINGATAN DARURAT: Nyeri dada hebat adalah tanda bahaya serangan jantung akut. Butuh penanganan medis secepatnya."
        },
        "UNCONSCIOUSNESS": {
            "keywords": [
                "faint", "pingsan", "unconscious", "tidak sadarkan diri", 
                "kejang", "seizure", "collapse", "hilang kesadaran"
            ],
            "level": "URGENT",
            "category": "Neurological / Loss of Consciousness",
            "first_aid": [
                "Periksa respon dengan menepuk bahu dan memanggil nama dengan lantang.",
                "Periksa hembusan napas dan gerakan dada.",
                "Jika bernapas normal, posisikan tubuh miring (Recovery Position) untuk mengamankan jalan napas.",
                "Tinggikan posisi kaki sekitar 30 cm jika pingsan karena tekanan darah rendah (sinkop sederhana).",
                "Jika mengalami kejang: jauhkan benda keras/tajam di sekitar korban, JANGAN masukkan benda apa pun ke dalam mulut korban, dan miringkan kepala ke samping.",
                "Hubungi 119 bila tidak kunjung sadar lebih dari 1 menit."
            ],
            "warning": "PERINGATAN: Hilang kesadaran atau kejang memerlukan pemantauan ketat jalan napas."
        },
        "STROKE_SIGNS": {
            "keywords": [
                "stroke", "bicara pelo", "slurred speech", "mati rasa separuh", 
                "wajah miring", "face drooping", "lumpuh sebelah", "mulut mencong"
            ],
            "level": "CRITICAL",
            "category": "Stroke (FAST Protocol)",
            "first_aid": [
                "Lakukan tes FAST (Face drooping, Arm weakness, Slurred speech, Time to call).",
                "SEGERA bawa ke IGD rumah sakit terdekat dengan fasilitas CT-Scan (Golden Period: < 4,5 jam).",
                "Catat waktu persis ketika gejala pertama kali muncul.",
                "Baringkan pasien dengan kepala sedikit ditinggikan (sekitar 30 derajat).",
                "JANGAN beri makan, minum, atau obat penurun tensi sebelum evaluasi dokter."
            ],
            "warning": "PERINGATAN: Gejala FAST mengindikasikan serangan Stroke akut. Setiap menit sangat berharga (Time is Brain)!"
        },
        "SEVERE_BLEEDING": {
            "keywords": [
                "severe bleeding", "pendarahan hebat", "darah mengucur", 
                "arteri putus", "pendarahan parah", "heavy bleeding"
            ],
            "level": "CRITICAL",
            "category": "Severe Hemorrhage / Trauma",
            "first_aid": [
                "Tekan luka secara langsung menggunakan kain bersih atau kassa steril.",
                "Pertahankan tekanan konstan selama minimal 10-15 menit tanpa membuka perban.",
                "Tinggikan bagian yang terluka di atas posisi jantung jika memungkinkan.",
                "Jika darah merembes, tambahkan kain di atasnya tanpa melepas kain pertama.",
                "Segera hubungi 119 atau bawa ke Unit Gawat Darurat."
            ],
            "warning": "PERINGATAN: Pendarahan masif dapat memicu syok hipovolemik fatal dalam waktu singkat."
        }
    }

    def assess_urgency(self, query: str) -> TriageResult:
        """
        Menganalisis keluhan pengguna dan mengembalikan status kedaruratan.
        """
        query_lower = query.lower()
        matched_symptoms = []
        highest_rule = None

        # Evaluasi aturan prioritas
        for rule_key, rule_data in self.CRITICAL_RULES.items():
            primary_match = any(kw in query_lower for kw in rule_data["keywords"])
            
            # Cek secondary trigger bila ada
            secondary_triggers = rule_data.get("secondary_triggers", [])
            secondary_match = any(st in query_lower for st in secondary_triggers) if secondary_triggers else True

            if primary_match:
                for kw in rule_data["keywords"]:
                    if kw in query_lower:
                        matched_symptoms.append(kw)

                if secondary_triggers and secondary_match:
                    highest_rule = rule_data
                    break
                elif not secondary_triggers and highest_rule is None:
                    highest_rule = rule_data

        if highest_rule:
            return TriageResult(
                is_emergency=True,
                level=highest_rule["level"],
                category=highest_rule["category"],
                detected_symptoms=list(set(matched_symptoms)),
                first_aid_steps=highest_rule["first_aid"],
                emergency_contacts={
                    "Ambulans / Kesehatan (Kemenkes)": settings.EMERGENCY_HOTLINE,
                    "Panggilan Darurat Terpadu": settings.NATIONAL_EMERGENCY
                },
                warning_message=highest_rule["warning"]
            )

        return TriageResult(
            is_emergency=False,
            level="NON_EMERGENCY",
            category="General Consultation",
            detected_symptoms=[],
            first_aid_steps=[],
            emergency_contacts={},
            warning_message=""
        )

# Instance default singleton
triage_service = EmergencyTriage()
