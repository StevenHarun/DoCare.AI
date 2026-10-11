"""
DoCare AI - FastAPI Backend API
Menyediakan REST API untuk integrasi mobile apps, web frontend, dan layanan eksternal.
"""
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from src.core.config import settings
from src.rag.engine import rag_engine
from src.triage.emergency import triage_service
from src.services.hospital_service import hospital_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="REST API untuk layanan asisten kesehatan dan triase gawat darurat DoCare AI."
)

class TriageRequest(BaseModel):
    query: str = Field(..., example="Teman saya pingsan dan mukanya membiru")

class ChatRequest(BaseModel):
    query: str = Field(..., example="Apa saja gejala glaukoma?")
    tone: Optional[str] = Field("professional and friendly", example="professional and friendly")
    history: Optional[List[Dict[str, str]]] = Field(default=None)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.post("/api/v1/triage", tags=["Triage"])
def assess_triage(req: TriageRequest):
    """Mengevaluasi apakah keluhan pasien termasuk kategori darurat (Red Flag)."""
    result = triage_service.assess_urgency(req.query)
    return {
        "is_emergency": result.is_emergency,
        "level": result.level,
        "category": result.category,
        "detected_symptoms": result.detected_symptoms,
        "first_aid_steps": result.first_aid_steps,
        "emergency_contacts": result.emergency_contacts,
        "warning_message": result.warning_message
    }

@app.post("/api/v1/chat", tags=["Consultation"])
def chat_consultation(req: ChatRequest):
    """Menghasilkan respon konsultasi kesehatan berbasis RAG dan MedQuAD."""
    result = rag_engine.ask(
        query=req.query,
        history=req.history,
        tone=req.tone
    )
    return result

@app.get("/api/v1/hospitals", tags=["Healthcare Facilities"])
def get_nearby_hospitals(
    latitude: float = Query(..., example=-6.9740),
    longitude: float = Query(..., example=107.6303),
    radius_km: float = Query(5.0, ge=0.5, le=30.0, example=5.0)
):
    """Mencari rumah sakit dan klinik terdekat dari koordinat pengguna."""
    facilities = hospital_service.find_nearby_facilities(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km
    )
    return {
        "count": len(facilities),
        "radius_km": radius_km,
        "facilities": facilities
    }
