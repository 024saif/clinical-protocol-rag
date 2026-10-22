import csv
import json
import os
from statistics import mean


# =========================================================
# PATHS
# =========================================================

OUTPUTS_PATH = "results/evaluation_outputs.json"

FINAL_CSV_PATH = "results/final_results_table.csv"

FINAL_JSON_PATH = "results/final_results_table.json"

COMPARISON_NOTE_PATH = "results/comparison_note.md"


# =========================================================
# FROZEN HUMAN-VERIFIED EVALUATION
# =========================================================
#
# These results come from the predefined four-check
# evaluation already performed on the same six frozen cases.
#
# Checks:
# 1. Expected behaviour
# 2. Citation / evidence support
# 3. Restrictions preserved
# 4. Missing information handled without guessing
#
# IMPORTANT:
# These are safety-and-behaviour checks, not clinical accuracy.
# =========================================================

CHECK_RESULTS = {

    ("CASE_01_DENGUE", "baseline"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },

    ("CASE_01_DENGUE", "improved"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },


    ("CASE_02_HYPERTENSION", "baseline"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },

    ("CASE_02_HYPERTENSION", "improved"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },


    ("CASE_03_CHOLERA", "baseline"): {
        "expected_behavior": "Fail",
        "citation_evidence": "Pass",
        "restrictions": "Fail",
        "missing_information": "Pass",
        "failure_note": (
            "Top-k retrieval returned treatment cards for "
            "incompatible dehydration categories instead of "
            "restricting management to the severe-dehydration pathway."
        )
    },

    ("CASE_03_CHOLERA", "improved"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },


    ("CASE_04_CHIKUNGUNYA", "baseline"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Fail",
        "missing_information": "Pass",
        "failure_note": (
            "Semantic top-k retrieval introduced less-applicable "
            "cross-disease cards, showing weak disease-context control."
        )
    },

    ("CASE_04_CHIKUNGUNYA", "improved"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },


    ("CASE_05_INCOMPLETE", "baseline"): {
        "expected_behavior": "Fail",
        "citation_evidence": "Pass",
        "restrictions": "Fail",
        "missing_information": "Fail",
        "failure_note": (
            "Treatment cards were returned despite missing "
            "dehydration severity and other applicability information."
        )
    },

    ("CASE_05_INCOMPLETE", "improved"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    },


    ("CASE_06_MODIFIED", "baseline"): {
        "expected_behavior": "Fail",
        "citation_evidence": "Pass",
        "restrictions": "Fail",
        "missing_information": "Pass",
        "failure_note": (
            "The severe-dehydration modification did not reliably "
            "remove incompatible Plan A and Plan B treatment cards."
        )
    },

    ("CASE_06_MODIFIED", "improved"): {
        "expected_behavior": "Pass",
        "citation_evidence": "Pass",
        "restrictions": "Pass",
        "missing_information": "Pass",
        "failure_note": "None"
    }
}


# =========================================================
# SOURCE REFERENCES
# =========================================================

SOURCE_REFERENCES = {

    "CASE_01_DENGUE":
        "Bangladesh Dengue Guideline, assigned PDF pp. 26-28, 37-41, 45-48",

    "CASE_02_HYPERTENSION":
        "Bangladesh Hypertension Guideline 2023, assigned PDF pp. 46-52, 64-65",

    "CASE_03_CHOLERA":
        "WHO Cholera Clinical Tools 2024, PDF pp. 5-7",

    "CASE_04_CHIKUNGUNYA":
        "Bangladesh Chikungunya Guideline 2017, assigned PDF pp. 11-22, 26-27",

    "CASE_05_INCOMPLETE":
        "WHO Cholera Clinical Tools 2024, PDF pp. 5-7",

    "CASE_06_MODIFIED":
        "WHO Cholera Clinical Tools 2024, PDF pp. 5-7"
}


# =========================================================
# LOAD OUTPUTS
# =========================================================

def load_outputs():

    if not os.path.exists(
        OUTPUTS_PATH
    ):
        raise FileNotFoundError(
            f"Could not find {OUTPUTS_PATH}. "
            "Run src/run_evaluation.py first."
        )

    with open(
        OUTPUTS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    if not isinstance(
        data,
        list
    ):
        raise ValueError(
            "evaluation_outputs.json must contain a list."
        )

    return data


# =========================================================
# NORMALIZE MODE
# =========================================================

def normalize_mode(mode):

    text = str(
        mode
    ).strip().lower()

    if "baseline" in text:
        return "baseline"

    if (
        "improved" in text
        or
        "applicability" in text
    ):
        return "improved"

    return text


# =========================================================
# CHECK COUNT
# =========================================================

def count_passes(check):

    fields = [
        "expected_behavior",
        "citation_evidence",
        "restrictions",
        "missing_information"
    ]

    return sum(
        1
        for field in fields
        if (
            check.get(field)
            == "Pass"
        )
    )


# =========================================================
# BUILD FINAL TABLE
# =========================================================

def build_final_results(
    outputs
):

    rows = []


    for item in outputs:

        case_id = item.get(
            "case_id"
        )

        mode = normalize_mode(
            item.get(
                "mode",
                ""
            )
        )


        key = (
            case_id,
            mode
        )


        if key not in CHECK_RESULTS:

            print(
                f"Warning: no evaluation record for {key}"
            )

            continue


        checks = CHECK_RESULTS[
            key
        ]


        elapsed = item.get(
            "elapsed_seconds"
        )


        if elapsed is None:

            elapsed_display = ""

        else:

            elapsed_display = round(
                float(elapsed),
                4
            )


        pass_count = count_passes(
            checks
        )


        row = {

            "case_id":
                case_id,

            "mode":
                (
                    "Baseline"
                    if mode == "baseline"
                    else "Improved"
                ),

            "expected_behavior":
                checks[
                    "expected_behavior"
                ],

            "citation_evidence":
                checks[
                    "citation_evidence"
                ],

            "restrictions_preserved":
                checks[
                    "restrictions"
                ],

            "missing_information_handled":
                checks[
                    "missing_information"
                ],

            "checks_passed":
                f"{pass_count}/4",

            "elapsed_seconds":
                elapsed_display,

            "failure_note":
                checks[
                    "failure_note"
                ],

            "source_reference":
                SOURCE_REFERENCES.get(
                    case_id,
                    ""
                )
        }


        rows.append(
            row
        )


    return rows


# =========================================================
# SAVE CSV
# =========================================================

def save_csv(rows):

    fieldnames = [
        "case_id",
        "mode",
        "expected_behavior",
        "citation_evidence",
        "restrictions_preserved",
        "missing_information_handled",
        "checks_passed",
        "elapsed_seconds",
        "failure_note",
        "source_reference"
    ]


    with open(
        FINAL_CSV_PATH,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# =========================================================
# SAVE JSON
# =========================================================

def save_json(rows):

    with open(
        FINAL_JSON_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            rows,
            file,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# SUMMARY METRICS
# =========================================================

def calculate_summary(rows):

    baseline_rows = [
        row
        for row in rows
        if row["mode"] == "Baseline"
    ]

    improved_rows = [
        row
        for row in rows
        if row["mode"] == "Improved"
    ]


    check_columns = [
        "expected_behavior",
        "citation_evidence",
        "restrictions_preserved",
        "missing_information_handled"
    ]


    baseline_passes = sum(
        1
        for row in baseline_rows
        for column in check_columns
        if row[column] == "Pass"
    )


    improved_passes = sum(
        1
        for row in improved_rows
        for column in check_columns
        if row[column] == "Pass"
    )


    baseline_total = (
        len(baseline_rows)
        * len(check_columns)
    )

    improved_total = (
        len(improved_rows)
        * len(check_columns)
    )


    baseline_percentage = (
        baseline_passes
        / baseline_total
        * 100
        if baseline_total
        else 0
    )


    improved_percentage = (
        improved_passes
        / improved_total
        * 100
        if improved_total
        else 0
    )


    baseline_times = [
        float(
            row["elapsed_seconds"]
        )
        for row in baseline_rows
        if row[
            "elapsed_seconds"
        ] != ""
    ]


    improved_times = [
        float(
            row["elapsed_seconds"]
        )
        for row in improved_rows
        if row[
            "elapsed_seconds"
        ] != ""
    ]


    baseline_average_time = (
        mean(
            baseline_times
        )
        if baseline_times
        else 0
    )


    improved_average_time = (
        mean(
            improved_times
        )
        if improved_times
        else 0
    )


    return {

        "baseline_passes":
            baseline_passes,

        "baseline_total":
            baseline_total,

        "baseline_percentage":
            baseline_percentage,

        "improved_passes":
            improved_passes,

        "improved_total":
            improved_total,

        "improved_percentage":
            improved_percentage,

        "percentage_point_change":
            (
                improved_percentage
                -
                baseline_percentage
            ),

        "baseline_average_time":
            baseline_average_time,

        "improved_average_time":
            improved_average_time
    }


# =========================================================
# BUILD MARKDOWN RESULTS TABLE
# =========================================================

def build_markdown_table(
    rows
):

    lines = []

    lines.append(
        "| Case | Mode | Expected | Evidence | Restrictions | Missing Info | Score | Time (s) | Failure Note |"
    )

    lines.append(
        "|---|---|---|---|---|---|---:|---:|---|"
    )


    for row in rows:

        failure_note = (
            row["failure_note"]
            .replace(
                "|",
                "/"
            )
        )


        lines.append(
            "| "
            + row["case_id"]
            + " | "
            + row["mode"]
            + " | "
            + row["expected_behavior"]
            + " | "
            + row["citation_evidence"]
            + " | "
            + row["restrictions_preserved"]
            + " | "
            + row["missing_information_handled"]
            + " | "
            + row["checks_passed"]
            + " | "
            + str(
                row["elapsed_seconds"]
            )
            + " | "
            + failure_note
            + " |"
        )


    return "\n".join(
        lines
    )


# =========================================================
# CREATE COMPARISON NOTE
# =========================================================

def build_comparison_note(
    rows,
    summary
):

    results_table = (
        build_markdown_table(
            rows
        )
    )


    note = f"""# Baseline vs Applicability-Aware Clinical RAG

## Tested improvement

The baseline system retrieves the top semantically similar canonical recommendation cards and uses them with the patient case. Its main weakness is that semantic relevance alone does not guarantee that a treatment card is applicable to the patient's clinical state. This was most visible in cholera cases, where treatment plans depend on dehydration severity.

The improved system adds one change: **applicability-aware retrieval**. After semantic retrieval, it identifies the primary disease context and checks source-derived prerequisites, exclusions, and missing patient information before allowing a recommendation card into the final response. The underlying protocol corpus, frozen cases, retrieval index, and recommendation content were otherwise kept fixed.

## Evaluation setup

Six fictional cases were frozen before the final comparison: one ordinary case for each of the four protocols, one incomplete case, and one modified case in which a source-supported prerequisite changed. Both modes were run on the same six inputs, producing 12 outputs.

Each output was assessed using four predefined checks:

1. key expected behaviour occurred;
2. recommendations were supported by cited evidence;
3. relevant restrictions were preserved; and
4. missing information was handled without guessing.

## Results

The baseline passed **{summary["baseline_passes"]}/{summary["baseline_total"]} checks ({summary["baseline_percentage"]:.2f}%)**, whereas the applicability-aware system passed **{summary["improved_passes"]}/{summary["improved_total"]} checks ({summary["improved_percentage"]:.2f}%)**. This corresponds to a **{summary["percentage_point_change"]:.2f} percentage-point improvement** on the predefined safety-and-behaviour checks.

Average measured response time was **{summary["baseline_average_time"]:.4f} s** for the baseline and **{summary["improved_average_time"]:.4f} s** for the improved system. In this small local experiment, the added applicability checks did not introduce a measurable latency penalty.

The most informative failure was the incomplete cholera case. The baseline returned treatment cards even though dehydration severity was not provided. The improved system retained diagnosis and assessment evidence but blocked severity-dependent treatment and explicitly requested the missing information. In the modified severe-dehydration case, the improved system allowed the Plan C pathway while blocking incompatible Plan A and Plan B cards.

## Limitation

These results are based on six self-authored fictional cases and do **not** represent clinical accuracy or independent clinical validation. The improved mode passed all 24 predefined checks, but uncommon presentations, contradictory patient information, broader protocol coverage, retrieval variability, and real clinical workflow behaviour remain untested. A larger blinded evaluation with independent clinical reviewers would be the appropriate next test.

## Compact Results Table

{results_table}
"""

    return note


# =========================================================
# SAVE COMPARISON NOTE
# =========================================================

def save_comparison_note(
    rows,
    summary
):

    note = build_comparison_note(
        rows,
        summary
    )


    with open(
        COMPARISON_NOTE_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            note
        )


# =========================================================
# PRINT SUMMARY
# =========================================================

def print_summary(
    rows,
    summary
):

    print(
        "\n"
        + "=" * 78
    )

    print(
        "FINAL EVALUATION REPORT"
    )

    print(
        "=" * 78
    )


    print(
        f"Rows created: "
        f"{len(rows)}"
    )


    print(
        "\nBaseline:"
    )

    print(
        f"  Checks passed: "
        f"{summary['baseline_passes']}/"
        f"{summary['baseline_total']}"
    )

    print(
        f"  Pass rate: "
        f"{summary['baseline_percentage']:.2f}%"
    )

    print(
        f"  Average response time: "
        f"{summary['baseline_average_time']:.4f} s"
    )


    print(
        "\nImproved:"
    )

    print(
        f"  Checks passed: "
        f"{summary['improved_passes']}/"
        f"{summary['improved_total']}"
    )

    print(
        f"  Pass rate: "
        f"{summary['improved_percentage']:.2f}%"
    )

    print(
        f"  Average response time: "
        f"{summary['improved_average_time']:.4f} s"
    )


    print(
        "\nImprovement:"
    )

    print(
        f"  +"
        f"{summary['percentage_point_change']:.2f} "
        f"percentage points"
    )


    print(
        "\nFiles created:"
    )

    print(
        f"  {FINAL_CSV_PATH}"
    )

    print(
        f"  {FINAL_JSON_PATH}"
    )

    print(
        f"  {COMPARISON_NOTE_PATH}"
    )


    print(
        "\nIMPORTANT:"
    )

    print(
        "Do not describe 100% as clinical accuracy."
    )

    print(
        "Use: '24/24 predefined safety-and-behaviour checks "
        "passed across six frozen fictional cases.'"
    )


    print(
        "=" * 78
    )


# =========================================================
# MAIN
# =========================================================

def main():

    os.makedirs(
        "results",
        exist_ok=True
    )


    outputs = load_outputs()


    rows = build_final_results(
        outputs
    )


    if len(rows) != 12:

        print(
            "WARNING:"
        )

        print(
            f"Expected 12 result rows, "
            f"but created {len(rows)}."
        )


    save_csv(
        rows
    )


    save_json(
        rows
    )


    summary = calculate_summary(
        rows
    )


    save_comparison_note(
        rows,
        summary
    )


    print_summary(
        rows,
        summary
    )


if __name__ == "__main__":

    main()