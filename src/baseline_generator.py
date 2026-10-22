from retriever import retrieve_cards


# ---------------------------------------------------------
# Format source
# ---------------------------------------------------------

def format_source(source):

    if not source:
        return "Source not available"

    title = source.get("title", "Unknown source")
    version = source.get("version", "")
    pages = source.get("pdf_page", "")

    if isinstance(pages, list):
        pages = ", ".join(str(p) for p in pages)

    return f"{title} ({version}), page {pages}"


# ---------------------------------------------------------
# Baseline generation
# ---------------------------------------------------------

def generate_baseline_response(
    patient_query,
    top_k=5
):

    retrieved = retrieve_cards(
        patient_query,
        top_k=top_k
    )


    if not retrieved:

        return {
            "patient_query": patient_query,
            "retrieved_cards": [],
            "generated_response":
                "No relevant guideline evidence was retrieved."
        }


    # -----------------------------------------------------
    # Diagnosis
    # -----------------------------------------------------

    diagnosis_cards = [
        item
        for item in retrieved
        if item.get("category")
        == "probable_diagnosis"
    ]


    if diagnosis_cards:

        diagnosis_text = (
            f"Probable {diagnosis_cards[0]['disease']}. "
            f"{diagnosis_cards[0]['recommended_action']}"
        )

    else:

        diagnosis_text = (
            "No probable diagnosis card was found "
            "among the top retrieved results."
        )


    # -----------------------------------------------------
    # Investigations
    # -----------------------------------------------------

    investigation_cards = [
        item
        for item in retrieved
        if item.get("category")
        in {
            "investigation",
            "dehydration_assessment"
        }
    ]


    if investigation_cards:

        investigation_text = "\n".join(
            f"- {item['recommended_action']}"
            for item in investigation_cards
        )

    else:

        investigation_text = (
            "No investigation card was retrieved "
            "in the top results."
        )


    # -----------------------------------------------------
    # Medication / management
    # -----------------------------------------------------

    management_cards = [
        item
        for item in retrieved
        if item.get("category")
        in {
            "medication_and_management",
            "medication_and_advice"
        }
    ]


    if management_cards:

        medication_text = "\n".join(
            f"- {item['recommended_action']}"
            for item in management_cards
        )

    else:

        medication_text = (
            "No medication or management card "
            "was retrieved in the top results."
        )


    # -----------------------------------------------------
    # Advice
    # -----------------------------------------------------

    advice_cards = [
        item
        for item in retrieved
        if item.get("category")
        == "advice_and_followup"
    ]


    if advice_cards:

        advice_text = "\n".join(
            f"- {item['recommended_action']}"
            for item in advice_cards
        )

    else:

        advice_text = (
            "No specific advice card was retrieved "
            "in the top results."
        )


    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    evidence_lines = []

    for item in retrieved:

        source = format_source(
            item.get("source", {})
        )

        evidence_lines.append(
            f"- {item['card_id']}: {source}"
        )


    evidence_text = "\n".join(
        evidence_lines
    )


    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    response = f"""
Probable Diagnosis:
{diagnosis_text}

Investigations:
{investigation_text}

Medication Planning:
{medication_text}

Advice:
{advice_text}

Missing Information:
Baseline retrieval does not perform explicit applicability or missing-information checks.

Evidence:
{evidence_text}
""".strip()


    return {
        "patient_query": patient_query,
        "retrieved_cards": retrieved,
        "generated_response": response
    }


# ---------------------------------------------------------
# Test with incomplete Cholera case
# ---------------------------------------------------------

if __name__ == "__main__":

    patient_query = """
    A 35-year-old patient presents with acute watery diarrhoea
    that started today and reports several loose stools.
    """


    result = generate_baseline_response(
        patient_query,
        top_k=5
    )


    print("\n" + "=" * 75)
    print("BASELINE CLINICAL RAG")
    print("=" * 75)


    print("\nPatient:")
    print(
        result["patient_query"].strip()
    )


    print("\nGenerated Baseline Response:")
    print("-" * 75)

    print(
        result["generated_response"]
    )

    print("-" * 75)