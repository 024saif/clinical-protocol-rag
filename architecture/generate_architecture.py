from pathlib import Path
from html import escape


# =========================================================
# OUTPUT
# =========================================================

OUTPUT_DIR = Path("architecture")
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "clinical_rag_architecture.svg"
)


# =========================================================
# SVG HELPERS
# =========================================================

WIDTH = 1800
HEIGHT = 1000


def svg_text(
    x,
    y,
    lines,
    size=16,
    weight="normal",
    anchor="middle",
    color="#173B36",
    line_height=22
):

    result = [
        (
            f'<text x="{x}" y="{y}" '
            f'font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" '
            f'font-weight="{weight}" '
            f'text-anchor="{anchor}" '
            f'fill="{color}">'
        )
    ]

    for index, line in enumerate(lines):

        dy = (
            0
            if index == 0
            else line_height
        )

        result.append(
            (
                f'<tspan x="{x}" '
                f'dy="{dy}">'
                f'{escape(str(line))}'
                f'</tspan>'
            )
        )

    result.append(
        "</text>"
    )

    return "".join(
        result
    )


def box(
    x,
    y,
    width,
    height,
    title,
    lines,
    fill,
    stroke,
    stroke_width=2,
    dashed=False
):

    dash = (
        ' stroke-dasharray="10 7"'
        if dashed
        else ""
    )

    elements = []

    elements.append(
        (
            f'<rect '
            f'x="{x}" '
            f'y="{y}" '
            f'width="{width}" '
            f'height="{height}" '
            f'rx="18" '
            f'fill="{fill}" '
            f'stroke="{stroke}" '
            f'stroke-width="{stroke_width}"'
            f'{dash}/>'
        )
    )

    elements.append(
        svg_text(
            x + width / 2,
            y + 32,
            [title],
            size=17,
            weight="bold"
        )
    )

    start_y = y + 62

    elements.append(
        svg_text(
            x + width / 2,
            start_y,
            lines,
            size=14,
            color="#274A45",
            line_height=20
        )
    )

    return "".join(
        elements
    )


def arrow(
    x1,
    y1,
    x2,
    y2,
    label=None,
    dashed=False,
    color="#4C6863"
):

    dash = (
        ' stroke-dasharray="8 6"'
        if dashed
        else ""
    )

    elements = []

    elements.append(
        (
            f'<line '
            f'x1="{x1}" '
            f'y1="{y1}" '
            f'x2="{x2}" '
            f'y2="{y2}" '
            f'stroke="{color}" '
            f'stroke-width="3" '
            f'marker-end="url(#arrowhead)"'
            f'{dash}/>'
        )
    )

    if label:

        mid_x = (
            x1 + x2
        ) / 2

        mid_y = (
            y1 + y2
        ) / 2 - 9

        elements.append(
            (
                f'<rect '
                f'x="{mid_x - 55}" '
                f'y="{mid_y - 15}" '
                f'width="110" '
                f'height="22" '
                f'rx="5" '
                f'fill="#FFFFFF" '
                f'opacity="0.92"/>'
            )
        )

        elements.append(
            svg_text(
                mid_x,
                mid_y,
                [label],
                size=12,
                weight="bold",
                color="#4C6863"
            )
        )

    return "".join(
        elements
    )


def group_title(
    x,
    y,
    text
):

    return svg_text(
        x,
        y,
        [text],
        size=15,
        weight="bold",
        anchor="start",
        color="#496D67"
    )


# =========================================================
# BUILD SVG
# =========================================================

def build_architecture():

    svg = []

    svg.append(
        f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>
"""
    )


    # =====================================================
    # DEFINITIONS
    # =====================================================

    svg.append(
        """
<defs>

    <marker
        id="arrowhead"
        markerWidth="10"
        markerHeight="7"
        refX="9"
        refY="3.5"
        orient="auto"
    >
        <polygon
            points="0 0, 10 3.5, 0 7"
            fill="#4C6863"
        />
    </marker>

    <filter
        id="shadow"
        x="-20%"
        y="-20%"
        width="140%"
        height="140%"
    >
        <feDropShadow
            dx="0"
            dy="4"
            stdDeviation="5"
            flood-opacity="0.12"
        />
    </filter>

</defs>
"""
    )


    # =====================================================
    # BACKGROUND
    # =====================================================

    svg.append(
        (
            f'<rect '
            f'x="0" '
            f'y="0" '
            f'width="{WIDTH}" '
            f'height="{HEIGHT}" '
            f'fill="#F8FBFA"/>'
        )
    )


    # =====================================================
    # TITLE
    # =====================================================

    svg.append(
        svg_text(
            WIDTH / 2,
            48,
            [
                "Clinical Protocol RAG Architecture"
            ],
            size=30,
            weight="bold",
            color="#173B36"
        )
    )

    svg.append(
        svg_text(
            WIDTH / 2,
            80,
            [
                "Baseline Retrieval vs Applicability-Aware Clinical RAG"
            ],
            size=16,
            color="#557570"
        )
    )


    # =====================================================
    # GROUP LABELS
    # =====================================================

    svg.append(
        group_title(
            60,
            135,
            "1. Protocol Preparation & Knowledge Base"
        )
    )

    svg.append(
        group_title(
            60,
            415,
            "2. Patient Input, Retrieval & Applicability"
        )
    )

    svg.append(
        group_title(
            60,
            715,
            "3. Recommendation Output & Future Integration"
        )
    )


    # =====================================================
    # ROW 1
    # =====================================================

    svg.append(
        box(
            60,
            160,
            230,
            170,
            "Clinical Protocols",
            [
                "Dengue",
                "Hypertension",
                "Cholera",
                "Chikungunya"
            ],
            "#DDEDEA",
            "#5E8F87"
        )
    )

    svg.append(
        box(
            350,
            160,
            250,
            170,
            "Protocol Extraction",
            [
                "Assigned PDF pages",
                "Tables & footnotes",
                "Conditions",
                "Exceptions",
                "Source pages"
            ],
            "#EAF4F2",
            "#5E8F87"
        )
    )

    svg.append(
        box(
            660,
            160,
            280,
            170,
            "Canonical Cards",
            [
                "JSON / JSONL",
                "Symptoms & prerequisites",
                "Recommended action",
                "Exclusions / missing info",
                "Evidence + source page"
            ],
            "#DDEDEA",
            "#5E8F87"
        )
    )

    svg.append(
        box(
            1000,
            160,
            250,
            170,
            "Embeddings",
            [
                "SentenceTransformer",
                "all-MiniLM-L6-v2",
                "Normalized vectors"
            ],
            "#E3EDF4",
            "#6E92AB"
        )
    )

    svg.append(
        box(
            1310,
            160,
            250,
            170,
            "RAG Index",
            [
                "FAISS IndexFlatIP",
                "Embeddings",
                "Metadata",
                "Source traceability"
            ],
            "#DCEAF3",
            "#6E92AB"
        )
    )


    svg.append(
        arrow(
            290,
            245,
            350,
            245
        )
    )

    svg.append(
        arrow(
            600,
            245,
            660,
            245
        )
    )

    svg.append(
        arrow(
            940,
            245,
            1000,
            245
        )
    )

    svg.append(
        arrow(
            1250,
            245,
            1310,
            245
        )
    )


    # =====================================================
    # ROW 2
    # =====================================================

    svg.append(
        box(
            60,
            445,
            250,
            180,
            "Patient Input",
            [
                "Chief complaints",
                "Symptoms & duration",
                "Age / sex / history",
                "Medicines / allergies",
                "Findings & vitals"
            ],
            "#EEE8F5",
            "#8B73A9"
        )
    )

    svg.append(
        box(
            360,
            445,
            250,
            180,
            "Input Processing",
            [
                "Unit conversion",
                "Context assembly",
                "Structured patient facts"
            ],
            "#F3EEF8",
            "#8B73A9"
        )
    )

    svg.append(
        box(
            660,
            445,
            240,
            180,
            "Semantic Retrieval",
            [
                "Retrieve top matching",
                "canonical cards",
                "from FAISS"
            ],
            "#F7EBDD",
            "#C2864F"
        )
    )

    svg.append(
        box(
            950,
            445,
            240,
            180,
            "Primary Context",
            [
                "Identify most supported",
                "disease / protocol",
                "context"
            ],
            "#F9EFE3",
            "#C2864F"
        )
    )

    svg.append(
        box(
            1240,
            425,
            260,
            200,
            "Applicability Filter",
            [
                "Prerequisites",
                "Exclusions",
                "Patient restrictions",
                "Disease consistency"
            ],
            "#F7E6D5",
            "#B9733E",
            stroke_width=4
        )
    )

    svg.append(
        box(
            1540,
            425,
            220,
            200,
            "Missing-Info Check",
            [
                "Identify required facts",
                "Block unsupported",
                "treatment",
                "Do not guess"
            ],
            "#FBEFE3",
            "#B9733E",
            stroke_width=4
        )
    )


    svg.append(
        svg_text(
            1500,
            402,
            [
                "TESTED IMPROVEMENT"
            ],
            size=13,
            weight="bold",
            color="#A35D2A"
        )
    )


    svg.append(
        arrow(
            310,
            535,
            360,
            535
        )
    )

    svg.append(
        arrow(
            610,
            535,
            660,
            535
        )
    )

    svg.append(
        arrow(
            900,
            535,
            950,
            535
        )
    )

    svg.append(
        arrow(
            1190,
            535,
            1240,
            535
        )
    )

    svg.append(
        arrow(
            1500,
            535,
            1540,
            535
        )
    )


    # Index to retrieval
    svg.append(
        arrow(
            1435,
            330,
            800,
            445,
            label="vector search"
        )
    )


    # =====================================================
    # BASELINE BRANCH
    # =====================================================

    svg.append(
        box(
            680,
            660,
            250,
            130,
            "Baseline Mode",
            [
                "Top-k semantic cards",
                "No applicability filter"
            ],
            "#FCE3E3",
            "#B76F6F"
        )
    )

    svg.append(
        arrow(
            785,
            625,
            805,
            660,
            label="Baseline"
        )
    )


    # =====================================================
    # OUTPUT
    # =====================================================

    svg.append(
        box(
            1020,
            690,
            300,
            190,
            "Recommendation Assembly",
            [
                "Probable diagnosis",
                "Investigations",
                "Medication planning",
                "Advice",
                "Missing information",
                "Evidence"
            ],
            "#DFF0E5",
            "#5C956F"
        )
    )

    svg.append(
        box(
            1380,
            690,
            300,
            190,
            "Streamlit Interface",
            [
                "Clinical analysis",
                "Professional report",
                "Clinical slip",
                "Blank printable form",
                "Evidence details"
            ],
            "#D8EBDF",
            "#5C956F"
        )
    )


    svg.append(
        arrow(
            930,
            725,
            1020,
            770,
            label="Baseline"
        )
    )

    svg.append(
        arrow(
            1650,
            625,
            1170,
            690,
            label="Improved"
        )
    )

    svg.append(
        arrow(
            1320,
            785,
            1380,
            785
        )
    )


    # =====================================================
    # FUTURE COMPONENTS
    # =====================================================

    svg.append(
        box(
            60,
            805,
            250,
            125,
            "Future NER Input",
            [
                "Extract symptoms",
                "vitals & medicines"
            ],
            "#F3F3F3",
            "#888888",
            dashed=True
        )
    )

    svg.append(
        box(
            370,
            805,
            260,
            125,
            "Doctor Feedback",
            [
                "Accept",
                "Reject",
                "Modify"
            ],
            "#F3F3F3",
            "#888888",
            dashed=True
        )
    )

    svg.append(
        box(
            690,
            805,
            260,
            125,
            "Prescription Assembly",
            [
                "Clinician-approved",
                "recommendations"
            ],
            "#F3F3F3",
            "#888888",
            dashed=True
        )
    )


    svg.append(
        arrow(
            185,
            805,
            450,
            625,
            label="future",
            dashed=True
        )
    )

    svg.append(
        arrow(
            1380,
            850,
            630,
            870,
            label="future feedback",
            dashed=True
        )
    )

    svg.append(
        arrow(
            630,
            870,
            690,
            870,
            label="future",
            dashed=True
        )
    )


    # =====================================================
    # TRACEABILITY
    # =====================================================

    svg.append(
        arrow(
            800,
            330,
            1500,
            690,
            label="source IDs + pages",
            dashed=True
        )
    )


    # =====================================================
    # LEGEND
    # =====================================================

    svg.append(
        svg_text(
            1110,
            955,
            [
                "Solid components = implemented prototype"
            ],
            size=13,
            anchor="start",
            color="#4C6863"
        )
    )

    svg.append(
        svg_text(
            1110,
            980,
            [
                "Dashed components = future integration"
            ],
            size=13,
            anchor="start",
            color="#777777"
        )
    )


    svg.append(
        "</svg>"
    )


    OUTPUT_FILE.write_text(
        "".join(svg),
        encoding="utf-8"
    )


    print(
        "\nArchitecture diagram created successfully:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nOpen it with:"
    )

    print(
        "start architecture\\clinical_rag_architecture.svg"
    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    build_architecture()