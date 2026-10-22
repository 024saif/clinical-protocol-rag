import json
import faiss
from sentence_transformers import SentenceTransformer

INDEX_PATH = "rag/faiss.index"
METADATA_PATH = "rag/metadata.json"

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index(INDEX_PATH)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    cards = json.load(f)


def retrieve_cards(query, top_k=3):
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        card = cards[idx]

        results.append({
            "score": float(score),
            "card_id": card["card_id"],
            "disease": card["disease"],
            "category": card["clinical_category"],
            "recommended_action": card["recommended_action"],
            "source": card["source"]
        })

    return results


if __name__ == "__main__":

    patient_query = """
   A 40-year-old patient presents with sudden acute watery diarrhoea,
very weak pulse, sunken eyes and is unable to drink properly.
The patient appears severely dehydrated.
   """

    results = retrieve_cards(patient_query, top_k=3)

    print("\n" + "=" * 65)
    print("CLINICAL RAG RETRIEVAL TEST")
    print("=" * 65)

    print("\nPatient Case:")
    print(patient_query.strip())

    print("\nTop Retrieved Evidence:\n")

    for i, result in enumerate(results, start=1):

        source = result["source"]

        pages = source.get("pdf_page")

        if isinstance(pages, list):
            pages = ", ".join(str(page) for page in pages)

        print(f"[{i}] {result['card_id']}")
        print(f"Disease       : {result['disease']}")
        print(f"Category      : {result['category']}")
        print(f"Similarity    : {result['score']:.3f}")
        print(f"Recommendation: {result['recommended_action']}")
        print(
            f"Evidence      : {source['title']} "
            f"({source['version']}), page {pages}"
        )

        print("-" * 65)