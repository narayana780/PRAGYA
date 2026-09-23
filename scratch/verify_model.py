import sys
import os

print("Testing SentenceTransformer model loading...")
try:
    from sentence_transformers import SentenceTransformer
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"Loading {model_name}...")
    model = SentenceTransformer(model_name)
    test_text = "PRAGYA AI-Powered Competency & Personalized Learning Platform"
    emb = model.encode(test_text, normalize_embeddings=True)
    dim = len(emb)
    print("SUCCESS: Model loaded!")
    print(f"Embedding dimension: {dim}")
    print(f"Embedding sample (first 5): {emb[:5]}")
    if dim == 384:
        print("DIMENSION VERIFIED: 384")
    else:
        print(f"DIMENSION MISMATCH: Expected 384, got {dim}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR loading model: {e}")
    sys.exit(1)
