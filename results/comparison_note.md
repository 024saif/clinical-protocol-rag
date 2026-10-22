# Baseline vs Applicability-Aware Clinical RAG

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

The baseline passed **16/24 checks (66.67%)**, whereas the applicability-aware system passed **24/24 checks (100.00%)**. This corresponds to a **33.33 percentage-point improvement** on the predefined safety-and-behaviour checks.

Average measured response time was **0.0469 s** for the baseline and **0.0279 s** for the improved system. In this small local experiment, the added applicability checks did not introduce a measurable latency penalty.

The most informative failure was the incomplete cholera case. The baseline returned treatment cards even though dehydration severity was not provided. The improved system retained diagnosis and assessment evidence but blocked severity-dependent treatment and explicitly requested the missing information. In the modified severe-dehydration case, the improved system allowed the Plan C pathway while blocking incompatible Plan A and Plan B cards.

## Limitation

These results are based on six self-authored fictional cases and do **not** represent clinical accuracy or independent clinical validation. The improved mode passed all 24 predefined checks, but uncommon presentations, contradictory patient information, broader protocol coverage, retrieval variability, and real clinical workflow behaviour remain untested. A larger blinded evaluation with independent clinical reviewers would be the appropriate next test.

## Compact Results Table

| Case | Mode | Expected | Evidence | Restrictions | Missing Info | Score | Time (s) | Failure Note |
|---|---|---|---|---|---|---:|---:|---|
| CASE_01_DENGUE | Baseline | Pass | Pass | Pass | Pass | 4/4 | 0.1432 | None |
| CASE_01_DENGUE | Improved | Pass | Pass | Pass | Pass | 4/4 | 0.0309 | None |
| CASE_02_HYPERTENSION | Baseline | Pass | Pass | Pass | Pass | 4/4 | 0.028 | None |
| CASE_02_HYPERTENSION | Improved | Pass | Pass | Pass | Pass | 4/4 | 0.0264 | None |
| CASE_03_CHOLERA | Baseline | Fail | Pass | Fail | Pass | 2/4 | 0.0304 | Top-k retrieval returned treatment cards for incompatible dehydration categories instead of restricting management to the severe-dehydration pathway. |
| CASE_03_CHOLERA | Improved | Pass | Pass | Pass | Pass | 4/4 | 0.031 | None |
| CASE_04_CHIKUNGUNYA | Baseline | Pass | Pass | Fail | Pass | 3/4 | 0.0269 | Semantic top-k retrieval introduced less-applicable cross-disease cards, showing weak disease-context control. |
| CASE_04_CHIKUNGUNYA | Improved | Pass | Pass | Pass | Pass | 4/4 | 0.0247 | None |
| CASE_05_INCOMPLETE | Baseline | Fail | Pass | Fail | Fail | 1/4 | 0.0245 | Treatment cards were returned despite missing dehydration severity and other applicability information. |
| CASE_05_INCOMPLETE | Improved | Pass | Pass | Pass | Pass | 4/4 | 0.0276 | None |
| CASE_06_MODIFIED | Baseline | Fail | Pass | Fail | Pass | 2/4 | 0.0282 | The severe-dehydration modification did not reliably remove incompatible Plan A and Plan B treatment cards. |
| CASE_06_MODIFIED | Improved | Pass | Pass | Pass | Pass | 4/4 | 0.0269 | None |
