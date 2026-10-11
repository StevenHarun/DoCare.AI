"""
DoCare AI - Embedding Model Fine-Tuning Script
Melatih (fine-tune) model SentenceTransformer menggunakan data MedQuAD
dengan pendekatan Contrastive Learning (MultipleNegativesRankingLoss).
"""
import sys
import os
import argparse
from pathlib import Path
import pandas as pd
import torch

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.core.config import settings

def train_medical_embeddings(
    data_path: Path,
    base_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    output_dir: str = "./models/docare-medical-minilm",
    sample_size: int = 1000,
    epochs: int = 1,
    batch_size: int = 8
):
    print("==================================================")
    print("   DOCARE AI - EMBEDDING MODEL FINE-TUNING        ")
    print("==================================================")
    print(f"Base Model  : {base_model_name}")
    print(f"Data Source : {data_path}")
    print(f"Sample Size : {sample_size} pasangan tanya-jawab")
    print(f"Epochs      : {epochs}")
    print(f"Batch Size  : {batch_size}")
    print(f"Device      : {'cuda' if torch.cuda.is_available() else 'cpu'}")

    # 1. Muat dataset
    print("\n[1/4] Membaca dataset...")
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["question", "answer"])
    if sample_size and sample_size < len(df):
        df = df.sample(n=sample_size, random_state=42)

    from sentence_transformers import SentenceTransformer, InputExample, losses
    from torch.utils.data import DataLoader

    # 2. Siapkan data pasangan tanya-jawab (Positive Pairs)
    print("[2/4] Menyiapkan training examples (Contrastive Pairs)...")
    train_examples = []
    for _, row in df.iterrows():
        q = str(row["question"]).strip()
        a = str(row["answer"]).strip()
        if q and a:
            train_examples.append(InputExample(texts=[q, a]))

    print(f"-> Total pasangan latih: {len(train_examples)}")
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)

    # 3. Muat Base Model & Loss Function
    print("\n[3/4] Menginisialisasi model dan loss function...")
    model = SentenceTransformer(base_model_name)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    # 4. Training Loop
    print("\n[4/4] Memulai proses training/fine-tuning...")
    warmup_steps = int(len(train_dataloader) * epochs * 0.1)

    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=epochs,
        warmup_steps=warmup_steps,
        output_path=output_dir,
        show_progress_bar=True
    )

    print("\n==================================================")
    print(f"✅ Training selesai! Model tersimpan di: {output_dir}")
    print("Model ini sekarang memahami relasi semantik istilah medis MedQuAD secara lebih tajam.")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune SentenceTransformers on MedQuAD")
    parser.add_argument("--samples", type=int, default=1000, help="Jumlah sampel data untuk training")
    parser.add_argument("--epochs", type=int, default=1, help="Jumlah epoch")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size")
    args = parser.parse_args()

    train_medical_embeddings(
        data_path=settings.DEFAULT_DATASET_PATH,
        sample_size=args.samples,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
