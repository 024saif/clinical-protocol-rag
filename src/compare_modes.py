from retriever import retrieve_cards
from applicability_retriever import retrieve_applicable_cards


def print_baseline(query):

    print("\n" + "=" * 75)
    print("BASELINE RAG")
    print("=" * 75)

    results = retrieve_cards(
        query,
        top_k=5
    )

    for i, result in enumerate(results, start=1):

        print(f"\n[{i}] {result['card_id']}")
        print("Disease       :", result["disease"])
        print("Category      :", result["category"])
        print("Similarity    :", round(result["score"], 3))
        print("Recommendation:", result["recommended_action"])


def print_improved(query):

    print("\n" + "=" * 75)
    print("APPLICABILITY-AWARE RAG")
    print("=" * 75)

    (
        patient_facts,
        primary_disease,
        accepted,
        rejected,
        differential_diagnoses
    ) = retrieve_applicable_cards(
        query,
        top_k=10
    )


    # -----------------------------------------------------
    # Primary disease
    # -----------------------------------------------------

    print("\nPrimary Disease Context:")

    if primary_disease:
        print(primary_disease)
    else:
        print("Not identified")


    # -----------------------------------------------------
    # Patient facts
    # -----------------------------------------------------

    print("\nDetected Patient Facts:")

    if patient_facts:
        print(patient_facts)
    else:
        print(
            "No clinically relevant structured "
            "applicability facts detected."
        )


    # -----------------------------------------------------
    # Applicable recommendations
    # -----------------------------------------------------

    print("\nAPPLICABLE RECOMMENDATIONS")

    if not accepted:
        print(
            "\nNo currently applicable recommendation "
            "was found."
        )

    for result in accepted:

        print(f"\n{result['card_id']}")
        print("Disease       :", result["disease"])
        print("Category      :", result["category"])
        print("Similarity    :", round(result["score"], 3))
        print(
            "Applicability :",
            result["applicability_reason"]
        )
        print(
            "Recommendation:",
            result["recommended_action"]
        )


    # -----------------------------------------------------
    # Missing / rejected
    # -----------------------------------------------------

    print("\nREJECTED / NEEDS MORE INFORMATION")

    if not rejected:
        print(
            "\nNo recommendation was rejected."
        )

    for result in rejected:

        print(f"\n{result['card_id']}")
        print(
            "Similarity    :",
            round(result["score"], 3)
        )
        print(
            "Reason        :",
            result["applicability_reason"]
        )


    # -----------------------------------------------------
    # Differential diagnoses
    # -----------------------------------------------------

    print("\nDIFFERENTIAL DIAGNOSES")

    if not differential_diagnoses:

        print(
            "\nNo competing diagnosis card "
            "retrieved."
        )

    for result in differential_diagnoses:

        print(f"\n{result['card_id']}")
        print(
            "Disease       :",
            result["disease"]
        )
        print(
            "Similarity    :",
            round(result["score"], 3)
        )


if __name__ == "__main__":

    patient_query = """
    A 35-year-old patient presents with acute watery diarrhoea
    that started today. The patient reports several loose stools.
    """

    print("\nPATIENT CASE")
    print("-" * 75)
    print(patient_query.strip())

    print_baseline(patient_query)

    print_improved(patient_query)