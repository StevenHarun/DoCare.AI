"""
DoCare AI - Core RAG Engine
Mengintegrasikan deteksi triage darurat, pencarian semantik MedQuAD Qdrant, dan orkestrasi respon LLM.
"""
import logging
from typing import List, Dict, Any, Optional
from src.core.config import settings
from src.triage.emergency import triage_service, TriageResult
from src.rag.embeddings import embedding_engine
from src.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

class DoCareRAGEngine:
    """
    Mesin utama DoCare AI untuk konsultasi kesehatan dan pertolongan pertama.
    """

    def __init__(self):
        self.triage = triage_service
        self.embeddings = embedding_engine
        self.store = vector_store

    def build_system_prompt(self, context_text: str, tone: str = "professional and friendly") -> str:
        """Menyusun instruksi sistem medis yang aman dan empatik."""
        return f"""You are DoCare AI, an empathetic and certified digital healthcare companion.
Tone: {tone}.

Rules for responding:
1. Start your response with: "Terima kasih telah berkonsultasi dengan DoCare AI." (or "Thank you for consulting with DoCare AI" if query is in English).
2. Answer clearly and informatively in the same language as the user's query (Bahasa Indonesia / English).
3. Base your health information strictly on the provided medical references below. If the provided reference does not directly answer the specific condition, clearly state "Ini adalah informasi rujukan terbaik yang kami temukan" and do NOT make up or fabricate medical diagnoses.
4. Always advise consulting a licensed physician for definitive medical diagnoses and treatment plans.
5. End your response with: "Semoga informasi ini bermanfaat, lekas sembuh, dan terima kasih." (or "Hope this information helps, wish you a speedy recovery, and thank you" in English).

Verified Medical References (MedQuAD Dataset):
{context_text}
"""

    def ask(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
        tone: str = "professional and friendly"
    ) -> Dict[str, Any]:
        """
        Memproses query pengguna dari tahap triage hingga respon AI.
        """
        # 1. Evaluasi Triage Kedaruratan Medis
        triage_res: TriageResult = self.triage.assess_urgency(query)

        if triage_res.is_emergency:
            # Bila terdeteksi kondisi darurat/kritis, dahulukan protokol First Aid
            first_aid_formatted = "\n".join([f"- {step}" for step in triage_res.first_aid_steps])
            emergency_reply = (
                f"🚨 **{triage_res.warning_message}**\n\n"
                f"**Kategori Darurat**: {triage_res.category} ({triage_res.level})\n\n"
                f"### Langkah Pertolongan Pertama Segera (First Aid):\n{first_aid_formatted}\n\n"
                f"📞 **Kontak Darurat Segera**:\n"
                f"- Ambulans / Kemenkes: **{settings.EMERGENCY_HOTLINE}**\n"
                f"- Panggilan Darurat Nasional: **{settings.NATIONAL_EMERGENCY}**\n\n"
                f"💡 *Gunakan tab 'Fasilitas Kesehatan' di samping untuk menemukan IGD / Rumah Sakit terdekat dari lokasi Anda.*"
            )
            return {
                "response": emergency_reply,
                "is_emergency": True,
                "triage": triage_res,
                "sources": [],
                "model_used": "DoCare-Triage-Emergency-Guard"
            }

        # 2. Pengambilan Vektor & Pencarian Semantik MedQuAD
        try:
            query_vector = self.embeddings.encode_query(query)
            retrieved_docs = self.store.search(
                query_vector=query_vector,
                limit=settings.RETRIEVAL_TOP_K,
                score_threshold=settings.SIMILARITY_THRESHOLD
            )
        except Exception as e:
            logger.error(f"Gagal melakukan embedding/search: {e}")
            retrieved_docs = []

        # 3. Format Konteks Medis
        if retrieved_docs:
            context_blocks = []
            for doc in retrieved_docs:
                context_blocks.append(
                    f"[Topik: {doc.get('focus_area') or 'Medis'} | Sumber: {doc.get('source')}]\n"
                    f"Pertanyaan: {doc.get('question')}\n"
                    f"Informasi Medis: {doc.get('answer')}"
                )
            context_text = "\n\n".join(context_blocks)
        else:
            context_text = "Tidak ditemukan rujukan dokumen spesifik di basis data MedQuAD."

        # 4. Generate Respon Menggunakan LLM (Ollama atau Fallback Berbasis RAG)
        system_prompt = self.build_system_prompt(context_text, tone)
        llm_response = self._call_llm(query, system_prompt, history)

        return {
            "response": llm_response,
            "is_emergency": False,
            "triage": triage_res,
            "sources": retrieved_docs,
            "model_used": settings.OLLAMA_MODEL
        }

    def _call_llm(
        self,
        query: str,
        system_prompt: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Memanggil Ollama atau fallback RAG generator."""
        # Coba panggil Ollama lokal
        try:
            import ollama
            messages = [{"role": "system", "content": system_prompt}]
            if history:
                for h in history[-4:]:  # 2 turn terakhir
                    messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": query})

            client = ollama.Client(host=settings.OLLAMA_HOST, timeout=2.0)
            res = client.chat(
                model=settings.OLLAMA_MODEL,
                messages=messages,
                options={"seed": 237, "temperature": 0.3}
            )
            return res["message"]["content"]
        except Exception as e:
            logger.info(f"Ollama offline/tidak tersedia ({e}), menggunakan RAG synthesizer bawaan.")

        # Fallback RAG Synthesis jika Ollama tidak sedang aktif di komputer pengguna
        # Tetap mengikuti aturan DoCare AI prompt
        return self._synthesize_rag_fallback(query, system_prompt)

    def _synthesize_rag_fallback(self, query: str, system_prompt: str) -> str:
        """Fallback aman jika server Ollama belum di-start oleh pengguna."""
        is_id = any(w in query.lower() for w in ["saya", "apa", "gejala", "apakah", "sakit", "obat", "bagaimana"])
        
        greeting = (
            "Terima kasih telah berkonsultasi dengan DoCare AI.\n\n"
            if is_id else
            "Thank you for consulting with DoCare AI.\n\n"
        )
        
        body = (
            "Berdasarkan basis pengetahuan medis rujukan terverifikasi yang kami temukan:\n\n"
            if is_id else
            "Based on the verified medical reference knowledge base:\n\n"
        )
        
        # Ekstrak bagian referensi dari system prompt jika ada
        if "Verified Medical References (MedQuAD Dataset):" in system_prompt:
            ref_part = system_prompt.split("Verified Medical References (MedQuAD Dataset):")[-1].strip()
            if "Tidak ditemukan rujukan" not in ref_part:
                body += f"{ref_part}\n\n"
            else:
                body += (
                    "Informasi rujukan yang spesifik tidak ditemukan secara tepat di basis data kami. "
                    "Harap segera berkonsultasi langsung dengan dokter untuk evaluasi lebih lanjut.\n\n"
                    if is_id else
                    "Specific references for this inquiry were not found in our database. "
                    "Please consult directly with a doctor for further evaluation.\n\n"
                )
        else:
            body += "Silakan konsultasikan gejala Anda dengan dokter untuk diagnosis akurat.\n\n"

        closing = (
            "⚠️ *Peringatan*: Informasi ini bersifat edukatif awal dan bukan pengganti diagnosis medis resmi dokter.\n\n"
            "Semoga informasi ini bermanfaat, lekas sembuh, dan terima kasih."
            if is_id else
            "⚠️ *Notice*: This information is educational and does not replace official medical diagnoses.\n\n"
            "Hope this information helps, wish you a speedy recovery, and thank you."
        )

        return greeting + body + closing

rag_engine = DoCareRAGEngine()
