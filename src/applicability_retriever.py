import json
import re
import faiss
from sentence_transformers import SentenceTransformer


INDEX_PATH = "rag/faiss.index"
METADATA_PATH = "rag/metadata.json"
RULES_PATH = "data/applicability_rules.json"

DIFFERENTIAL_MIN_SCORE = 0.35
DIFFERENTIAL_MAX_GAP = 0.10


# ---------------------------------------------------------
# Load resources
# ---------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index(INDEX_PATH)

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    cards = json.load(f)

with open(RULES_PATH, "r", encoding="utf-8") as f:
    rules = json.load(f)


# ---------------------------------------------------------
# Detect patient facts
# ---------------------------------------------------------

def detect_patient_facts(query):

    text = query.lower()

    facts = {}


    # -----------------------------------------------------
    # Dehydration severity
    # -----------------------------------------------------

    if (
        "severe dehydration" in text
        or "weak pulse" in text
        or "unable to drink" in text
        or "drinks poorly" in text
    ):
        facts["dehydration_severity"] = "severe"

    elif (
        "some dehydration" in text
        or "thirsty" in text
        or "rapid pulse" in text
        or "restless" in text
    ):
        facts["dehydration_severity"] = "some"

    elif (
        "no dehydration" in text
        or "no signs of dehydration" in text
    ):
        facts["dehydration_severity"] = "none"


    # -----------------------------------------------------
    # Severe dehydration flag
    # -----------------------------------------------------

    if facts.get("dehydration_severity") == "severe":
        facts["severe_dehydration"] = True


    # -----------------------------------------------------
    # Pregnancy
    # -----------------------------------------------------

    if (
        "pregnant" in text
        or "pregnancy" in text
    ):
        facts["pregnancy"] = True


    # -----------------------------------------------------
    # Elderly
    # -----------------------------------------------------

    if (
        "elderly" in text
        or "older adult" in text
        or "geriatric" in text
    ):
        facts["elderly"] = True

    else:

        age_match = re.search(
            r"\b(\d{1,3})\s*[- ]?year[- ]?old\b",
            text
        )

        if age_match:

            age = int(age_match.group(1))

            if age >= 60:
                facts["elderly"] = True


    return facts


# ---------------------------------------------------------
# Applicability checker
# ---------------------------------------------------------

def check_applicability(card_id, patient_facts):

    if card_id not in rules:
        return True, "No special applicability rule."

    rule = rules[card_id]

    requires = rule.get("requires", {})
    requires_any = rule.get("requires_any", {})
    excludes = rule.get("excludes", {})


    # Required conditions
    for field, allowed_values in requires.items():

        if field not in patient_facts:

            return False, (
                f"Missing required information: {field}"
            )

        if patient_facts[field] not in allowed_values:

            return False, (
                f"Not applicable because "
                f"{field}={patient_facts[field]}"
            )


    # Requires any
    if requires_any:

        any_condition_met = False

        for field, required_value in requires_any.items():

            if (
                field in patient_facts
                and patient_facts[field] == required_value
            ):
                any_condition_met = True
                break

        if not any_condition_met:

            missing_fields = ", ".join(
                requires_any.keys()
            )

            return False, (
                "Missing applicability information: "
                + missing_fields
            )


    # Exclusions
    for field, excluded_values in excludes.items():

        if (
            field in patient_facts
            and patient_facts[field] in excluded_values
        ):

            return False, (
                f"Excluded because "
                f"{field}={patient_facts[field]}"
            )


    return True, "Applicable to current patient."


# ---------------------------------------------------------
# Identify primary disease
# ---------------------------------------------------------

def identify_primary_disease(retrieved_items):

    diagnosis_cards = []

    for item in retrieved_items:

        card = item["card"]

        if (
            card.get("clinical_category")
            == "probable_diagnosis"
        ):
            diagnosis_cards.append(item)

    if not diagnosis_cards:
        return None, None

    diagnosis_cards.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    best = diagnosis_cards[0]

    return (
        best["card"]["disease"],
        best["score"]
    )


# ---------------------------------------------------------
# Applicability-aware retrieval
# ---------------------------------------------------------

def retrieve_applicable_cards(query, top_k=10):

    patient_facts = detect_patient_facts(query)

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    retrieved_items = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx == -1:
            continue

        retrieved_items.append({
            "score": float(score),
            "card": cards[idx]
        })


    (
        primary_disease,
        primary_score
    ) = identify_primary_disease(
        retrieved_items
    )


    accepted = []
    rejected = []
    differential_diagnoses = []


    for item in retrieved_items:

        score = item["score"]
        card = item["card"]

        disease = card["disease"]
        category = card["clinical_category"]


        # -------------------------------------------------
        # Other disease cards
        # -------------------------------------------------

        if (
            primary_disease
            and disease != primary_disease
        ):

            if (
                category == "probable_diagnosis"
                and primary_score is not None
            ):

                score_gap = primary_score - score

                if (
                    score >= DIFFERENTIAL_MIN_SCORE
                    and score_gap <= DIFFERENTIAL_MAX_GAP
                ):

                    differential_diagnoses.append({
                        "score": score,
                        "card_id": card["card_id"],
                        "disease": disease,
                        "category": category,
                        "recommended_action":
                            card["recommended_action"],
                        "source":
                            card.get("source", {})
                    })

            continue


        # -------------------------------------------------
        # Applicability
        # -------------------------------------------------

        applicable, reason = check_applicability(
            card["card_id"],
            patient_facts
        )


        result = {
            "score": score,
            "card_id": card["card_id"],
            "disease": disease,
            "category": category,
            "recommended_action":
                card["recommended_action"],
            "advice":
                card.get("advice", []),
            "medication":
                card.get("medication", []),
            "conditions":
                card.get("conditions", []),
            "missing_fields":
                card.get(
                    "exclusions_or_missing_information",
                    []
                ),
            "source":
                card.get("source", {}),
            "applicability_reason":
                reason
        }


        if applicable:
            accepted.append(result)

        else:
            rejected.append(result)


    return (
        patient_facts,
        primary_disease,
        accepted,
        rejected,
        differential_diagnoses
    )


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    patient_query = """
    A 32-year-old patient developed sudden high fever,
    severe pain in multiple joints, headache and skin rash 3 days ago.
    """

    (
        patient_facts,
        primary_disease,
        accepted,
        rejected,
        differential_diagnoses
    ) = retrieve_applicable_cards(
        patient_query,
        top_k=10
    )


    print("\n" + "=" * 70)
    print("APPLICABILITY-AWARE CLINICAL RAG")
    print("=" * 70)


    print("\nPrimary Disease Context:")
    print(primary_disease)


    print("\nDetected Patient Facts:")

    if patient_facts:
        print(patient_facts)
    else:
        print(
            "No clinically relevant structured "
            "applicability facts detected."
        )


    print("\nAPPLICABLE CARDS\n")

    for result in accepted:

        print(result["card_id"])
        print("Disease       :", result["disease"])
        print("Category      :", result["category"])
        print(
            "Similarity    :",
            round(result["score"], 3)
        )
        print(
            "Applicability :",
            result["applicability_reason"]
        )

        if result["advice"]:
            print(
                "Advice         :",
                result["advice"]
            )

        print("-" * 70)


    print(
        "\nREJECTED / NEEDS MORE INFORMATION\n"
    )

    if not rejected:
        print("No cards were rejected.")

    for result in rejected:

        print(result["card_id"])
        print(
            "Similarity    :",
            round(result["score"], 3)
        )
        print(
            "Reason        :",
            result["applicability_reason"]
        )
        print("-" * 70)


    print("\nDIFFERENTIAL DIAGNOSES\n")

    if not differential_diagnoses:

        print(
            "No sufficiently supported competing "
            "diagnosis retrieved."
        )

    for result in differential_diagnoses:

        print(result["card_id"])
        print(
            "Disease       :",
            result["disease"]
        )
        print(
            "Similarity    :",
            round(result["score"], 3)
        )
        print("-" * 70)