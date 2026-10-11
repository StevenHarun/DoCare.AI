"""
DoCare AI - Application Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:
    PROJECT_NAME: str = "DoCare AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Your Reliable Digital Health Companion"

    # Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DEFAULT_DATASET_PATH: Path = DATA_DIR / "cleaned_medquad.csv"
    STORAGE_DIR: Path = BASE_DIR / "qdrant_storage"

    # Qdrant Vector DB
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION_NAME", "Healthcare_MedQuAD")
    QDRANT_LOCAL_PATH: str = os.getenv("QDRANT_STORAGE_PATH", str(STORAGE_DIR))

    # Embeddings
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_DIMENSION: int = 384  # MiniLM dimension (768 for MPNet)
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))

    # LLM Settings (Ollama)
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Emergency Triage
    EMERGENCY_HOTLINE: str = os.getenv("EMERGENCY_HOTLINE", "119")
    NATIONAL_EMERGENCY: str = os.getenv("NATIONAL_EMERGENCY", "112")

    # Nearby Healthcare
    HOSPITAL_SEARCH_RADIUS_KM: float = float(os.getenv("HOSPITAL_SEARCH_RADIUS_KM", "5.0"))
    OVERPASS_API_URL: str = os.getenv(
        "OVERPASS_API_URL", 
        "https://overpass-api.de/api/interpreter"
    )

settings = Settings()
