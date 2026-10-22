from applicability_retriever import retrieve_applicable_cards


# =========================================================
# SOURCE FORMATTING
# =========================================================

def format_source(source):

    if not source:
        return "Source information unavailable"

    # Source may occasionally arrive as a string
    if isinstance(source, str):
        return source

    if not isinstance(source, dict):
        return str(source)

    title = source.get(
        "title",
        "Unknown source"
    )

    version = source.get(
        "version",
        ""
    )

    pages = source.get(
        "pdf_page",
        source.get(
            "page",
            ""
        )
    )

    # -----------------------------------------------------
    # Format pages
    # -----------------------------------------------------

    if isinstance(pages, list):

        pages = ", ".join(
            str(page)
            for page in pages
        )

    elif pages is None:

        pages = ""

    else:

        pages = str(pages)


    # -----------------------------------------------------
    # Build source string
    # -----------------------------------------------------

    source_text = title

    if version:

        source_text += (
            f" ({version})"
        )

    if pages:

        if "," in pages:

            source_text += (
                f", pages {pages}"
            )

        else:

            source_text += (
                f", page {pages}"
            )

    return source_text


# =========================================================
# SAFE LIST NORMALIZATION
# =========================================================

def ensure_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


# =========================================================
# MEDICATION FORMATTING
# =========================================================

def format_single_medication(med):

    """
    Safely formats medication information.

    Supported inputs:
    - dictionary
    - string
    - number / other printable value
    """

    # -----------------------------------------------------
    # String medication
    # -----------------------------------------------------

    if isinstance(med, str):

        clean_text = med.strip()

        if clean_text:
            return clean_text

        return None


    # -----------------------------------------------------
    # Dictionary medication
    # -----------------------------------------------------

    if isinstance(med, dict):

        name = med.get(
            "name"
        )

        dose = med.get(
            "dose"
        )

        route = med.get(
            "route"
        )

        frequency = med.get(
            "frequency"
        )

        duration = med.get(
            "duration"
        )

        instructions = med.get(
            "instructions"
        )


        parts = []


        if name:

            parts.append(
                str(name)
            )


        if dose:

            parts.append(
                f"dose: {dose}"
            )


        if route:

            parts.append(
                f"route: {route}"
            )


        if frequency:

            parts.append(
                f"frequency: {frequency}"
            )


        if duration:

            parts.append(
                f"duration: {duration}"
            )


        if instructions:

            # Instructions may itself be a list
            if isinstance(
                instructions,
                list
            ):

                instruction_text = "; ".join(
                    str(item)
                    for item in instructions
                    if item
                )

            else:

                instruction_text = str(
                    instructions
                )


            if instruction_text:

                parts.append(
                    f"instructions: "
                    f"{instruction_text}"
                )


        # If dictionary exists but does not use the
        # expected medication keys, preserve its content.
        if not parts:

            fallback_parts = []

            for key, value in med.items():

                if value is None:
                    continue

                fallback_parts.append(
                    f"{key}: {value}"
                )

            if fallback_parts:

                return "; ".join(
                    fallback_parts
                )

            return None


        return "; ".join(
            parts
        )


    # -----------------------------------------------------
    # Other data type
    # -----------------------------------------------------

    if med is not None:

        return str(
            med
        )

    return None


def format_medication(
    medication_data
):

    """
    Returns formatted medication bullet lines.

    Handles:
    - None
    - one dictionary
    - one string
    - list of dictionaries
    - list of strings
    - mixed list
    """

    medications = ensure_list(
        medication_data
    )

    lines = []


    for med in medications:

        formatted = (
            format_single_medication(
                med
            )
        )

        if formatted:

            lines.append(
                f"- {formatted}"
            )


    return lines


# =========================================================
# ADVICE FORMATTING
# =========================================================

def format_advice(
    advice_data
):

    advice_items = ensure_list(
        advice_data
    )

    lines = []


    for advice in advice_items:

        if advice is None:
            continue


        if isinstance(
            advice,
            dict
        ):

            text = (
                advice.get("text")
                or
                advice.get("advice")
                or
                advice.get("instruction")
            )

            if not text:

                text = "; ".join(
                    f"{key}: {value}"
                    for key, value
                    in advice.items()
                    if value is not None
                )

        else:

            text = str(
                advice
            )


        if text.strip():

            lines.append(
                f"- {text.strip()}"
            )


    return lines


# =========================================================
# CARD HELPERS
# =========================================================

def get_card_category(card):

    return (
        card.get(
            "category"
        )
        or
        card.get(
            "clinical_category"
        )
        or
        ""
    )


def get_recommended_action(card):

    return (
        card.get(
            "recommended_action"
        )
        or
        card.get(
            "action"
        )
        or
        ""
    )


def get_medication_data(card):

    """
    Supports several possible canonical field names
    without changing the card data.
    """

    possible_fields = [
        "medications",
        "medication",
        "medication_details",
        "drug_details",
        "drugs"
    ]


    for field in possible_fields:

        if field in card:

            value = card.get(
                field
            )

            if value:

                return value


    return None


def get_advice_data(card):

    possible_fields = [
        "advice",
        "patient_advice",
        "instructions",
        "recommendations"
    ]


    for field in possible_fields:

        if field in card:

            value = card.get(
                field
            )

            if value:

                return value


    return None


# =========================================================
# MISSING INFORMATION
# =========================================================

def collect_missing_information(
    rejected_cards
):

    missing_lines = []


    for card in rejected_cards:

        reason = (
            card.get(
                "applicability_reason"
            )
            or
            card.get(
                "reason"
            )
            or
            ""
        )


        if not reason:

            continue


        lower_reason = (
            reason.lower()
        )


        if (
            "missing required information"
            in lower_reason
            or
            "missing applicability information"
            in lower_reason
        ):

            line = (
                f"- {reason}"
            )

            if line not in missing_lines:

                missing_lines.append(
                    line
                )


    return missing_lines


# =========================================================
# DIAGNOSIS SECTION
# =========================================================

def build_diagnosis_section(
    primary_disease,
    accepted_cards,
    differential_diagnoses
):

    diagnosis_cards = []

    for card in accepted_cards:

        category = get_card_category(
            card
        )

        if category == "probable_diagnosis":

            diagnosis_cards.append(
                card
            )


    # -----------------------------------------------------
    # Primary diagnosis
    # -----------------------------------------------------

    if diagnosis_cards:

        diagnosis_action = (
            get_recommended_action(
                diagnosis_cards[0]
            )
        )

        if primary_disease:

            diagnosis_text = (
                f"Probable {primary_disease}."
            )

        else:

            diagnosis_text = (
                "Probable diagnosis identified."
            )


        if diagnosis_action:

            diagnosis_text += (
                f" {diagnosis_action}"
            )

    elif primary_disease:

        diagnosis_text = (
            f"Probable {primary_disease}."
        )

    else:

        diagnosis_text = (
            "No sufficiently supported probable "
            "diagnosis was identified."
        )


    # -----------------------------------------------------
    # Differential diagnoses
    # -----------------------------------------------------

    differential_names = []


    for item in differential_diagnoses:

        disease = item.get(
            "disease"
        )

        if (
            disease
            and
            disease not in differential_names
        ):

            differential_names.append(
                disease
            )


    if differential_names:

        diagnosis_text += (
            " Differential diagnosis retrieved: "
            + ", ".join(
                differential_names
            )
            + "."
        )


    return diagnosis_text


# =========================================================
# INVESTIGATION SECTION
# =========================================================

def build_investigation_section(
    accepted_cards
):

    investigation_categories = {
        "investigation",
        "dehydration_assessment"
    }

    investigation_lines = []


    for card in accepted_cards:

        category = get_card_category(
            card
        )

        if category not in investigation_categories:
            continue


        action = get_recommended_action(
            card
        )


        if action:

            line = (
                f"- {action}"
            )

            if line not in investigation_lines:

                investigation_lines.append(
                    line
                )


    if investigation_lines:

        return "\n".join(
            investigation_lines
        )


    return (
        "No additional investigation recommendation "
        "was explicitly supported by the currently "
        "applicable cards."
    )


# =========================================================
# MEDICATION SECTION
# =========================================================

def build_medication_section(
    accepted_cards,
    rejected_cards
):

    management_categories = {
        "medication_and_management",
        "medication_and_advice"
    }

    medication_lines = []

    management_cards_found = False


    # -----------------------------------------------------
    # Accepted management cards
    # -----------------------------------------------------

    for card in accepted_cards:

        category = get_card_category(
            card
        )


        if category not in management_categories:
            continue


        management_cards_found = True


        medication_data = (
            get_medication_data(
                card
            )
        )


        formatted_meds = (
            format_medication(
                medication_data
            )
        )


        # Structured medication available
        if formatted_meds:

            for line in formatted_meds:

                if line not in medication_lines:

                    medication_lines.append(
                        line
                    )


        # No structured medication field:
        # preserve guideline action instead.
        else:

            action = (
                get_recommended_action(
                    card
                )
            )

            if action:

                line = (
                    f"- {action}"
                )

                if line not in medication_lines:

                    medication_lines.append(
                        line
                    )


    # -----------------------------------------------------
    # If applicable treatment exists
    # -----------------------------------------------------

    if medication_lines:

        return "\n".join(
            medication_lines
        )


    # -----------------------------------------------------
    # Determine whether treatment cards were blocked
    # because applicability info is missing.
    # -----------------------------------------------------

    missing_applicability_for_management = False


    for card in rejected_cards:

        category = get_card_category(
            card
        )

        reason = (
            card.get(
                "applicability_reason"
            )
            or
            ""
        )


        if category not in management_categories:
            continue


        lower_reason = reason.lower()


        if (
            "missing required information"
            in lower_reason
            or
            "missing applicability information"
            in lower_reason
        ):

            missing_applicability_for_management = True
            break


    if missing_applicability_for_management:

        return (
            "A treatment plan should not yet be selected "
            "because required applicability information "
            "is missing."
        )


    if management_cards_found:

        return (
            "No structured medication recommendation "
            "was available from the applicable cards."
        )


    return (
        "No medication or treatment plan was explicitly "
        "supported by the currently applicable cards."
    )


# =========================================================
# ADVICE SECTION
# =========================================================

def build_advice_section(
    accepted_cards
):

    advice_lines = []


    for card in accepted_cards:

        advice_data = (
            get_advice_data(
                card
            )
        )


        formatted = (
            format_advice(
                advice_data
            )
        )


        for line in formatted:

            if line not in advice_lines:

                advice_lines.append(
                    line
                )


    if advice_lines:

        return "\n".join(
            advice_lines
        )


    return (
        "No additional patient advice was explicitly "
        "supported by the currently applicable cards."
    )


# =========================================================
# EVIDENCE SECTION
# =========================================================

def build_evidence_section(
    accepted_cards
):

    evidence_lines = []


    for card in accepted_cards:

        card_id = card.get(
            "card_id",
            "Unknown card"
        )

        source = format_source(
            card.get(
                "source",
                {}
            )
        )


        line = (
            f"- {card_id}: {source}"
        )


        if line not in evidence_lines:

            evidence_lines.append(
                line
            )


    if evidence_lines:

        return "\n".join(
            evidence_lines
        )


    return (
        "No supporting evidence cards were available."
    )


# =========================================================
# BUILD STRUCTURED RESPONSE
# =========================================================

def build_structured_response(
    primary_disease,
    accepted_cards,
    rejected_cards,
    differential_diagnoses
):

    # -----------------------------------------------------
    # Diagnosis
    # -----------------------------------------------------

    diagnosis_text = (
        build_diagnosis_section(
            primary_disease,
            accepted_cards,
            differential_diagnoses
        )
    )


    # -----------------------------------------------------
    # Investigations
    # -----------------------------------------------------

    investigation_text = (
        build_investigation_section(
            accepted_cards
        )
    )


    # -----------------------------------------------------
    # Medication
    # -----------------------------------------------------

    medication_text = (
        build_medication_section(
            accepted_cards,
            rejected_cards
        )
    )


    # -----------------------------------------------------
    # Advice
    # -----------------------------------------------------

    advice_text = (
        build_advice_section(
            accepted_cards
        )
    )


    # -----------------------------------------------------
    # Missing information
    # -----------------------------------------------------

    missing_lines = (
        collect_missing_information(
            rejected_cards
        )
    )


    if missing_lines:

        missing_text = "\n".join(
            missing_lines
        )

    else:

        missing_text = (
            "No major applicability information "
            "was identified as missing."
        )


    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    evidence_text = (
        build_evidence_section(
            accepted_cards
        )
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
{missing_text}

Evidence:
{evidence_text}
""".strip()


    return response


# =========================================================
# MAIN GENERATION FUNCTION
# =========================================================

def generate_clinical_response(
    patient_query,
    top_k=10
):

    (
        patient_facts,
        primary_disease,
        accepted_cards,
        rejected_cards,
        differential_diagnoses
    ) = retrieve_applicable_cards(
        patient_query,
        top_k=top_k
    )


    generated_response = (
        build_structured_response(
            primary_disease,
            accepted_cards,
            rejected_cards,
            differential_diagnoses
        )
    )


    return {

        "patient_query":
            patient_query,

        "patient_facts":
            patient_facts,

        "primary_disease":
            primary_disease,

        "accepted_cards":
            accepted_cards,

        "rejected_cards":
            rejected_cards,

        "differential_diagnoses":
            differential_diagnoses,

        "generated_response":
            generated_response
    }


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":

    patient_query = """
    A 35-year-old patient presents with acute watery diarrhoea.
    The patient has a weak pulse, sunken eyes, cannot drink
    properly and has severe dehydration.
    """


    result = generate_clinical_response(
        patient_query,
        top_k=10
    )


    print(
        "\n"
        + "=" * 75
    )

    print(
        "CLINICAL NLP RESPONSE"
    )

    print(
        "=" * 75
    )


    print(
        "\nPatient:"
    )

    print(
        result[
            "patient_query"
        ].strip()
    )


    print(
        "\nPrimary Disease Context:"
    )

    print(
        result[
            "primary_disease"
        ]
    )


    print(
        "\nDetected Patient Facts:"
    )

    if result[
        "patient_facts"
    ]:

        print(
            result[
                "patient_facts"
            ]
        )

    else:

        print(
            "No structured applicability facts detected."
        )


    print(
        "\nDifferential Diagnoses:"
    )

    if result[
        "differential_diagnoses"
    ]:

        for item in result[
            "differential_diagnoses"
        ]:

            print(
                "-",
                item.get(
                    "disease"
                ),
                "| score:",
                round(
                    item.get(
                        "score",
                        0
                    ),
                    3
                )
            )

    else:

        print(
            "No sufficiently supported differential diagnosis."
        )


    print(
        "\nGenerated Clinical Response:"
    )

    print(
        "-" * 75
    )

    print(
        result[
            "generated_response"
        ]
    )

    print(
        "-" * 75
    )