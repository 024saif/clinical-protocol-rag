import json
import os
import time

from baseline_generator import generate_baseline_response
from clinical_generator import generate_clinical_response


# =========================================================
# PATHS
# =========================================================

CASES_PATH = "data/evaluation_cases.json"
OUTPUT_PATH = "results/evaluation_outputs.json"


# =========================================================
# LOAD CASES
# =========================================================

def load_cases():

    with open(
        CASES_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in [
            "cases",
            "evaluation_cases",
            "test_cases",
            "data"
        ]:

            value = data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(
        "Could not identify evaluation case list."
    )


# =========================================================
# CASE ID
# =========================================================

def get_case_id(case, index):

    return (
        case.get("case_id")
        or case.get("id")
        or case.get("name")
        or f"CASE_{index + 1:02d}"
    )


# =========================================================
# PATIENT INPUT
# =========================================================

def get_patient_input(case):

    """
    The current frozen evaluation dataset uses
    'patient_text' as the patient input field.

    Other possible names are also supported.
    """

    possible_fields = [
        "patient_text",
        "patient_input",
        "patient_query",
        "case_input",
        "input_text",
        "clinical_input",
        "query",
        "text",
        "description"
    ]

    for field in possible_fields:

        value = case.get(field)

        if (
            isinstance(value, str)
            and value.strip()
        ):
            return value.strip()


    # -----------------------------------------------------
    # Fallback for structured cases
    # -----------------------------------------------------

    parts = []

    age = case.get("age")

    if age:
        parts.append(
            f"{age}-year-old patient"
        )


    sex = (
        case.get("sex")
        or case.get("gender")
    )

    if sex:
        parts.append(
            f"Sex: {sex}"
        )


    duration = case.get(
        "duration"
    )

    if duration:
        parts.append(
            f"Duration: {duration}"
        )


    symptoms = (
        case.get("symptoms")
        or case.get("chief_complaint")
        or case.get("chief_complaints")
    )

    if symptoms:

        if isinstance(
            symptoms,
            list
        ):

            symptoms = ", ".join(
                str(item)
                for item in symptoms
            )

        parts.append(
            f"Symptoms: {symptoms}"
        )


    history = (
        case.get("history")
        or case.get("relevant_history")
    )

    if history:
        parts.append(
            f"Relevant history: {history}"
        )


    medicines = (
        case.get("current_medicines")
        or case.get("medicines")
        or case.get("medications")
    )

    if medicines:

        if isinstance(
            medicines,
            list
        ):

            medicines = ", ".join(
                str(item)
                for item in medicines
            )

        parts.append(
            f"Current medicines: {medicines}"
        )


    allergies = case.get(
        "allergies"
    )

    if allergies:
        parts.append(
            f"Allergies: {allergies}"
        )


    findings = (
        case.get("additional_findings")
        or case.get("findings")
        or case.get("clinical_findings")
    )

    if findings:
        parts.append(
            f"Clinical findings: {findings}"
        )


    if parts:

        return ". ".join(
            parts
        ) + "."


    raise ValueError(
        "Could not identify patient input for "
        f"case {case.get('case_id', 'unknown')}."
    )


# =========================================================
# RUN BASELINE WITH TIMER
# =========================================================

def run_baseline(
    patient_input
):

    start_time = (
        time.perf_counter()
    )

    result = (
        generate_baseline_response(
            patient_input,
            top_k=5
        )
    )

    elapsed_seconds = (
        time.perf_counter()
        - start_time
    )

    return (
        result,
        elapsed_seconds
    )


# =========================================================
# RUN IMPROVED WITH TIMER
# =========================================================

def run_improved(
    patient_input
):

    start_time = (
        time.perf_counter()
    )

    result = (
        generate_clinical_response(
            patient_input,
            top_k=10
        )
    )

    elapsed_seconds = (
        time.perf_counter()
        - start_time
    )

    return (
        result,
        elapsed_seconds
    )


# =========================================================
# PREPARE OUTPUT RECORD
# =========================================================

def prepare_output_record(
    case,
    case_id,
    mode,
    patient_input,
    result,
    elapsed_seconds
):

    record = {

        "case_id":
            case_id,

        "case_type":
            case.get(
                "case_type"
            ),

        "protocol":
            case.get(
                "protocol"
            ),

        "mode":
            mode,

        "patient_text":
            patient_input,

        "elapsed_seconds":
            round(
                elapsed_seconds,
                4
            ),

        "generated_response":
            result.get(
                "generated_response",
                ""
            )
    }


    # -----------------------------------------------------
    # Preserve expected checklist
    # -----------------------------------------------------

    if "expected_checklist" in case:

        record[
            "expected_checklist"
        ] = case[
            "expected_checklist"
        ]


    # -----------------------------------------------------
    # Preserve model/retrieval details
    # -----------------------------------------------------

    optional_fields = [
        "primary_disease",
        "patient_facts",
        "accepted_cards",
        "rejected_cards",
        "differential_diagnoses",
        "retrieved_cards"
    ]


    for field in optional_fields:

        if field in result:

            record[field] = (
                result[field]
            )


    return record


# =========================================================
# RUN FULL EVALUATION
# =========================================================

def run_evaluation():

    cases = load_cases()

    os.makedirs(
        "results",
        exist_ok=True
    )

    outputs = []


    print(
        "\n"
        + "=" * 76
    )

    print(
        "CLINICAL RAG EVALUATION"
    )

    print(
        "=" * 76
    )

    print(
        f"Frozen cases: {len(cases)}"
    )

    print(
        "Modes: Baseline + Applicability-Aware"
    )

    print(
        f"Expected outputs: {len(cases) * 2}"
    )

    print(
        "=" * 76
    )


    # =====================================================
    # RUN EACH CASE
    # =====================================================

    for index, case in enumerate(
        cases
    ):

        case_id = get_case_id(
            case,
            index
        )

        patient_input = (
            get_patient_input(
                case
            )
        )


        print(
            f"\n[{index + 1}/{len(cases)}] "
            f"{case_id}"
        )

        print(
            "-" * 76
        )

        print(
            "Patient input:"
        )

        print(
            patient_input
        )


        # -------------------------------------------------
        # BASELINE
        # -------------------------------------------------

        try:

            (
                baseline_result,
                baseline_time
            ) = run_baseline(
                patient_input
            )


            baseline_record = (
                prepare_output_record(
                    case=case,
                    case_id=case_id,
                    mode="baseline",
                    patient_input=patient_input,
                    result=baseline_result,
                    elapsed_seconds=baseline_time
                )
            )


            outputs.append(
                baseline_record
            )


            print(
                "\nBaseline:"
            )

            print(
                f"  elapsed = "
                f"{baseline_time:.4f} seconds"
            )


        except Exception as error:

            print(
                "\nBaseline ERROR:"
            )

            print(
                f"  {type(error).__name__}: "
                f"{error}"
            )


            outputs.append(
                {
                    "case_id":
                        case_id,

                    "case_type":
                        case.get(
                            "case_type"
                        ),

                    "protocol":
                        case.get(
                            "protocol"
                        ),

                    "mode":
                        "baseline",

                    "patient_text":
                        patient_input,

                    "elapsed_seconds":
                        None,

                    "generated_response":
                        "",

                    "expected_checklist":
                        case.get(
                            "expected_checklist",
                            {}
                        ),

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        )
                }
            )


        # -------------------------------------------------
        # IMPROVED
        # -------------------------------------------------

        try:

            (
                improved_result,
                improved_time
            ) = run_improved(
                patient_input
            )


            improved_record = (
                prepare_output_record(
                    case=case,
                    case_id=case_id,
                    mode="improved",
                    patient_input=patient_input,
                    result=improved_result,
                    elapsed_seconds=improved_time
                )
            )


            outputs.append(
                improved_record
            )


            print(
                "Improved:"
            )

            print(
                f"  elapsed = "
                f"{improved_time:.4f} seconds"
            )


        except Exception as error:

            print(
                "\nImproved ERROR:"
            )

            print(
                f"  {type(error).__name__}: "
                f"{error}"
            )


            outputs.append(
                {
                    "case_id":
                        case_id,

                    "case_type":
                        case.get(
                            "case_type"
                        ),

                    "protocol":
                        case.get(
                            "protocol"
                        ),

                    "mode":
                        "improved",

                    "patient_text":
                        patient_input,

                    "elapsed_seconds":
                        None,

                    "generated_response":
                        "",

                    "expected_checklist":
                        case.get(
                            "expected_checklist",
                            {}
                        ),

                    "error":
                        (
                            f"{type(error).__name__}: "
                            f"{error}"
                        )
                }
            )


    # =====================================================
    # SAVE OUTPUTS
    # =====================================================

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            outputs,
            file,
            indent=2,
            ensure_ascii=False
        )


    # =====================================================
    # RESPONSE TIME SUMMARY
    # =====================================================

    baseline_times = [
        item["elapsed_seconds"]
        for item in outputs
        if (
            item.get("mode")
            == "baseline"
            and item.get(
                "elapsed_seconds"
            ) is not None
        )
    ]


    improved_times = [
        item["elapsed_seconds"]
        for item in outputs
        if (
            item.get("mode")
            == "improved"
            and item.get(
                "elapsed_seconds"
            ) is not None
        )
    ]


    print(
        "\n"
        + "=" * 76
    )

    print(
        "EVALUATION COMPLETE"
    )

    print(
        "=" * 76
    )


    print(
        f"Saved outputs: "
        f"{len(outputs)} / "
        f"{len(cases) * 2}"
    )


    print(
        f"Output file: "
        f"{OUTPUT_PATH}"
    )


    if baseline_times:

        average_baseline = (
            sum(baseline_times)
            /
            len(baseline_times)
        )

        print(
            "Average baseline response time: "
            f"{average_baseline:.4f} seconds"
        )


    if improved_times:

        average_improved = (
            sum(improved_times)
            /
            len(improved_times)
        )

        print(
            "Average improved response time: "
            f"{average_improved:.4f} seconds"
        )


    print(
        "=" * 76
    )


    return outputs


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_evaluation()