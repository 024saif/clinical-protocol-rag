import html
import json
import os
import re
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from baseline_generator import generate_baseline_response
from clinical_generator import generate_clinical_response


# =========================================================
# CONFIG
# =========================================================

METRICS_PATH = "results/evaluation_metrics.json"

st.set_page_config(
    page_title="Clinical Protocol RAG",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# THEME
# =========================================================

st.markdown(
    """
<style>

html,
body,
[data-testid="stAppViewContainer"],
.stApp {
    background-color: #23433F !important;
    color: #D9F0EC !important;
}

[data-testid="stHeader"] {
    background-color: #23433F !important;
}

.block-container {
    max-width: 1380px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background-color: #193632 !important;
    border-right: 1px solid #315D57 !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #193632 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #D9F0EC !important;
}

h1,
h2,
h3 {
    color: #D9F0EC !important;
}

label {
    color: #D9F0EC !important;
    font-weight: 600 !important;
}

div[data-testid="stTextInput"] input {
    background: #55A9A0 !important;
    color: #102C28 !important;
    border: 1px solid #79C8BF !important;
    border-radius: 11px !important;
}

div[data-testid="stTextArea"] textarea {
    background: #55A9A0 !important;
    color: #102C28 !important;
    border: 1px solid #79C8BF !important;
    border-radius: 11px !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    background: #55A9A0 !important;
    border: 2px solid #8FE3D8 !important;
    box-shadow: none !important;
}

input::placeholder,
textarea::placeholder {
    color: #315B56 !important;
    opacity: 1 !important;
}

div[data-testid="stSelectbox"]
div[data-baseweb="select"] > div,
div[data-testid="stSelectbox"]
div[data-baseweb="select"] > div > div,
div[data-testid="stSelectbox"]
[role="combobox"] {
    background: #55A9A0 !important;
    color: #102C28 !important;
}

div[data-testid="stSelectbox"]
div[data-baseweb="select"] > div {
    border: 1px solid #79C8BF !important;
    border-radius: 11px !important;
    overflow: hidden !important;
}

div[data-testid="stSelectbox"] span {
    color: #102C28 !important;
}

div[data-testid="stSelectbox"] svg {
    color: #102C28 !important;
    fill: #102C28 !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] [role="option"] {
    background-color: #55A9A0 !important;
    color: #102C28 !important;
}

div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] [role="option"]:hover {
    background-color: #72C1B8 !important;
}

.main-header {
    background-color: #55A9A0;
    border: 1px solid #79C8BF;
    border-radius: 15px;
    padding: 24px 28px;
    margin-bottom: 30px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.12);
}

.main-header-title {
    color: #102C28 !important;
    font-size: 2.15rem;
    font-weight: 750;
}

.clinical-card {
    background-color: #55A9A0;
    border: 1px solid #79C8BF;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 18px;
    box-shadow: 0 5px 16px rgba(0,0,0,0.12);
}

.clinical-title {
    color: #102C28;
    font-size: 1.07rem;
    font-weight: 750;
    margin-bottom: 12px;
}

.clinical-content {
    color: #153B36;
    font-size: 0.97rem;
    line-height: 1.65;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    min-height: 50px;
    background-color: #102C28 !important;
    color: #D9F0EC !important;
    border: 1px solid #315D57 !important;
    border-radius: 12px !important;
    font-weight: 750;
    font-size: 1rem;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #193F3A !important;
    color: #FFFFFF !important;
    border: 1px solid #55A9A0 !important;
}

button[data-baseweb="tab"] {
    color: #CFE4E0 !important;
    font-weight: 650 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
}

div[data-testid="stExpander"] {
    background-color: #244B46 !important;
    border: 1px solid #315D57 !important;
    border-radius: 12px !important;
}

div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] span {
    color: #D9F0EC !important;
}

hr {
    border-color: #315D57 !important;
}

::-webkit-scrollbar {
    width: 9px;
}

::-webkit-scrollbar-track {
    background: #193632;
}

::-webkit-scrollbar-thumb {
    background: #55A9A0;
    border-radius: 10px;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# DEMO CASES
# =========================================================

demo_cases = {
    "Custom": {
        "age": "",
        "sex": "Not specified",
        "duration": "",
        "symptoms": "",
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": ""
    },

    "Dengue": {
        "age": "24",
        "sex": "Not specified",
        "duration": "3 days",
        "symptoms": (
            "High fever, severe headache, pain behind the eyes, "
            "body ache and rash"
        ),
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": "No vomiting, bleeding or altered consciousness"
    },

    "Hypertension": {
        "age": "55",
        "sex": "Not specified",
        "duration": "Several visits",
        "symptoms": (
            "Repeated blood pressure readings around 150/95 mmHg"
        ),
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": "No acute emergency symptoms"
    },

    "Severe Cholera": {
        "age": "40",
        "sex": "Not specified",
        "duration": "Started today",
        "symptoms": "Acute watery diarrhoea",
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": (
            "Very weak pulse, sunken eyes, unable to drink properly, "
            "severe dehydration"
        )
    },

    "Chikungunya": {
        "age": "32",
        "sex": "Not specified",
        "duration": "3 days",
        "symptoms": (
            "Sudden high fever, severe pain in multiple joints, "
            "headache and skin rash"
        ),
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": ""
    },

    "Incomplete Cholera": {
        "age": "35",
        "sex": "Not specified",
        "duration": "Started today",
        "symptoms": "Acute watery diarrhoea with several loose stools",
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": ""
    },

    "Modified Cholera": {
        "age": "35",
        "sex": "Not specified",
        "duration": "Started today",
        "symptoms": "Acute watery diarrhoea with frequent loose stools",
        "history": "",
        "medicines": "",
        "allergies": "",
        "findings": (
            "Weak pulse, sunken eyes, unable to drink properly, "
            "severe dehydration"
        )
    }
}


# =========================================================
# SESSION STATE
# =========================================================

def clear_analysis():
    st.session_state.pop("analysis_payload", None)


def load_demo_case():

    selected = demo_cases[
        st.session_state.demo_case
    ]

    st.session_state.patient_age = selected["age"]
    st.session_state.patient_sex = selected["sex"]
    st.session_state.patient_duration = selected["duration"]
    st.session_state.patient_symptoms = selected["symptoms"]
    st.session_state.patient_history = selected["history"]
    st.session_state.patient_medicines = selected["medicines"]
    st.session_state.patient_allergies = selected["allergies"]
    st.session_state.patient_findings = selected["findings"]

    clear_analysis()


if "demo_case" not in st.session_state:
    st.session_state.demo_case = "Custom"

if "system_mode" not in st.session_state:
    st.session_state.system_mode = "Applicability-Aware RAG"


initial_case = demo_cases[st.session_state.demo_case]


defaults = {
    "patient_name": "",
    "patient_id": "",
    "patient_contact": "",
    "patient_address": "",

    "patient_age": initial_case["age"],
    "patient_sex": initial_case["sex"],
    "patient_duration": initial_case["duration"],

    "patient_symptoms": initial_case["symptoms"],
    "patient_history": initial_case["history"],
    "patient_medicines": initial_case["medicines"],
    "patient_allergies": initial_case["allergies"],
    "patient_findings": initial_case["findings"],

    "vital_bp": "",
    "vital_bp_unit": "mmHg",

    "vital_pulse": "",
    "vital_pulse_unit": "bpm",

    "vital_temperature": "",
    "vital_temperature_unit": "°F",

    "vital_spo2": "",
    "vital_spo2_unit": "%",

    "vital_weight": "",
    "vital_weight_unit": "kg",

    "vital_height": "",
    "vital_height_unit": "cm",

    "follow_up": ""
}


for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# GENERAL HELPERS
# =========================================================

def load_evaluation_metrics():

    if not os.path.exists(METRICS_PATH):
        return None

    try:
        with open(
            METRICS_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except Exception:
        return None


def split_response_sections(text):

    headings = [
        "Probable Diagnosis:",
        "Investigations:",
        "Medication Planning:",
        "Advice:",
        "Missing Information:",
        "Evidence:"
    ]

    sections = {}
    current_heading = None
    current_lines = []

    for line in text.splitlines():

        stripped = line.strip()

        if stripped in headings:

            if current_heading is not None:
                sections[current_heading] = (
                    "\n".join(current_lines).strip()
                )

            current_heading = stripped
            current_lines = []

        elif current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = (
            "\n".join(current_lines).strip()
        )

    return sections


def clean_for_html(text):

    if not text:
        return ""

    safe_text = (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    lines = []

    for line in safe_text.splitlines():

        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("-"):
            lines.append(
                "• " + stripped[1:].strip()
            )
        else:
            lines.append(stripped)

    return "<br><br>".join(lines)


def display_card(title, content, icon):

    safe_content = clean_for_html(content)

    if not safe_content:
        safe_content = "No applicable information available."

    st.markdown(
        (
            '<div class="clinical-card">'
            f'<div class="clinical-title">{icon} {title}</div>'
            f'<div class="clinical-content">{safe_content}</div>'
            '</div>'
        ),
        unsafe_allow_html=True
    )


# =========================================================
# UNIT CONVERSION
# =========================================================

def extract_number(value):

    if value is None:
        return None

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        str(value)
    )

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def clean_number(number):

    if number is None:
        return ""

    if abs(number - round(number)) < 0.000001:
        return str(int(round(number)))

    return (
        f"{number:.2f}"
        .rstrip("0")
        .rstrip(".")
    )


def normalize_temperature(value, unit):

    number = extract_number(value)

    if number is None:
        return ""

    if unit == "°F":
        number = (number - 32) * 5 / 9

    return clean_number(number) + " °C"


def normalize_weight(value, unit):

    number = extract_number(value)

    if number is None:
        return ""

    if unit == "lb":
        number = number * 0.45359237

    return clean_number(number) + " kg"


def normalize_height(value, unit):

    number = extract_number(value)

    if number is None:
        return ""

    if unit == "m":
        number = number * 100

    elif unit == "inch":
        number = number * 2.54

    return clean_number(number) + " cm"


def normalize_pulse(value, unit):

    number = extract_number(value)

    if number is None:
        return ""

    if unit == "beats/sec":
        number = number * 60

    return clean_number(number) + " bpm"


def normalize_bp(value, unit):

    if not value:
        return ""

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        str(value)
    )

    if not numbers:
        return ""

    if unit == "kPa":

        converted = [
            clean_number(float(item) * 7.50062)
            for item in numbers[:2]
        ]

        return "/".join(converted) + " mmHg"

    if len(numbers) >= 2:
        return (
            numbers[0]
            + "/"
            + numbers[1]
            + " mmHg"
        )

    return numbers[0] + " mmHg"


def normalize_spo2(value):

    number = extract_number(value)

    if number is None:
        return ""

    return clean_number(number) + "%"


def display_measurement(value, unit):

    if not str(value).strip():
        return ""

    return (
        str(value).strip()
        + " "
        + unit
    )


# =========================================================
# PATIENT TEXT
# =========================================================

def build_patient_text(patient):

    parts = []

    if patient["age"]:
        parts.append(
            f"{patient['age']}-year-old patient"
        )

    if patient["sex"] != "Not specified":
        parts.append(
            f"Sex: {patient['sex']}"
        )

    if patient["symptoms"]:
        parts.append(
            f"Symptoms: {patient['symptoms']}"
        )

    if patient["duration"]:
        parts.append(
            f"Duration: {patient['duration']}"
        )

    if patient["history"]:
        parts.append(
            f"Relevant history: {patient['history']}"
        )

    if patient["medicines"]:
        parts.append(
            f"Current medicines: {patient['medicines']}"
        )

    if patient["allergies"]:
        parts.append(
            f"Allergies: {patient['allergies']}"
        )

    if patient["findings"]:
        parts.append(
            f"Clinical findings: {patient['findings']}"
        )

    vital_parts = []

    if patient["normalized_bp"]:
        vital_parts.append(
            "Blood pressure "
            + patient["normalized_bp"]
        )

    if patient["normalized_pulse"]:
        vital_parts.append(
            "Pulse "
            + patient["normalized_pulse"]
        )

    if patient["normalized_temperature"]:
        vital_parts.append(
            "Temperature "
            + patient["normalized_temperature"]
        )

    if patient["normalized_spo2"]:
        vital_parts.append(
            "SpO2 "
            + patient["normalized_spo2"]
        )

    if patient["normalized_weight"]:
        vital_parts.append(
            "Weight "
            + patient["normalized_weight"]
        )

    if patient["normalized_height"]:
        vital_parts.append(
            "Height "
            + patient["normalized_height"]
        )

    if vital_parts:
        parts.append(
            "Vitals: "
            + ", ".join(vital_parts)
        )

    return ". ".join(parts) + "."


# =========================================================
# PRINT HELPERS
# =========================================================

def safe(value, fallback="—"):

    if value is None:
        return fallback

    value = str(value).strip()

    if not value:
        return fallback

    return html.escape(value)


def formatted_section(value):

    if not value:
        return "—"

    escaped = html.escape(str(value))

    rows = []

    for line in escaped.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("-"):
            rows.append(
                "<div class='bullet'>"
                "• "
                + line[1:].strip()
                + "</div>"
            )
        else:
            rows.append(
                "<div>"
                + line
                + "</div>"
            )

    return "".join(rows)


def document_css():

    return """
<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #e8eceb;
    font-family: Arial, Helvetica, sans-serif;
    color: #202020;
}

.toolbar {
    max-width: 210mm;
    margin: 12px auto;
    display: flex;
    justify-content: flex-end;
}

.print-button {
    background: #173b36;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 16px;
    cursor: pointer;
    font-weight: 700;
}

.document {
    width: 210mm;
    min-height: 297mm;
    margin: 0 auto 20px auto;
    background: white;
    padding: 15mm;
    box-shadow: 0 2px 14px rgba(0,0,0,.12);
}

.hospital-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #55A9A0;
    padding-bottom: 12px;
    margin-bottom: 16px;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    color: #173b36;
}

.brand-sub {
    font-size: 11px;
    color: #666;
}

.report-type {
    text-align: right;
}

.report-type strong {
    display: block;
    color: #173b36;
}

.report-type span {
    font-size: 10px;
    color: #666;
}

.section-title {
    background: #e5f1ef;
    color: #173b36;
    font-weight: 800;
    font-size: 12px;
    padding: 7px 9px;
    margin-top: 14px;
    margin-bottom: 7px;
    border-left: 4px solid #55A9A0;
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-top: 1px solid #aaa;
    border-left: 1px solid #aaa;
}

.field {
    padding: 7px;
    min-height: 45px;
    border-right: 1px solid #aaa;
    border-bottom: 1px solid #aaa;
}

.field.wide {
    grid-column: span 2;
}

.label {
    font-size: 8.5px;
    color: #666;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.value {
    font-size: 11px;
    font-weight: 600;
}

.content-box {
    border: 1px solid #aaa;
    padding: 9px;
    min-height: 55px;
    font-size: 10.5px;
    line-height: 1.5;
}

.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.signature-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 25px;
    margin-top: 35px;
}

.signature {
    border-top: 1px solid #555;
    text-align: center;
    padding-top: 5px;
    font-size: 9px;
}

.footer {
    margin-top: 18px;
    border-top: 1px solid #bbb;
    padding-top: 7px;
    color: #666;
    font-size: 8px;
}

@page {
    size: A4;
    margin: 8mm;
}

@media print {

    body {
        background: white;
    }

    .toolbar {
        display: none;
    }

    .document {
        width: 100%;
        margin: 0;
        box-shadow: none;
        min-height: auto;
    }
}

</style>
"""


# =========================================================
# PROFESSIONAL REPORT
# =========================================================

def build_professional_report(
    patient,
    sections,
    primary,
    differentials,
    report_id,
    generated_on
):

    differential_text = (
        ", ".join(differentials)
        if differentials
        else "—"
    )

    return f"""
<!DOCTYPE html>
<html>

<head>
{document_css()}
</head>

<body>

<div class="toolbar">
<button
class="print-button"
onclick="window.print()"
>
Print / Save as PDF
</button>
</div>

<div class="document">

<div class="hospital-header">

<div>
<div class="brand">
Clinical Protocol RAG
</div>

<div class="brand-sub">
Clinical Assessment Report
</div>
</div>

<div class="report-type">
<strong>Clinical Assessment</strong>
<span>Report ID: {safe(report_id)}</span>
<br>
<span>{safe(generated_on)}</span>
</div>

</div>


<div class="section-title">
Patient Information
</div>

<div class="grid">

<div class="field wide">
<div class="label">Patient Name</div>
<div class="value">{safe(patient["name"])}</div>
</div>

<div class="field">
<div class="label">Patient ID</div>
<div class="value">{safe(patient["id"])}</div>
</div>

<div class="field">
<div class="label">Date</div>
<div class="value">{safe(generated_on)}</div>
</div>

<div class="field">
<div class="label">Age</div>
<div class="value">{safe(patient["age"])}</div>
</div>

<div class="field">
<div class="label">Sex</div>
<div class="value">{safe(patient["sex"])}</div>
</div>

<div class="field">
<div class="label">Contact</div>
<div class="value">{safe(patient["contact"])}</div>
</div>

<div class="field">
<div class="label">Duration</div>
<div class="value">{safe(patient["duration"])}</div>
</div>

<div class="field wide">
<div class="label">Address</div>
<div class="value">{safe(patient["address"])}</div>
</div>

<div class="field wide">
<div class="label">Allergies</div>
<div class="value">{safe(patient["allergies"])}</div>
</div>

</div>


<div class="section-title">
Vital Signs
</div>

<div class="grid">

<div class="field">
<div class="label">Blood Pressure</div>
<div class="value">{safe(patient["display_bp"])}</div>
</div>

<div class="field">
<div class="label">Pulse</div>
<div class="value">{safe(patient["display_pulse"])}</div>
</div>

<div class="field">
<div class="label">Temperature</div>
<div class="value">{safe(patient["display_temperature"])}</div>
</div>

<div class="field">
<div class="label">SpO₂</div>
<div class="value">{safe(patient["display_spo2"])}</div>
</div>

<div class="field">
<div class="label">Weight</div>
<div class="value">{safe(patient["display_weight"])}</div>
</div>

<div class="field">
<div class="label">Height</div>
<div class="value">{safe(patient["display_height"])}</div>
</div>

</div>


<div class="section-title">
Clinical Presentation
</div>

<div class="two-column">

<div>
<div class="label">Chief Complaints</div>
<div class="content-box">
{safe(patient["symptoms"])}
</div>
</div>

<div>
<div class="label">Additional Findings</div>
<div class="content-box">
{safe(patient["findings"])}
</div>
</div>

</div>


<div class="section-title">
Assessment
</div>

<div class="grid">

<div class="field wide">
<div class="label">Primary Context</div>
<div class="value">{safe(primary)}</div>
</div>

<div class="field wide">
<div class="label">Differential</div>
<div class="value">{safe(differential_text)}</div>
</div>

</div>


<div class="section-title">
Probable Diagnosis
</div>

<div class="content-box">
{formatted_section(
    sections.get(
        "Probable Diagnosis:",
        ""
    )
)}
</div>


<div class="section-title">
Investigations
</div>

<div class="content-box">
{formatted_section(
    sections.get(
        "Investigations:",
        ""
    )
)}
</div>


<div class="section-title">
Medication Planning
</div>

<div class="content-box">
{formatted_section(
    sections.get(
        "Medication Planning:",
        ""
    )
)}
</div>


<div class="section-title">
Advice
</div>

<div class="content-box">
{formatted_section(
    sections.get(
        "Advice:",
        ""
    )
)}
</div>


<div class="section-title">
Evidence
</div>

<div class="content-box">
{formatted_section(
    sections.get(
        "Evidence:",
        ""
    )
)}
</div>


<div class="signature-row">

<div class="signature">
Prepared / Reviewed By
</div>

<div class="signature">
Clinician Signature
</div>

<div class="signature">
Seal / Date
</div>

</div>


<div class="footer">
Protocol-grounded clinical assessment generated
for clinician review.
</div>

</div>

</body>
</html>
"""


# =========================================================
# CLINICAL SLIP
# =========================================================

def build_clinical_slip(
    patient,
    sections,
    primary,
    report_id,
    generated_on
):

    return f"""
<!DOCTYPE html>
<html>

<head>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #e8eceb;
    font-family: Arial, Helvetica, sans-serif;
}}

.toolbar {{
    max-width: 148mm;
    margin: 10px auto;
    text-align: right;
}}

.button {{
    background: #173b36;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 9px 14px;
    font-weight: 700;
}}

.slip {{
    width: 148mm;
    min-height: 210mm;
    background: white;
    margin: auto;
    padding: 11mm;
    color: #222;
}}

.header {{
    border-bottom: 3px solid #55A9A0;
    padding-bottom: 8px;
}}

.brand {{
    color: #173b36;
    font-size: 22px;
    font-weight: 800;
}}

.small {{
    color: #666;
    font-size: 9px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
}}

td {{
    border: 1px solid #aaa;
    padding: 6px;
    font-size: 10px;
}}

.section {{
    margin-top: 12px;
}}

.title {{
    border-bottom: 1px solid #777;
    font-size: 10px;
    font-weight: 800;
    color: #173b36;
    padding-bottom: 3px;
}}

.content {{
    padding-top: 5px;
    font-size: 10.5px;
    line-height: 1.5;
}}

.rx {{
    font-family: Georgia, serif;
    font-size: 25px;
    font-weight: 700;
    margin-top: 12px;
}}

.rx-box {{
    border: 1px solid #aaa;
    padding: 8px;
    min-height: 80px;
    font-size: 10.5px;
    line-height: 1.5;
}}

.signature {{
    width: 180px;
    border-top: 1px solid #555;
    margin-left: auto;
    margin-top: 35px;
    padding-top: 4px;
    text-align: center;
    font-size: 9px;
}}

@page {{
    size: A5;
    margin: 6mm;
}}

@media print {{

    body {{
        background: white;
    }}

    .toolbar {{
        display: none;
    }}

    .slip {{
        width: 100%;
        margin: 0;
    }}
}}

</style>

</head>

<body>

<div class="toolbar">
<button
class="button"
onclick="window.print()"
>
Print / Save as PDF
</button>
</div>


<div class="slip">

<div class="header">

<div class="brand">
Clinical Protocol RAG
</div>

<div class="small">
Clinical Assessment Slip
</div>

</div>


<table>

<tr>
<td>
<b>Patient:</b>
{safe(patient["name"])}
</td>

<td>
<b>ID:</b>
{safe(patient["id"])}
</td>
</tr>

<tr>
<td>
<b>Age / Sex:</b>
{safe(patient["age"])}
/
{safe(patient["sex"])}
</td>

<td>
<b>Date:</b>
{safe(generated_on)}
</td>
</tr>

<tr>
<td>
<b>BP:</b>
{safe(patient["display_bp"])}
</td>

<td>
<b>Pulse:</b>
{safe(patient["display_pulse"])}
</td>
</tr>

<tr>
<td>
<b>Temperature:</b>
{safe(patient["display_temperature"])}
</td>

<td>
<b>SpO₂:</b>
{safe(patient["display_spo2"])}
</td>
</tr>

</table>


<div class="section">

<div class="title">
Chief Complaints
</div>

<div class="content">
{safe(patient["symptoms"])}
</div>

</div>


<div class="section">

<div class="title">
Clinical Findings
</div>

<div class="content">
{safe(patient["findings"])}
</div>

</div>


<div class="section">

<div class="title">
Probable Diagnosis
</div>

<div class="content">
{formatted_section(
    sections.get(
        "Probable Diagnosis:",
        ""
    )
)}
</div>

</div>


<div class="rx">
Rx
</div>

<div class="rx-box">
{formatted_section(
    sections.get(
        "Medication Planning:",
        ""
    )
)}
</div>


<div class="section">

<div class="title">
Investigations
</div>

<div class="content">
{formatted_section(
    sections.get(
        "Investigations:",
        ""
    )
)}
</div>

</div>


<div class="section">

<div class="title">
Advice
</div>

<div class="content">
{formatted_section(
    sections.get(
        "Advice:",
        ""
    )
)}
</div>

</div>


<div class="section">

<div class="title">
Follow Up
</div>

<div class="content">
{safe(patient["follow_up"])}
</div>

</div>


<div class="signature">
Clinician Signature / Seal
</div>


<div class="small">
Report ID:
{safe(report_id)}
<br>
Primary context:
{safe(primary)}
</div>

</div>

</body>
</html>
"""


# =========================================================
# BLANK FORM
# =========================================================

def build_blank_form():

    return f"""
<!DOCTYPE html>
<html>

<head>

{document_css()}

<style>

.blank {{
    min-height: 60px;
}}

.big {{
    min-height: 100px;
}}

.medicine-table {{
    width: 100%;
    border-collapse: collapse;
}}

.medicine-table th,
.medicine-table td {{
    border: 1px solid #888;
    padding: 5px;
    height: 34px;
    font-size: 10px;
}}

.medicine-table th {{
    background: #e5f1ef;
}}

</style>

</head>

<body>

<div class="toolbar">

<button
class="print-button"
onclick="window.print()"
>
Print Blank Form
</button>

</div>


<div class="document">

<div class="hospital-header">

<div>

<div class="brand">
Clinical Protocol RAG
</div>

<div class="brand-sub">
Clinical Assessment Form
</div>

</div>

<div class="report-type">

<strong>
Patient Assessment
</strong>

<span>
Date: ____________________
</span>

</div>

</div>


<div class="section-title">
Patient Information
</div>

<div class="grid">

<div class="field wide">
<div class="label">Patient Name</div>
</div>

<div class="field">
<div class="label">Patient ID</div>
</div>

<div class="field">
<div class="label">Date / Time</div>
</div>

<div class="field">
<div class="label">Age</div>
</div>

<div class="field">
<div class="label">Sex</div>
</div>

<div class="field">
<div class="label">Contact</div>
</div>

<div class="field">
<div class="label">Duration</div>
</div>

<div class="field wide">
<div class="label">Address</div>
</div>

<div class="field wide">
<div class="label">Allergies</div>
</div>

</div>


<div class="section-title">
Vital Signs
</div>

<div class="grid">

<div class="field">
<div class="label">
BP ________ mmHg / kPa
</div>
</div>

<div class="field">
<div class="label">
Pulse ______ bpm
</div>
</div>

<div class="field">
<div class="label">
Temperature ______ °C / °F
</div>
</div>

<div class="field">
<div class="label">
SpO₂ ______ %
</div>
</div>

<div class="field">
<div class="label">
Weight ______ kg / lb
</div>
</div>

<div class="field">
<div class="label">
Height ______ cm / m / inch
</div>
</div>

</div>


<div class="section-title">
Chief Complaints
</div>

<div class="content-box big"></div>


<div class="section-title">
Relevant History
</div>

<div class="content-box big"></div>


<div class="section-title">
Clinical Findings
</div>

<div class="content-box big"></div>


<div class="section-title">
Probable Diagnosis
</div>

<div class="content-box blank"></div>


<div class="section-title">
Investigations
</div>

<div class="content-box blank"></div>


<div class="section-title">
Medication / Treatment
</div>

<table class="medicine-table">

<tr>
<th>Medicine</th>
<th>Dose</th>
<th>Route</th>
<th>Frequency</th>
<th>Duration</th>
</tr>

<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>

<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>

<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>

<tr>
<td></td>
<td></td>
<td></td>
<td></td>
<td></td>
</tr>

</table>


<div class="section-title">
Advice
</div>

<div class="content-box blank"></div>


<div class="section-title">
Follow Up
</div>

<div class="content-box"></div>


<div class="signature-row">

<div class="signature">
Clinician Name
</div>

<div class="signature">
Signature
</div>

<div class="signature">
Seal / Date
</div>

</div>

</div>

</body>
</html>
"""


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🩺 Clinical RAG"
    )

    st.divider()

    st.markdown(
        "### System Mode"
    )

    st.radio(
        "Mode",
        [
            "Applicability-Aware RAG",
            "Baseline RAG"
        ],
        key="system_mode",
        label_visibility="collapsed",
        on_change=clear_analysis
    )

    st.divider()

    st.markdown(
        "### Demo Case"
    )

    st.selectbox(
        "Case",
        list(demo_cases.keys()),
        key="demo_case",
        label_visibility="collapsed",
        on_change=load_demo_case
    )

    st.divider()

    with st.expander(
        "Evaluation",
        expanded=False
    ):

        metrics = load_evaluation_metrics()

        if metrics:

            summary = metrics.get(
                "summary",
                {}
            )

            cases = summary.get(
                "number_of_cases",
                0
            )

            baseline = summary.get(
                "baseline_percentage",
                0
            )

            improved = summary.get(
                "improved_percentage",
                0
            )

            difference = summary.get(
                "absolute_improvement_percentage_points",
                0
            )

            st.markdown(
                f"""
**Cases:** {cases}  
**Baseline:** {baseline:.2f}%  
**Improved:** {improved:.2f}%  
**Difference:** +{difference:.2f} pp
                """
            )

        else:

            st.write(
                "Evaluation results unavailable."
            )

    st.divider()

    with st.expander(
        "Protocols",
        expanded=False
    ):

        st.write("Dengue")
        st.write("Hypertension")
        st.write("Cholera")
        st.write("Chikungunya")


# =========================================================
# HEADER
# =========================================================

st.markdown(
    (
        '<div class="main-header">'
        '<div class="main-header-title">'
        'Clinical Protocol RAG'
        '</div>'
        '</div>'
    ),
    unsafe_allow_html=True
)


# =========================================================
# PATIENT FORM
# =========================================================

with st.form(
    "patient_assessment_form",
    clear_on_submit=False
):

    # -----------------------------------------------------
    # PATIENT INFORMATION
    # -----------------------------------------------------

    st.markdown(
        "## Patient Information"
    )

    p1, p2, p3 = st.columns(
        [2, 1, 1]
    )

    with p1:

        st.text_input(
            "Patient Name",
            key="patient_name"
        )

    with p2:

        st.text_input(
            "Patient ID",
            key="patient_id"
        )

    with p3:

        st.text_input(
            "Contact",
            key="patient_contact"
        )


    st.text_input(
        "Address",
        key="patient_address"
    )


    p4, p5, p6 = st.columns(
        [1, 1, 2]
    )

    with p4:

        st.text_input(
            "Age",
            key="patient_age"
        )

    with p5:

        st.selectbox(
            "Sex",
            [
                "Not specified",
                "Male",
                "Female",
                "Other"
            ],
            key="patient_sex"
        )

    with p6:

        st.text_input(
            "Duration",
            key="patient_duration"
        )


    # -----------------------------------------------------
    # PRESENTING COMPLAINT
    # -----------------------------------------------------

    st.markdown(
        "## Presenting Complaint"
    )

    st.text_area(
        "Symptoms",
        key="patient_symptoms",
        height=110
    )


    # -----------------------------------------------------
    # CLINICAL DETAILS
    # -----------------------------------------------------

    st.markdown(
        "## Clinical Details"
    )

    detail_left, detail_right = (
        st.columns(2)
    )

    with detail_left:

        st.text_area(
            "Relevant History",
            key="patient_history",
            height=90
        )

        st.text_area(
            "Current Medicines",
            key="patient_medicines",
            height=90
        )

    with detail_right:

        st.text_area(
            "Allergies",
            key="patient_allergies",
            height=90
        )

        st.text_area(
            "Additional Findings",
            key="patient_findings",
            height=90
        )


    # -----------------------------------------------------
    # VITAL SIGNS
    # -----------------------------------------------------

    st.markdown(
        "## Vital Signs"
    )


    bp_value, bp_unit = st.columns(
        [4, 1]
    )

    with bp_value:

        st.text_input(
            "Blood Pressure",
            key="vital_bp",
            placeholder="Example: 120/80"
        )

    with bp_unit:

        st.selectbox(
            "Unit",
            [
                "mmHg",
                "kPa"
            ],
            key="vital_bp_unit"
        )


    pulse_value, pulse_unit = st.columns(
        [4, 1]
    )

    with pulse_value:

        st.text_input(
            "Pulse Rate",
            key="vital_pulse",
            placeholder="Example: 80"
        )

    with pulse_unit:

        st.selectbox(
            "Unit",
            [
                "bpm",
                "beats/sec"
            ],
            key="vital_pulse_unit"
        )


    temp_value, temp_unit = st.columns(
        [4, 1]
    )

    with temp_value:

        st.text_input(
            "Temperature",
            key="vital_temperature",
            placeholder="Example: 98.6"
        )

    with temp_unit:

        st.selectbox(
            "Unit",
            [
                "°F",
                "°C"
            ],
            key="vital_temperature_unit"
        )


    spo2_value, spo2_unit = st.columns(
        [4, 1]
    )

    with spo2_value:

        st.text_input(
            "SpO₂",
            key="vital_spo2",
            placeholder="Example: 98"
        )

    with spo2_unit:

        st.selectbox(
            "Unit",
            ["%"],
            key="vital_spo2_unit"
        )


    weight_value, weight_unit = st.columns(
        [4, 1]
    )

    with weight_value:

        st.text_input(
            "Weight",
            key="vital_weight",
            placeholder="Example: 62"
        )

    with weight_unit:

        st.selectbox(
            "Unit",
            [
                "kg",
                "lb"
            ],
            key="vital_weight_unit"
        )


    height_value, height_unit = st.columns(
        [4, 1]
    )

    with height_value:

        st.text_input(
            "Height",
            key="vital_height",
            placeholder="Example: 168"
        )

    with height_unit:

        st.selectbox(
            "Unit",
            [
                "cm",
                "m",
                "inch"
            ],
            key="vital_height_unit"
        )


    st.text_input(
        "Follow Up",
        key="follow_up",
        placeholder="Example: Review after initial treatment"
    )


    # -----------------------------------------------------
    # ONLY SUBMISSION POINT
    # -----------------------------------------------------

    analyze_button = (
        st.form_submit_button(
            "Analyze Patient",
            use_container_width=True,
            type="primary"
        )
    )


# =========================================================
# RUN ANALYSIS
# =========================================================

if analyze_button:

    symptoms = (
        st.session_state
        .patient_symptoms
        .strip()
    )

    if not symptoms:

        st.error(
            "Symptoms are required."
        )

        st.stop()


    normalized_bp = normalize_bp(
        st.session_state.vital_bp,
        st.session_state.vital_bp_unit
    )

    normalized_pulse = normalize_pulse(
        st.session_state.vital_pulse,
        st.session_state.vital_pulse_unit
    )

    normalized_temperature = (
        normalize_temperature(
            st.session_state.vital_temperature,
            st.session_state.vital_temperature_unit
        )
    )

    normalized_spo2 = normalize_spo2(
        st.session_state.vital_spo2
    )

    normalized_weight = normalize_weight(
        st.session_state.vital_weight,
        st.session_state.vital_weight_unit
    )

    normalized_height = normalize_height(
        st.session_state.vital_height,
        st.session_state.vital_height_unit
    )


    patient = {

        "name":
            st.session_state.patient_name,

        "id":
            st.session_state.patient_id,

        "contact":
            st.session_state.patient_contact,

        "address":
            st.session_state.patient_address,

        "age":
            st.session_state.patient_age,

        "sex":
            st.session_state.patient_sex,

        "duration":
            st.session_state.patient_duration,

        "symptoms":
            st.session_state.patient_symptoms,

        "history":
            st.session_state.patient_history,

        "medicines":
            st.session_state.patient_medicines,

        "allergies":
            st.session_state.patient_allergies,

        "findings":
            st.session_state.patient_findings,

        "follow_up":
            st.session_state.follow_up,


        "display_bp":
            display_measurement(
                st.session_state.vital_bp,
                st.session_state.vital_bp_unit
            ),

        "display_pulse":
            display_measurement(
                st.session_state.vital_pulse,
                st.session_state.vital_pulse_unit
            ),

        "display_temperature":
            display_measurement(
                st.session_state.vital_temperature,
                st.session_state.vital_temperature_unit
            ),

        "display_spo2":
            display_measurement(
                st.session_state.vital_spo2,
                st.session_state.vital_spo2_unit
            ),

        "display_weight":
            display_measurement(
                st.session_state.vital_weight,
                st.session_state.vital_weight_unit
            ),

        "display_height":
            display_measurement(
                st.session_state.vital_height,
                st.session_state.vital_height_unit
            ),


        "normalized_bp":
            normalized_bp,

        "normalized_pulse":
            normalized_pulse,

        "normalized_temperature":
            normalized_temperature,

        "normalized_spo2":
            normalized_spo2,

        "normalized_weight":
            normalized_weight,

        "normalized_height":
            normalized_height
    }


    patient_text = build_patient_text(
        patient
    )


    with st.spinner(
        "Analyzing patient..."
    ):

        if (
            st.session_state.system_mode
            ==
            "Applicability-Aware RAG"
        ):

            result = (
                generate_clinical_response(
                    patient_text,
                    top_k=10
                )
            )

        else:

            result = (
                generate_baseline_response(
                    patient_text,
                    top_k=5
                )
            )


    response = result[
        "generated_response"
    ]


    generated_time = datetime.now()


    report_id = (
        "CR-"
        + generated_time.strftime(
            "%Y%m%d-%H%M%S"
        )
    )


    generated_on = (
        generated_time.strftime(
            "%d %b %Y, %I:%M %p"
        )
    )


    st.session_state.analysis_payload = {

        "patient":
            patient,

        "patient_text":
            patient_text,

        "result":
            result,

        "response":
            response,

        "mode":
            st.session_state.system_mode,

        "report_id":
            report_id,

        "generated_on":
            generated_on
    }


# =========================================================
# RESULTS
# =========================================================

if "analysis_payload" in st.session_state:

    payload = st.session_state.analysis_payload

    patient = payload["patient"]
    result = payload["result"]
    response = payload["response"]

    sections = split_response_sections(
        response
    )


    primary = result.get(
        "primary_disease",
        ""
    )

    if not primary:
        primary = "See probable diagnosis"


    differential_names = []

    for item in result.get(
        "differential_diagnoses",
        []
    ):

        if isinstance(item, dict):

            disease = item.get(
                "disease"
            )

            if disease:
                differential_names.append(
                    disease
                )


    st.markdown("---")


    tabs = st.tabs(
        [
            "Clinical Analysis",
            "Professional Report",
            "Clinical Slip",
            "Blank Printable Form"
        ]
    )


    # =====================================================
    # CLINICAL ANALYSIS
    # =====================================================

    with tabs[0]:

        st.markdown(
            "## Clinical Assessment"
        )


        if (
            payload["mode"]
            ==
            "Applicability-Aware RAG"
        ):

            status_left, status_right = (
                st.columns(2)
            )

            with status_left:

                st.success(
                    f"Primary context: {primary}"
                )

            with status_right:

                if differential_names:

                    st.info(
                        "Differential: "
                        + ", ".join(
                            differential_names
                        )
                    )


        result_left, result_right = (
            st.columns(2)
        )


        with result_left:

            display_card(
                "Probable Diagnosis",
                sections.get(
                    "Probable Diagnosis:",
                    ""
                ),
                "🔎"
            )

            display_card(
                "Investigations",
                sections.get(
                    "Investigations:",
                    ""
                ),
                "🧪"
            )

            display_card(
                "Medication Planning",
                sections.get(
                    "Medication Planning:",
                    ""
                ),
                "💊"
            )


        with result_right:

            display_card(
                "Patient Advice",
                sections.get(
                    "Advice:",
                    ""
                ),
                "📋"
            )


            st.markdown(
                "### ⚠️ Missing Information"
            )


            missing = sections.get(
                "Missing Information:",
                ""
            )


            if (
                missing
                and
                "No major applicability information"
                not in missing
            ):

                friendly_missing = (
                    missing
                    .replace(
                        "dehydration_severity",
                        "dehydration severity"
                    )
                    .replace(
                        "severe_dehydration",
                        "severe dehydration status"
                    )
                )

                st.warning(
                    friendly_missing
                )

            else:

                st.success(
                    "No required applicability "
                    "information is missing."
                )


            display_card(
                "Evidence",
                sections.get(
                    "Evidence:",
                    ""
                ),
                "📚"
            )


        if (
            payload["mode"]
            ==
            "Applicability-Aware RAG"
        ):

            with st.expander(
                "Recommendation Details",
                expanded=False
            ):

                st.markdown(
                    "#### Detected Clinical Facts"
                )

                patient_facts = result.get(
                    "patient_facts",
                    {}
                )

                if patient_facts:

                    friendly_facts = {}

                    for key, value in patient_facts.items():

                        friendly_key = (
                            key
                            .replace("_", " ")
                            .title()
                        )

                        friendly_facts[
                            friendly_key
                        ] = value

                    st.json(
                        friendly_facts
                    )

                else:

                    st.write(
                        "No structured applicability "
                        "facts detected."
                    )


                st.markdown(
                    "#### Accepted Evidence"
                )


                accepted_cards = result.get(
                    "accepted_cards",
                    []
                )


                if accepted_cards:

                    for card in accepted_cards:

                        st.markdown(
                            f"**{card['card_id']}**"
                        )

                        st.write(
                            f"{card['disease']} — "
                            f"{card['category']}"
                        )

                        score = card.get(
                            "score",
                            0
                        )

                        reason = card.get(
                            "applicability_reason",
                            ""
                        )

                        st.caption(
                            f"Similarity: "
                            f"{score:.3f} | "
                            f"{reason}"
                        )

                else:

                    st.write(
                        "No evidence cards accepted."
                    )


                st.markdown(
                    "#### Blocked Evidence"
                )


                rejected = result.get(
                    "rejected_cards",
                    []
                )


                if rejected:

                    for card in rejected:

                        reason = (
                            card.get(
                                "applicability_reason",
                                ""
                            )
                            .replace(
                                "dehydration_severity",
                                "dehydration severity"
                            )
                            .replace(
                                "severe_dehydration",
                                "severe dehydration status"
                            )
                        )

                        st.markdown(
                            f"**{card['card_id']}**"
                        )

                        st.write(
                            reason
                        )

                else:

                    st.write(
                        "No evidence cards blocked."
                    )


        with st.expander(
            "Technical Details",
            expanded=False
        ):

            st.code(
                payload["patient_text"],
                language=None
            )

            st.code(
                response,
                language=None
            )


    # =====================================================
    # PROFESSIONAL REPORT
    # =====================================================

    with tabs[1]:

        st.markdown(
            "## Professional Clinical Report"
        )

        report_html = (
            build_professional_report(
                patient,
                sections,
                primary,
                differential_names,
                payload["report_id"],
                payload["generated_on"]
            )
        )

        components.html(
            report_html,
            height=1250,
            scrolling=True
        )


    # =====================================================
    # CLINICAL SLIP
    # =====================================================

    with tabs[2]:

        st.markdown(
            "## Clinical Slip"
        )

        slip_html = (
            build_clinical_slip(
                patient,
                sections,
                primary,
                payload["report_id"],
                payload["generated_on"]
            )
        )

        components.html(
            slip_html,
            height=950,
            scrolling=True
        )


    # =====================================================
    # BLANK PRINTABLE FORM
    # =====================================================

    with tabs[3]:

        st.markdown(
            "## Blank Printable Clinical Form"
        )

        components.html(
            build_blank_form(),
            height=1250,
            scrolling=True
        )