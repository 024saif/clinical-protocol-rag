# Architecture Explanation

The prototype is organized as a protocol-grounded clinical recommendation pipeline. Four supplied clinical protocols are first reviewed at the assigned PDF pages and converted into canonical JSON/JSONL recommendation cards. Each card preserves disease context, clinical category, prerequisites, recommended action, exclusions or missing information, medication details where supported, and source-page evidence. These cards are embedded using `all-MiniLM-L6-v2` and indexed with FAISS for semantic retrieval.

For a new patient case, editable information such as symptoms, duration, age, sex, medical history, current medicines, allergies, clinical findings and available vital signs is combined into the patient context. The baseline mode retrieves the top semantically similar cards directly. This approach is simple, but semantic similarity alone can retrieve a treatment card even when its clinical prerequisite is not satisfied.

The tested improvement is an **Applicability-Aware Clinical RAG** stage. After semantic retrieval, the system identifies the primary disease context and checks source-derived prerequisites, exclusions and required patient information. Cards that are incompatible with known patient facts are blocked. If necessary information is missing, the system does not guess; it retains recommendations that are still supported and reports the missing information explicitly.

A source-supported change in patient information can therefore alter the recommendation. For example, an incomplete cholera case without dehydration severity does not receive a severity-dependent rehydration plan. When the same case is modified to include severe-dehydration findings such as weak pulse, sunken eyes and inability to drink, the severe-dehydration pathway becomes applicable while incompatible alternatives remain blocked.

The final recommendation assembly presents probable diagnosis, investigations, medication planning, advice, missing information and evidence references through the Streamlit interface. Source IDs and PDF-page evidence are retained for traceability.

Future integration points include NER-based extraction of patient information, clinician acceptance or modification of recommendations, and clinician-approved prescription assembly. These are shown as future components rather than implemented prototype functions.

The main architectural trade-off is that applicability checking introduces additional rule evaluation after semantic retrieval. However, in the six frozen evaluation cases, the measured average response time remained small: 0.0469 seconds for the baseline and 0.0279 seconds for the improved mode. These timings are local prototype measurements and should not be interpreted as production latency benchmarks.