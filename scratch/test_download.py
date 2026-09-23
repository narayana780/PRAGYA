import os
import sys

# Disable hf_transfer and symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

print("Starting direct hf_hub_download test...")
from huggingface_hub import hf_hub_download

repo_id = "sentence-transformers/all-MiniLM-L6-v2"
for fn in ["config.json", "tokenizer.json", "model.safetensors"]:
    print(f"Downloading {fn}...")
    p = hf_hub_download(repo_id=repo_id, filename=fn)
    print(f"Downloaded {fn} to {p} (size={os.path.getsize(p)} bytes)")

print("All essential files downloaded!")
from sentence_transformers import SentenceTransformer
print("Loading model...")
model = SentenceTransformer(repo_id)
emb = model.encode("Test PRAGYA", normalize_embeddings=True)
print("SUCCESS! Dimension:", len(emb))
