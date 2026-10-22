import json
import numpy as np
from sentence_transformers import SentenceTransformer

CARDS_PATH = "data/canonical_cards.jsonl"
OUTPUT_PATH = "rag/embeddings.npy"


def load_cards():
    cards = []

    with open(CARDS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cards.append(json.loads(line))

    return cards


def card_to_text(card):
    parts = [
        f"Disease: {card.get('disease', '')}",
        f"Category: {card.get('clinical_category', '')}",
        f"Symptoms or prerequisites: {card.get('symptoms_or_prerequisites', [])}",
        f"Recommended action: {card.get('recommended_action', '')}",
        f"Conditions: {card.get('conditions', [])}",
        f"Missing or exclusions: {card.get('exclusions_or_missing_information', [])}",
        f"Advice: {card.get('advice', [])}",
        f"Evidence: {card.get('evidence', '')}"
    ]

    return " ".join(parts)


cards = load_cards()

texts = [card_to_text(card) for card in cards]

print("Loaded cards:", len(cards))

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True
)

np.save(OUTPUT_PATH, embeddings)

print("Embedding shape:", embeddings.shape)
print("Saved to:", OUTPUT_PATH)