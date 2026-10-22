import json


INPUT_PATH = "results/evaluation_outputs.json"
OUTPUT_PATH = "results/evaluation_metrics.json"


# ---------------------------------------------------------
# Load evaluation outputs
# ---------------------------------------------------------

def load_results():

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def contains_any(text, keywords):

    text = text.lower()

    return any(
        keyword.lower() in text
        for keyword in keywords
    )


# ---------------------------------------------------------
# Case-specific expected behavior checks
# ---------------------------------------------------------

def check_expected_behavior(
    case_id,
    mode,
    response,
    record
):

    text = response.lower()


    # -----------------------------------------------------
    # CASE 01 - Dengue
    # -----------------------------------------------------

    if case_id == "CASE_01_DENGUE":

        return (
            "dengue" in text
            and not contains_any(
                text,
                [
                    "confirmed dengue",
                    "dengue confirmed"
                ]
            )
        )


    # -----------------------------------------------------
    # CASE 02 - Hypertension
    # -----------------------------------------------------

    if case_id == "CASE_02_HYPERTENSION":

        return (
            "hypertension" in text
            and contains_any(
                text,
                [
                    "blood pressure",
                    "investigation",
                    "creatinine",
                    "ecg",
                    "sodium",
                    "potassium"
                ]
            )
        )


    # -----------------------------------------------------
    # CASE 03 - Severe Cholera
    # -----------------------------------------------------

    if case_id == "CASE_03_CHOLERA":

        if mode == "improved":

            accepted = record[
                "improved"
            ].get(
                "accepted_card_ids",
                []
            )

            rejected = [
                item["card_id"]
                for item
                in record[
                    "improved"
                ].get(
                    "rejected_cards",
                    []
                )
            ]

            return (
                "CHOLERA_MGMT_001"
                in accepted
                and
                "CHOLERA_MGMT_002"
                in rejected
                and
                "CHOLERA_MGMT_003"
                in rejected
            )

        else:

            # Baseline passes only if it avoids
            # conflicting Plan A / Plan B
            cards = record[
                "baseline"
            ].get(
                "retrieved_card_ids",
                []
            )

            return not (
                "CHOLERA_MGMT_002" in cards
                or
                "CHOLERA_MGMT_003" in cards
            )


    # -----------------------------------------------------
    # CASE 04 - Chikungunya
    # -----------------------------------------------------

    if case_id == "CASE_04_CHIKUNGUNYA":

        if mode == "improved":

            accepted = record[
                "improved"
            ].get(
                "accepted_card_ids",
                []
            )

            differentials = [
                item["disease"]
                for item
                in record[
                    "improved"
                ].get(
                    "differential_diagnoses",
                    []
                )
            ]

            return (
                "CHIK_DIAG_001"
                in accepted
                and
                "CHIK_INV_001"
                in accepted
                and
                "CHIK_MGMT_001"
                in accepted
                and
                "Dengue"
                in differentials
            )

        return (
            "chikungunya" in text
        )


    # -----------------------------------------------------
    # CASE 05 - Incomplete Cholera
    # -----------------------------------------------------

    if case_id == "CASE_05_INCOMPLETE":

        if mode == "improved":

            accepted = record[
                "improved"
            ].get(
                "accepted_card_ids",
                []
            )

            return (
                "CHOLERA_MGMT_001"
                not in accepted
                and
                "CHOLERA_MGMT_002"
                not in accepted
                and
                "CHOLERA_MGMT_003"
                not in accepted
                and
                "treatment plan should not yet be selected"
                in text
            )

        else:

            cards = record[
                "baseline"
            ].get(
                "retrieved_card_ids",
                []
            )

            return not (
                "CHOLERA_MGMT_001" in cards
                or
                "CHOLERA_MGMT_002" in cards
                or
                "CHOLERA_MGMT_003" in cards
            )


    # -----------------------------------------------------
    # CASE 06 - Modified Cholera
    # -----------------------------------------------------

    if case_id == "CASE_06_MODIFIED":

        if mode == "improved":

            accepted = record[
                "improved"
            ].get(
                "accepted_card_ids",
                []
            )

            rejected = [
                item["card_id"]
                for item
                in record[
                    "improved"
                ].get(
                    "rejected_cards",
                    []
                )
            ]

            return (
                "CHOLERA_MGMT_001"
                in accepted
                and
                "CHOLERA_MGMT_002"
                in rejected
                and
                "CHOLERA_MGMT_003"
                in rejected
            )

        else:

            cards = record[
                "baseline"
            ].get(
                "retrieved_card_ids",
                []
            )

            return not (
                "CHOLERA_MGMT_002" in cards
                or
                "CHOLERA_MGMT_003" in cards
            )


    return False


# ---------------------------------------------------------
# Citation / evidence check
# ---------------------------------------------------------

def check_evidence(response):

    text = response.lower()

    return (
        "evidence:" in text
        and
        "page" in text
    )


# ---------------------------------------------------------
# Treatment restriction check
# ---------------------------------------------------------

def check_restrictions(
    case_id,
    mode,
    response,
    record
):

    text = response.lower()


    if case_id in {
        "CASE_03_CHOLERA",
        "CASE_06_MODIFIED"
    }:

        if mode == "improved":

            rejected = [
                item["card_id"]
                for item
                in record[
                    "improved"
                ].get(
                    "rejected_cards",
                    []
                )
            ]

            return (
                "CHOLERA_MGMT_002"
                in rejected
                and
                "CHOLERA_MGMT_003"
                in rejected
            )

        else:

            cards = record[
                "baseline"
            ].get(
                "retrieved_card_ids",
                []
            )

            return not (
                "CHOLERA_MGMT_002" in cards
                or
                "CHOLERA_MGMT_003" in cards
            )


    if case_id == "CASE_04_CHIKUNGUNYA":

        return (
            "avoid" in text
            and
            "nsaid" in text
            and
            "dengue" in text
        )


    if case_id == "CASE_05_INCOMPLETE":

        if mode == "improved":

            accepted = record[
                "improved"
            ].get(
                "accepted_card_ids",
                []
            )

            return not any(
                card_id in accepted
                for card_id in [
                    "CHOLERA_MGMT_001",
                    "CHOLERA_MGMT_002",
                    "CHOLERA_MGMT_003"
                ]
            )

        else:

            cards = record[
                "baseline"
            ].get(
                "retrieved_card_ids",
                []
            )

            return not any(
                card_id in cards
                for card_id in [
                    "CHOLERA_MGMT_001",
                    "CHOLERA_MGMT_002",
                    "CHOLERA_MGMT_003"
                ]
            )


    # For other cases, no special restriction
    # failure was defined.
    return True


# ---------------------------------------------------------
# Missing-information handling check
# ---------------------------------------------------------

def check_missing_information(
    case_id,
    mode,
    response
):

    text = response.lower()


    if case_id == "CASE_05_INCOMPLETE":

        if mode == "improved":

            return (
                "missing" in text
                and
                "dehydration_severity"
                in text
                and
                "should not yet be selected"
                in text
            )

        else:

            return False


    # Cases where required information is sufficiently
    # available should not automatically fail.
    return True


# ---------------------------------------------------------
# Evaluate one mode
# ---------------------------------------------------------

def evaluate_mode(
    record,
    mode
):

    case_id = record["case_id"]

    response = record[
        mode
    ]["response"]


    expected = check_expected_behavior(
        case_id,
        mode,
        response,
        record
    )

    evidence = check_evidence(
        response
    )

    restrictions = check_restrictions(
        case_id,
        mode,
        response,
        record
    )

    missing_info = check_missing_information(
        case_id,
        mode,
        response
    )


    total_passed = sum(
        [
            expected,
            evidence,
            restrictions,
            missing_info
        ]
    )


    return {

        "expected_behavior":
            expected,

        "citation_evidence":
            evidence,

        "restrictions_preserved":
            restrictions,

        "missing_information_handled":
            missing_info,

        "checks_passed":
            total_passed,

        "total_checks":
            4
    }


# ---------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------

def main():

    results = load_results()

    evaluated = []

    baseline_total = 0
    improved_total = 0

    possible_per_mode = (
        len(results) * 4
    )


    print("\n" + "=" * 85)
    print("CLINICAL RAG EVALUATION METRICS")
    print("=" * 85)


    for record in results:

        case_id = record["case_id"]


        baseline_eval = evaluate_mode(
            record,
            "baseline"
        )

        improved_eval = evaluate_mode(
            record,
            "improved"
        )


        baseline_total += (
            baseline_eval[
                "checks_passed"
            ]
        )

        improved_total += (
            improved_eval[
                "checks_passed"
            ]
        )


        evaluated.append({

            "case_id":
                case_id,

            "baseline":
                baseline_eval,

            "improved":
                improved_eval
        })


        print(
            f"\n{case_id}"
        )

        print(
            "Baseline:",
            f"{baseline_eval['checks_passed']}/4"
        )

        print(
            "Improved:",
            f"{improved_eval['checks_passed']}/4"
        )


    baseline_percentage = (
        baseline_total
        / possible_per_mode
        * 100
    )

    improved_percentage = (
        improved_total
        / possible_per_mode
        * 100
    )


    summary = {

        "number_of_cases":
            len(results),

        "checks_per_case":
            4,

        "possible_checks_per_mode":
            possible_per_mode,

        "baseline_passed":
            baseline_total,

        "baseline_percentage":
            round(
                baseline_percentage,
                2
            ),

        "improved_passed":
            improved_total,

        "improved_percentage":
            round(
                improved_percentage,
                2
            ),

        "absolute_improvement_percentage_points":
            round(
                improved_percentage
                - baseline_percentage,
                2
            )
    }


    output = {

        "summary":
            summary,

        "cases":
            evaluated
    }


    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2
        )


    print("\n" + "=" * 85)
    print("SUMMARY")
    print("=" * 85)

    print(
        f"\nBaseline : "
        f"{baseline_total}/{possible_per_mode} "
        f"({baseline_percentage:.2f}%)"
    )

    print(
        f"Improved : "
        f"{improved_total}/{possible_per_mode} "
        f"({improved_percentage:.2f}%)"
    )

    print(
        "\nImprovement:",
        f"{improved_percentage - baseline_percentage:.2f}",
        "percentage points"
    )

    print(
        "\nSaved to:",
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()