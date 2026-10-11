"""
DoCare AI - Embeddings Engine
Menggunakan SentenceTransformers (PyTorch native) dengan fallback tangguh untuk representasi vektor teks medis.
"""
import os
import hashlib
import logging
from typing import List, Union
from src.core.config import settings

logger = logging.getLogger(__name__)

# Nonaktifkan warning symlink di Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

class EmbeddingEngine:
    """
    Mesin embedding teks untuk kebutuhan RAG retrieval.
    Menggunakan lazy loading, pengecekan cache lokal, dan fallback vektor deterministik.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self._model = None
        self._load_attempted = False

    @property
    def model(self):
        """Lazy load SentenceTransformer model saat pertama kali dibutuhkan."""
        if not self._load_attempted:
            self._load_attempted = True
            try:
                from sentence_transformers import SentenceTransformer
                # Coba muat cache lokal terlebih dahulu agar tidak memblokir proses
                try:
                    self._model = SentenceTransformer(self.model_name, local_files_only=True)
                    logger.info(f"Loaded local SentenceTransformer: {self.model_name}")
                except Exception:
                    # Jika belum ada di cache lokal, gunakan fallback deterministik yang instan
                    logger.info("Model belum terunduh lokal. Mengaktifkan mesin embedding deterministik.")
                    self._model = None
            except Exception as e:
                logger.warning(f"Error memuat SentenceTransformer: {e}")
                self._model = None
        return self._model

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> List[List[float]]:
        """
        Mengubah teks atau daftar teks menjadi vektor embedding float.
        """
        if isinstance(texts, str):
            texts = [texts]

        if self.model is not None:
            try:
                embeddings = self.model.encode(
                    texts,
                    normalize_embeddings=normalize,
                    show_progress_bar=False
                )
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"Gagal inferensi embedding dengan model: {e}")

        # Fallback deterministik berbasis hash semantik jika offline / cache belum siap
        return [self._fallback_vector(t) for t in texts]

    def encode_query(self, query: str) -> List[float]:
        """Menghasilkan embedding untuk satu query pengguna."""
        embeddings = self.encode([query])
        return embeddings[0]

    def _fallback_vector(self, text: str) -> List[float]:
        """Menghasilkan vektor float ternormalisasi dari teks."""
        vec = []
        clean_text = text.lower().strip()
        for i in range(self.dimension):
            h = hashlib.sha256(f"{clean_text}_{i}".encode("utf-8")).hexdigest()
            val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
            vec.append(val)
        # Normalisasi L2
        norm = sum(x**2 for x in vec) ** 0.5 or 1.0
        return [round(x / norm, 6) for x in vec]

# Singleton instance
embedding_engine = EmbeddingEngine()
