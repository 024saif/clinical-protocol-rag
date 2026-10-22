import json
import numpy as np
import faiss

EMBEDDINGS_PATH = "rag/embeddings.npy"
CARDS_PATH = "data/canonical_cards.jsonl"

INDEX_PATH = "rag/faiss.index"
METADATA_PATH = "rag/metadata.json"


# Load embeddings
embeddings = np.load(EMBEDDINGS_PATH).astype("float32")

print("Loaded embeddings:", embeddings.shape)


# Build FAISS index
dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print("Vectors added to FAISS:", index.ntotal)


# Save FAISS index
faiss.write_index(index, INDEX_PATH)


# Load card metadata
cards = []

with open(CARDS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            cards.append(json.loads(line))


# Save metadata
with open(METADATA_PATH, "w", encoding="utf-8") as f:
    json.dump(cards, f, indent=2, ensure_ascii=False)


print("FAISS index saved to:", INDEX_PATH)
print("Metadata saved to:", METADATA_PATH)