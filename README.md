# Clinical Protocol RAG

## Overview

Clinical Protocol RAG is a small protocol-grounded clinical recommendation prototype developed for the Clinical NLP assessment.

The system accepts patient symptoms and available clinical context, retrieves relevant evidence from four supplied clinical protocols, and produces:

- probable diagnosis or differential diagnosis;
- suggested investigations;
- medication and treatment planning;
- patient advice;
- missing-information warnings; and
- protocol evidence references.

The prototype includes two runnable modes:

1. **Baseline RAG**
2. **Applicability-Aware Clinical RAG**

The improved mode was designed to reduce errors that occur when a semantically relevant recommendation is not actually applicable to the patient's clinical condition.

---

# Supported Clinical Protocols

The prototype uses assigned sections from four supplied protocols:

1. Bangladesh Dengue Guideline, Fifth Edition
2. Bangladesh Hypertension Guideline, Second Edition 2023
3. WHO Clinical Tools for Cholera Treatment Facilities, 2024
4. Bangladesh Chikungunya Guideline, 2017

Protocol evidence is converted into canonical recommendation cards with source-page traceability.

---

# Core Idea

The baseline system performs semantic retrieval of the top matching recommendation cards.

The improved system adds an applicability-aware stage:

```text
Patient Input
     |
     v
Semantic Retrieval
     |
     v
Primary Disease Context
     |
     v
Applicability Check
     |
     v
Missing-Information Check
     |
     v
Structured Recommendation
```

The applicability-aware stage checks source-derived prerequisites, exclusions, and required patient information before a recommendation is used.

If a required clinical detail is missing, the system avoids guessing and reports what additional information is needed.

---

# Canonical Recommendation Cards

The clinical knowledge base is stored in:

```text
data/canonical_cards.jsonl
```

The current prototype contains 17 canonical cards across the four protocols.

Each card may contain:

- card ID
- disease
- clinical category
- relevant symptoms
- prerequisites
- exclusions
- missing-information requirements
- recommended action
- medication details where supported
- patient advice
- protocol title
- protocol version
- PDF page
- supporting evidence passage

Medication fields such as dose, route, frequency, duration, and instructions are retained only when supported by the source protocol.

---

# Reasoning Challenge: Representing Conditional Treatment Logic

One clinically important recommendation in the prototype is Cholera treatment selection based on dehydration severity.

There are at least two possible ways to represent this logic.

## Representation A — Simple Text-Only Card

A simple recommendation card could store the treatment rule only as free text:

```text
Use Plan C for severe dehydration.
```

This representation is easy to create and easy to retrieve semantically.

However, the treatment condition exists only inside the text. A semantic retrieval system may still retrieve this card when the patient has some dehydration, no dehydration, or when dehydration severity has not been provided.

The card may therefore be semantically relevant while not being clinically applicable to the current patient.

## Representation B — Structured Applicability Rules

The implemented system represents important treatment conditions using explicit machine-readable applicability rules.

For example:

```json
{
  "card_id": "CHOLERA_MGMT_001",
  "disease": "Cholera",
  "clinical_category": "Management",
  "requires": {
    "dehydration_severity": "severe"
  },
  "recommended_action": "Apply Plan C treatment according to the protocol."
}
```

The system first performs semantic retrieval and then checks whether the patient satisfies the required prerequisite before allowing the recommendation.

Related treatment cards also contain their own applicability requirements and exclusions.

## Why the Structured Representation Was Chosen

The structured representation was selected because:

```text
semantic relevance ≠ patient-specific applicability
```

A treatment recommendation may be highly related to the disease while still being inappropriate for a particular patient state.

Explicit applicability rules make these conditions easier to:

- inspect;
- audit;
- test;
- preserve during retrieval; and
- apply consistently.

This approach also makes missing patient information visible instead of silently guessing it.

## Example Failure of the Simpler Representation

Consider a patient with acute watery diarrhoea but no documented dehydration severity.

A text-only semantic retriever may retrieve several Cholera management cards, including Plan A, Plan B, or Plan C, because all are semantically related to Cholera treatment.

However, the correct treatment pathway depends on dehydration severity.

The structured applicability-aware approach therefore:

- retains relevant Cholera diagnosis and assessment information;
- identifies dehydration severity as missing;
- blocks severity-dependent treatment recommendations until that information is available.

If the same patient is later documented as having severe dehydration, the system can then allow Plan C while keeping incompatible Plan A and Plan B pathways blocked.

This conditional recommendation was selected as the reasoning example because it demonstrates why explicit source-supported prerequisites are safer and more auditable than relying only on free-text semantic similarity.

---

# RAG Components

## Embedding Model

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model produces normalized 384-dimensional embeddings.

## Vector Index

FAISS is used for semantic retrieval.

Files:

```text
rag/embeddings.npy
rag/faiss.index
rag/metadata.json
```

---

# Baseline Mode

The baseline retrieves the top semantically similar canonical cards.

Workflow:

```text
Patient Input
     |
     v
Semantic Retrieval
     |
     v
Top-k Recommendation Cards
     |
     v
Structured Recommendation
```

The baseline does not perform explicit patient-specific applicability filtering.

Its purpose is to provide a reasonable semantic-retrieval reference system against which the tested improvement can be compared.

---

# Improved Mode

The tested improvement is:

## Applicability-Aware Clinical RAG

Workflow:

```text
Patient Input
     |
     v
Semantic Retrieval
     |
     v
Primary Disease Context
     |
     v
Prerequisite / Exclusion Checks
     |
     v
Missing-Information Handling
     |
     v
Structured Recommendation
```

The improvement is intended to separate:

```text
semantic relevance
```

from:

```text
clinical applicability
```

The same protocol corpus, canonical cards, embedding model, frozen evaluation cases, and general recommendation structure are retained across both modes.

---

# Example of the Tested Improvement

## Incomplete Cholera Case

Patient information includes acute watery diarrhoea but does not specify dehydration severity.

The improved system:

- retains relevant Cholera diagnosis and assessment evidence;
- does not select a severity-dependent treatment plan;
- identifies dehydration severity as missing information.

## Modified Cholera Case

The same case is modified with:

- weak pulse;
- sunken eyes;
- inability to drink; and
- severe dehydration.

The improved system then:

- recognizes severe dehydration;
- allows the severe-dehydration Plan C pathway;
- blocks incompatible Plan A and Plan B cards.

This demonstrates how a source-supported patient prerequisite changes the recommendation while the underlying disease context remains the same.

---

# Frozen Evaluation Cases

The project uses six fictional frozen cases:

```text
CASE_01_DENGUE
CASE_02_HYPERTENSION
CASE_03_CHOLERA
CASE_04_CHIKUNGUNYA
CASE_05_INCOMPLETE
CASE_06_MODIFIED
```

The same six inputs are used for both Baseline and Improved modes.

This produces:

```text
6 cases × 2 modes = 12 outputs
```

Case definitions are stored in:

```text
data/evaluation_cases.json
```

The expected-behaviour checklist for each case was frozen before the final comparison and was not inserted into the retrieval index or used as hidden case-specific answer logic.

---

# Evaluation Checks

Each output is evaluated using four predefined checks:

1. Did the key expected behaviour occur?
2. Were the recommendations supported by cited evidence?
3. Were relevant restrictions preserved?
4. Was missing information handled without guessing?

The purpose of these checks is to assess whether the tested applicability-aware change improves source-grounded system behaviour on the frozen fictional cases.

---

# Evaluation Results

## Baseline

```text
16 / 24 checks passed
66.67%
```

Average local response time:

```text
0.0469 seconds
```

## Applicability-Aware Mode

```text
24 / 24 checks passed
100.00%
```

Average local response time:

```text
0.0279 seconds
```

Observed difference:

```text
+33.33 percentage points
```

These values refer to predefined safety-and-behaviour checks on six self-authored fictional cases.

**They are not a clinical accuracy estimate and do not represent independent clinical validation.**

Detailed results are available in:

```text
results/final_results_table.csv
results/final_results_table.json
results/comparison_note.md
results/evaluation_outputs.json
results/evaluation_metrics.json
```

---

# Observed Baseline Failure Patterns

The baseline produced several types of errors during the frozen evaluation.

Examples included:

- incompatible Cholera treatment pathways being retrieved together;
- treatment recommendations appearing despite missing dehydration severity;
- cross-disease retrieval leakage in the Chikungunya case.

These failures are consistent with the limitation of using semantic similarity alone without explicit applicability filtering.

The improved system addressed these cases by checking prerequisites, exclusions, disease context, and missing patient information before accepting treatment cards.

---

# User Interface

The Streamlit application supports:

- editable patient details;
- symptoms and illness duration;
- age and sex;
- medical history;
- current medicines;
- allergies;
- additional clinical findings;
- vital signs;
- selectable measurement units;
- automatic unit normalization;
- Baseline / Improved mode switching;
- retrieved evidence display;
- probable diagnosis and differential diagnosis output;
- investigation recommendations;
- medication planning;
- patient advice;
- missing-information reporting;
- accepted and blocked recommendation details;
- professional clinical report;
- clinical slip;
- blank printable clinical form.

A disease name is not required as patient input.

---

# Run the Application

## 1. Open the project directory

```bat
cd /d "C:\Users\Asus\3D Objects\UIU"
```

## 2. Activate the virtual environment

```bat
venv\Scripts\activate
```

## 3. Start Streamlit

```bat
streamlit run src\app.py
```

The interface should open automatically in a browser.

If it does not open automatically:

```text
http://localhost:8501
```

---

# Install Dependencies

Using the provided requirements file:

```bat
pip install -r requirements.txt
```

---

# Rebuild Embeddings

Run:

```bat
python src\embeddings.py
```

Expected embedding shape:

```text
(17, 384)
```

The embeddings are stored in:

```text
rag/embeddings.npy
```

---

# Rebuild FAISS Index

Run:

```bat
python src\build_index.py
```

This creates or updates:

```text
rag/faiss.index
rag/metadata.json
```

---

# Run the Frozen Evaluation

Run:

```bat
python src\run_evaluation.py
```

This evaluates:

```text
6 frozen cases × 2 modes = 12 outputs
```

and saves:

```text
results/evaluation_outputs.json
```

---

# Generate Final Evaluation Report

Run:

```bat
python src\generate_final_evaluation_report.py
```

This generates:

```text
results/final_results_table.csv
results/final_results_table.json
results/comparison_note.md
```

---

# Project Structure

```text
UIU/
│
├── .streamlit/
│   └── config.toml
│
├── architecture/
│   ├── architecture_explanation.md
│   ├── clinical_rag_architecture.png
│   ├── clinical_rag_architecture.pdf
│   └── clinical_rag_architecture.svg
│
├── data/
│   ├── applicability_rules.json
│   ├── canonical_cards.jsonl
│   └── evaluation_cases.json
│
├── presentation/
│   ├── Clinical_Protocol_RAG_Interview_Deck.pptx
│   ├── Clinical_Protocol_RAG_Interview_Deck.pdf
│   ├── images/
│   └── paper_summary.md
│
├── protocols/
│   ├── chikungunya.pdf
│   ├── cholera.pdf
│   ├── dengue.pdf
│   └── hypertension.pdf
│
├── rag/
│   ├── embeddings.npy
│   ├── faiss.index
│   └── metadata.json
│
├── results/
│   ├── comparison_note.md
│   ├── evaluation_metrics.json
│   ├── evaluation_outputs.json
│   ├── final_results_table.csv
│   └── final_results_table.json
│
├── src/
│   ├── app.py
│   ├── applicability_retriever.py
│   ├── baseline_generator.py
│   ├── build_index.py
│   ├── clinical_generator.py
│   ├── compare_modes.py
│   ├── embeddings.py
│   ├── evaluation_metrics.py
│   ├── generate_final_evaluation_report.py
│   ├── retriever.py
│   └── run_evaluation.py
│
├── AI_TOOL_DISCLOSURE.md
├── README.md
└── requirements.txt
```

---

# System Architecture

The full architecture is provided in:

```text
architecture/clinical_rag_architecture.png
architecture/clinical_rag_architecture.pdf
architecture/clinical_rag_architecture.svg
```

The implemented pipeline includes:

```text
Protocol PDFs
    ↓
Protocol Extraction
    ↓
Canonical Cards
    ↓
Embeddings
    ↓
FAISS Index
    ↓
Patient Input
    ↓
Semantic Retrieval
    ↓
Primary Disease Context
    ↓
Applicability Check
    ↓
Missing-Information Check
    ↓
Recommendation Assembly
    ↓
Streamlit Interface
```

Future architecture connections include:

- NER-based information extraction;
- doctor acceptance / rejection / modification;
- broader protocol coverage; and
- clinician-approved prescription assembly.

The architectural explanation is documented in:

```text
architecture/architecture_explanation.md
```

---

# Research Paper Discussion

The assessment-related paper summary is stored in:

```text
presentation/paper_summary.md
```

Paper:

**Saab et al. — Advancing conversational diagnostic AI with multimodal reasoning, Nature Medicine, 2026**

DOI:

```text
10.1038/s41591-026-04371-0
```

The presentation deck is stored in:

```text
presentation/Clinical_Protocol_RAG_Interview_Deck.pptx
```

A PDF copy is also included for convenience.

---

# Main Design Decision

The central design decision in this prototype is to keep semantic retrieval and patient-specific applicability as separate stages.

The simpler alternative would be to accept the highest-scoring semantic cards directly.

That alternative is computationally simple, but it cannot reliably enforce source-defined prerequisites or exclusions.

The selected design adds a lightweight rule-based applicability layer after retrieval.

This choice provides:

- clearer traceability;
- explicit missing-information handling;
- easier debugging;
- better preservation of treatment conditions; and
- a direct way to test whether a newly supplied patient detail should change the recommendation.

---

# Latency and Cost Trade-off

The improved mode introduces additional processing for:

- primary disease-context selection;
- prerequisite checks;
- exclusion checks; and
- missing-information detection.

This adds logical complexity compared with simple semantic retrieval.

However, in the local frozen evaluation, the measured average runtime remained small:

```text
Baseline: 0.0469 seconds
Improved: 0.0279 seconds
```

These timings are local prototype measurements only and should not be interpreted as production latency benchmarks.

The applicability layer does not require an additional trained model and therefore avoids extra model-training cost.

---

# Limitations

The current prototype has several important limitations:

- only four clinical protocols are included;
- the knowledge base currently contains 17 recommendation cards;
- evaluation uses only six self-authored fictional cases;
- no real patient data were used;
- no independent clinician validation was performed;
- applicability rules cover only the conditions represented in the current demonstration;
- the primary disease context is determined using retrieval behaviour rather than a separately validated diagnostic model;
- local response-time measurements are not production benchmarks;
- the system is not integrated with a hospital information system;
- NER and doctor-feedback components are future architecture elements;
- the current experiment does not establish clinical effectiveness.

---

# Future Work

Possible future extensions include:

- automated NER extraction from clinical notes;
- larger protocol coverage;
- broader applicability-rule coverage;
- blinded evaluation by clinicians;
- real-world workflow testing;
- doctor accept/reject/modify feedback;
- multilingual clinical input;
- improved differential-diagnosis handling;
- clinician-approved prescription assembly.

---

# AI and Tool Disclosure

A separate disclosure is provided in:

```text
AI_TOOL_DISCLOSURE.md
```

AI tools were used for:

- development assistance;
- debugging;
- documentation;
- architecture explanation;
- evaluation organization; and
- presentation preparation.

AI assistance was not treated as an independent clinical validator.

The clinical protocols, source references, evaluation cases, system behaviour, and final reported results remain explicitly represented in the project artifacts.

---

# Safety and Interpretation

This prototype was created for an assessment and research demonstration.

Its outputs are protocol-grounded recommendations for fictional or manually entered cases.

The evaluation results describe predefined checks on a small set of self-authored fictional examples.

They should not be interpreted as:

- clinical accuracy;
- diagnostic accuracy;
- treatment efficacy;
- external validation; or
- approval for autonomous clinical use.

---

# Final Contribution

The main contribution of this prototype is a small and auditable clinical RAG workflow that separates semantic relevance from patient-specific applicability before producing recommendations.

The strongest demonstrated behaviour is its ability to:

- preserve relevant protocol evidence;
- identify when a required patient detail is missing;
- withhold a condition-dependent treatment when its prerequisite is unavailable; and
- activate the appropriate treatment pathway when the required patient information becomes available.

This behaviour is demonstrated most clearly by the incomplete and modified Cholera evaluation cases.