"""
DoCare AI - Data Ingestion Pipeline (MedQuAD to Qdrant)
Memuat dataset MedQuAD, menghitung embedding vektor, dan menyimpan ke koleksi Qdrant.
"""
import sys
import time
import argparse
from pathlib import Path
import pandas as pd
from qdrant_client.http.models import PointStruct

# Tambahkan root folder ke sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.core.config import settings
from src.rag.embeddings import embedding_engine
from src.rag.vector_store import vector_store

def run_ingestion(dataset_path: Path, limit: int = None, batch_size: int = 64):
    print("==================================================")
    print("      DOCARE AI - DATA INGESTION PIPELINE         ")
    print("==================================================")
    print(f"Dataset Path : {dataset_path}")
    print(f"Target Qdrant: {vector_store.collection_name}")
    print(f"Batch Size   : {batch_size}")

    if not dataset_path.exists():
        print(f"ERROR: File dataset tidak ditemukan di: {dataset_path}")
        sys.exit(1)

    print("\n[1/4] Membaca dataset...")
    df = pd.read_csv(dataset_path)
    if limit:
        df = df.head(limit)
    total_records = len(df)
    print(f"-> Total baris yang akan diproses: {total_records}")

    print("\n[2/4] Menyiapkan koleksi Qdrant...")
    vector_store.recreate_collection(vector_size=settings.EMBEDDING_DIMENSION)

    print("\n[3/4] Menghitung embeddings dan mengunggah ke Qdrant...")
    start_time = time.time()
    uploaded_count = 0

    for i in range(0, total_records, batch_size):
        batch_df = df.iloc[i:i + batch_size]
        batch_texts = (
            batch_df["question"].fillna("") + " " + batch_df["answer"].fillna("")
        ).tolist()

        # Hitung embeddings
        batch_embeddings = embedding_engine.encode(batch_texts)

        # Buat PointStruct
        points = []
        for idx, (_, row) in enumerate(batch_df.iterrows()):
            point_id = i + idx
            points.append(
                PointStruct(
                    id=point_id,
                    vector=batch_embeddings[idx],
                    payload={
                        "question": str(row["question"]),
                        "answer": str(row["answer"]),
                        "source": str(row.get("source", "MedQuAD")),
                        "focus_area": str(row.get("focus_area", ""))
                    }
                )
            )

        vector_store.upsert_points(points)
        uploaded_count += len(points)
        percent = (uploaded_count / total_records) * 100
        print(f"  -> Terunggah: {uploaded_count}/{total_records} ({percent:.1f}%)")

    total_time = time.time() - start_time
    print(f"\n[4/4] Ingesti selesai! Total waktu: {total_time:.2f} detik.")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest MedQuAD dataset into Qdrant")
    parser.add_argument("--limit", type=int, default=None, help="Batasi jumlah data (opsional untuk pengujian cepat)")
    parser.add_argument("--batch-size", type=int, default=64, help="Ukuran batch pemrosesan")
    args = parser.parse_args()

    run_ingestion(
        dataset_path=settings.DEFAULT_DATASET_PATH,
        limit=args.limit,
        batch_size=args.batch_size
    )
