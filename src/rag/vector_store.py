"""
DoCare AI - Vector Store Manager (Qdrant Client)
Mengelola inisialisasi koleksi, penyimpanan point, dan pencarian vektor kemiripan semantik.
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from src.core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manajer interaksi Qdrant Vector Database.
    Mendukung fallback otomatis ke local disk storage bila Qdrant server belum berjalan.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        collection_name: Optional[str] = None,
        local_path: Optional[str] = None
    ):
        self.url = url or settings.QDRANT_URL
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        self.local_path = local_path or settings.QDRANT_LOCAL_PATH
        self.client = self._init_client()

    def _init_client(self) -> QdrantClient:
        """
        Inisialisasi koneksi client: mencoba server HTTP terlebih dahulu,
        kemudian fallback ke direktori lokal on-disk jika server tidak aktif.
        """
        try:
            client = QdrantClient(url=self.url, timeout=3.0)
            # Cek koneksi sederhana
            client.get_collections()
            logger.info(f"Connected to Qdrant server at {self.url}")
            return client
        except Exception:
            logger.warning(
                f"Qdrant server at {self.url} is not reachable. "
                f"Falling back to local disk storage at {self.local_path}"
            )
            try:
                return QdrantClient(path=self.local_path)
            except Exception as err:
                logger.warning(f"Local storage locked or inaccessible ({err}). Using in-memory Qdrant fallback.")
                return QdrantClient(":memory:")

    def ensure_collection(self, vector_size: int = 384):
        """Membuat koleksi jika belum ada."""
        collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")

    def recreate_collection(self, vector_size: int = 384):
        """Membuat ulang koleksi baru."""
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Recreated Qdrant collection: {self.collection_name}")

    def upsert_points(self, points: List[PointStruct]):
        """Menyimpan titik vektor dan payload ke dalam koleksi."""
        return self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points
        )

    def search(
        self,
        query_vector: List[float],
        limit: int = 3,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Mencari dokumen medis yang paling mirip dengan query vektor.
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            formatted = []
            for res in results:
                payload = res.payload or {}
                formatted.append({
                    "id": res.id,
                    "score": round(res.score, 4),
                    "question": payload.get("question", ""),
                    "answer": payload.get("answer", ""),
                    "source": payload.get("source", "MedQuAD"),
                    "focus_area": payload.get("focus_area", "")
                })
            return formatted
        except Exception as e:
            logger.error(f"Error executing vector search: {e}")
            return []

vector_store = VectorStoreManager()
