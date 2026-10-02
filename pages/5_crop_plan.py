import json
from io import BytesIO
from typing import Any

import streamlit as st

from utils.formatting import pkr


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="CropCare Plan | NabatAI",
    page_icon="🌱",
    layout="wide",
)




# ============================================================
# PDF DEPENDENCY
# ============================================================

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True

except ImportError:
    REPORTLAB_AVAILABLE = False


# ============================================================
# HELPERS
# ============================================================

def safe_text(value: Any, default: str = "Not provided") -> str:
    """Convert values safely to readable text."""
    if value is None:
        return default

    if isinstance(value, str) and not value.strip():
        return default

    if isinstance(value, list):
        if not value:
            return default
        return ", ".join(str(item) for item in value)

    if isinstance(value, dict):
        if not value:
            return default
        return json.dumps(value, ensure_ascii=False, default=str)

    return str(value)


def safe_money(value: Any) -> str:
    """Format a value as Pakistani Rupees."""
    try:
        return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Not available"


def html_safe(value: Any) -> str:
    """Prevent basic ReportLab paragraph markup problems."""
    text = safe_text(value)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def extract_profile_value(profile: dict, *keys: str, default: str = "") -> Any:
    """Read the first matching profile field."""
    for key in keys:
        value = profile.get(key)

        if value not in (None, ""):
            return value

    return default


def get_latest_assessment() -> dict:
    """Prefer the second-round assessment when available."""
    return (
        st.session_state.get("second_assessment")
        or st.session_state.get("first_assessment")
        or {}
    )


def build_case_export() -> dict:
    """
    Build the complete portable NabatAI case.

    JSON is intended for later import/resume.
    PDF is intended for human-readable reporting.
    """

    first_assessment = st.session_state.get(
        "first_assessment",
        {},
    )

    second_assessment = st.session_state.get(
        "second_assessment",
        {},
    )

    requested_tests = (
        first_assessment
        .get("evidence", {})
        .get("tests", [])
    )

    references = (
        second_assessment.get("references")
        or first_assessment.get("references")
        or []
    )

    return {
        "profile": st.session_state.get(
            "profile",
            {},
        ),
        "structured_case": (
            second_assessment.get("structured_case")
            or first_assessment.get("structured_case")
            or {}
        ),
        "problem_description": extract_profile_value(
            st.session_state.get("profile", {}),
            "problem_description",
            "problem",
            "symptoms",
            default="",
        ),
        "first_assessment": first_assessment,
        "requested_tests": requested_tests,
        "report_extraction": st.session_state.get(
            "report_extraction",
            {},
        ),
        "confirmed_values": st.session_state.get(
            "confirmed_values",
            {},
        ),
        "second_assessment": second_assessment,
        "options": st.session_state.get(
            "options",
            {},
        ),
        "plan": st.session_state.get(
            "plan",
            {},
        ),
        "expert_review": st.session_state.get(
            "expert_review",
            {},
        ),
        "references": references,
    }


# ============================================================
# PDF GENERATOR
# ============================================================

def generate_case_pdf(case_data: dict) -> bytes:
    """Generate a complete NabatAI PDF report in memory."""

    if not REPORTLAB_AVAILABLE:
        raise RuntimeError(
            "ReportLab is not installed. Add "
            "'reportlab>=4.2.0' to requirements.txt."
        )

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="NabatAI Crop Decision Support Report",
        author="NabatAI",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "NabatAITitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1B5E20"),
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "NabatAISubtitle",
        parent=styles["Heading2"],
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#455A64"),
        spaceAfter=16,
    )

    section_style = ParagraphStyle(
        "NabatAISection",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1B5E20"),
        spaceBefore=12,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "NabatAIBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "NabatAISmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#616161"),
        spaceAfter=4,
    )

    warning_style = ParagraphStyle(
        "NabatAIWarning",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#8A4B08"),
        backColor=colors.HexColor("#FFF8E1"),
        borderPadding=7,
        spaceBefore=6,
        spaceAfter=8,
    )

    story = []

    profile = case_data.get("profile", {})
    first_assessment = case_data.get("first_assessment", {})
    second_assessment = case_data.get("second_assessment", {})
    latest_assessment = second_assessment or first_assessment

    crop = extract_profile_value(
        profile,
        "crop",
        default="Crop case",
    )

    location = extract_profile_value(
        profile,
        "district",
        "location",
        default="Not provided",
    )

    # ========================================================
    # COVER
    # ========================================================

    story.append(
        Paragraph(
            "NabatAI",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Evidence-Based Plant Biotechnology & "
            "Crop Decision Support for Pakistan",
            subtitle_style,
        )
    )

    story.append(
        Spacer(
            1,
            8,
        )
    )

    cover_rows = [
        [
            Paragraph(
                "<b>Crop</b>",
                body_style,
            ),
            Paragraph(
                html_safe(crop),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Location</b>",
                body_style,
            ),
            Paragraph(
                html_safe(location),
                body_style,
            ),
        ],
        [
            Paragraph(
                "<b>Report Type</b>",
                body_style,
            ),
            Paragraph(
                "Crop Decision Support Report",
                body_style,
            ),
        ],
    ]

    cover_table = Table(
        cover_rows,
        colWidths=[
            45 * mm,
            115 * mm,
        ],
    )

    cover_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#E8F5E9"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D0D0D0"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(cover_table)

    story.append(
        Spacer(
            1,
            14,
        )
    )

    story.append(
        Paragraph(
            "<b>Responsible AI Notice:</b> "
            "NabatAI provides decision support, not guaranteed diagnosis. "
            "Critical agricultural and financial decisions should be "
            "confirmed with qualified local professionals.",
            warning_style,
        )
    )

    story.append(PageBreak())

    # ========================================================
    # 1. PROFILE
    # ========================================================

    story.append(
        Paragraph(
            "1. Crop & Grower Profile",
            section_style,
        )
    )

    area = extract_profile_value(
        profile,
        "area",
        default="",
    )

    area_unit = extract_profile_value(
        profile,
        "area_unit",
        default="",
    )

    if area:
        area_display = f"{area} {area_unit}".strip()
    else:
        area_display = "Not provided"

    profile_rows = [
        [
            "User Type",
            safe_text(
                extract_profile_value(
                    profile,
                    "user_type",
                )
            ),
        ],
        [
            "Language",
            safe_text(
                extract_profile_value(
                    profile,
                    "language",
                )
            ),
        ],
        [
            "Crop",
            safe_text(crop),
        ],
        [
            "Variety",
            safe_text(
                extract_profile_value(
                    profile,
                    "variety",
                )
            ),
        ],
        [
            "District / Location",
            safe_text(location),
        ],
        [
            "Area",
            area_display,
        ],
        [
            "Crop Age",
            safe_text(
                extract_profile_value(
                    profile,
                    "crop_age",
                )
            ),
        ],
        [
            "Growth Stage",
            safe_text(
                extract_profile_value(
                    profile,
                    "growth_stage",
                )
            ),
        ],
        [
            "Purpose",
            safe_text(
                extract_profile_value(
                    profile,
                    "purpose",
                )
            ),
        ],
        [
            "Irrigation Source",
            safe_text(
                extract_profile_value(
                    profile,
                    "irrigation_source",
                    "irrigation",
                )
            ),
        ],
        [
            "Available Budget",
            safe_money(
                extract_profile_value(
                    profile,
                    "budget",
                    "available_budget",
                    default=0,
                )
            ),
        ],
        [
            "Expected Crop Value",
            safe_money(
                extract_profile_value(
                    profile,
                    "expected_crop_value",
                    "crop_value",
                    default=0,
                )
            ),
        ],
    ]

    formatted_profile_rows = []

    for label, value in profile_rows:
        formatted_profile_rows.append(
            [
                Paragraph(
                    f"<b>{html_safe(label)}</b>",
                    body_style,
                ),
                Paragraph(
                    html_safe(value),
                    body_style,
                ),
            ]
        )

    profile_table = Table(
        formatted_profile_rows,
        colWidths=[
            55 * mm,
            105 * mm,
        ],
    )

    profile_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#E8F5E9"),
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor("#D8D8D8"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(profile_table)

    # ========================================================
    # 2. PROBLEM
    # ========================================================

    story.append(
        Paragraph(
            "2. Reported Problem",
            section_style,
        )
    )

    problem_description = case_data.get(
        "problem_description",
        "",
    )

    story.append(
        Paragraph(
            html_safe(problem_description),
            body_style,
        )
    )

    previous_fertilizer = extract_profile_value(
        profile,
        "previous_fertilizer_applications",
        "previous_fertilizer",
        default="",
    )

    previous_pesticide = extract_profile_value(
        profile,
        "previous_pesticide_applications",
        "previous_pesticide",
        default="",
    )

    if previous_fertilizer:
        story.append(
            Paragraph(
                "<b>Previous fertilizer:</b> "
                + html_safe(previous_fertilizer),
                body_style,
            )
        )

    if previous_pesticide:
        story.append(
            Paragraph(
                "<b>Previous pesticide:</b> "
                + html_safe(previous_pesticide),
                body_style,
            )
        )

    # ========================================================
    # 3. INITIAL ASSESSMENT
    # ========================================================

    story.append(
        Paragraph(
            "3. Initial AI Assessment",
            section_style,
        )
    )

    plant_health = first_assessment.get(
        "plant_health",
        {},
    )

    hypotheses = plant_health.get(
        "hypotheses",
        [],
    )

    if hypotheses:

        hypothesis_rows = [
            [
                Paragraph(
                    "<b>Possible Cause</b>",
                    body_style,
                ),
                Paragraph(
                    "<b>Category</b>",
                    body_style,
                ),
                Paragraph(
                    "<b>Confidence</b>",
                    body_style,
                ),
                Paragraph(
                    "<b>Why Considered</b>",
                    body_style,
                ),
            ]
        ]

        for hypothesis in hypotheses:

            hypothesis_rows.append(
                [
                    Paragraph(
                        html_safe(
                            hypothesis.get(
                                "name",
                                "Unnamed hypothesis",
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            hypothesis.get(
                                "category",
                                "uncertain",
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            hypothesis.get(
                                "confidence",
                                "LOW",
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            hypothesis.get(
                                "rationale",
                                "",
                            )
                        ),
                        small_style,
                    ),
                ]
            )

        hypothesis_table = Table(
            hypothesis_rows,
            colWidths=[
                40 * mm,
                30 * mm,
                24 * mm,
                66 * mm,
            ],
            repeatRows=1,
        )

        hypothesis_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#DDEEDD"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#D8D8D8"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(hypothesis_table)

    else:
        story.append(
            Paragraph(
                "No initial hypotheses are available in this case.",
                body_style,
            )
        )

    uncertainty = plant_health.get(
        "uncertainty",
        "",
    )

    if uncertainty:
        story.append(
            Spacer(
                1,
                5,
            )
        )

        story.append(
            Paragraph(
                "<b>Uncertainty:</b> "
                + html_safe(uncertainty),
                body_style,
            )
        )

    # ========================================================
    # 4. SKEPTIC REVIEW
    # ========================================================

    story.append(
        Paragraph(
            "4. Skeptic Review & Uncertainty Challenge",
            section_style,
        )
    )

    skeptic = first_assessment.get(
        "skeptic",
        {},
    )

    if skeptic:

        challenge = skeptic.get(
            "challenge",
            "",
        )

        if challenge:
            story.append(
                Paragraph(
                    "<b>Challenge to the current assessment:</b> "
                    + html_safe(challenge),
                    body_style,
                )
            )

        skeptic_sections = [
            (
                "Competing Explanations",
                skeptic.get(
                    "competing_explanations",
                    [],
                ),
            ),
            (
                "Missing Evidence",
                skeptic.get(
                    "missing_evidence",
                    [],
                ),
            ),
            (
                "Unsupported Assumptions",
                skeptic.get(
                    "unsupported_assumptions",
                    [],
                ),
            ),
            (
                "Contradictions",
                skeptic.get(
                    "contradictions",
                    [],
                ),
            ),
        ]

        for heading, items in skeptic_sections:

            if not items:
                continue

            story.append(
                Paragraph(
                    f"<b>{heading}</b>",
                    body_style,
                )
            )

            if not isinstance(items, list):
                items = [items]

            for item in items:
                story.append(
                    Paragraph(
                        "• " + html_safe(item),
                        body_style,
                    )
                )

        confidence_reason = skeptic.get(
            "confidence_reduction_reason",
            "",
        )

        if confidence_reason:
            story.append(
                Paragraph(
                    "<b>Reason confidence should remain cautious:</b> "
                    + html_safe(confidence_reason),
                    body_style,
                )
            )

    else:
        story.append(
            Paragraph(
                "No Skeptic Agent result is available.",
                body_style,
            )
        )

    # ========================================================
    # 5. TESTS
    # ========================================================

    story.append(
        Paragraph(
            "5. Recommended Field Checks / Laboratory Evidence",
            section_style,
        )
    )

    requested_tests = case_data.get(
        "requested_tests",
        [],
    )

    if requested_tests:

        test_rows = [
            [
                Paragraph(
                    "<b>Test / Check</b>",
                    small_style,
                ),
                Paragraph(
                    "<b>Priority</b>",
                    small_style,
                ),
                Paragraph(
                    "<b>Why Needed</b>",
                    small_style,
                ),
                Paragraph(
                    "<b>Estimated Cost</b>",
                    small_style,
                ),
                Paragraph(
                    "<b>Evidence</b>",
                    small_style,
                ),
            ]
        ]

        for test in requested_tests:

            test_rows.append(
                [
                    Paragraph(
                        html_safe(
                            test.get(
                                "name",
                                "Test",
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            test.get(
                                "priority",
                                "",
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            test.get(
                                "why_needed",
                                test.get(
                                    "reason",
                                    "",
                                ),
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            safe_money(
                                test.get(
                                    "estimated_cost_pkr",
                                    0,
                                )
                            )
                        ),
                        small_style,
                    ),
                    Paragraph(
                        html_safe(
                            test.get(
                                "evidence_strength",
                                "",
                            )
                        ),
                        small_style,
                    ),
                ]
            )

        tests_table = Table(
            test_rows,
            colWidths=[
                32 * mm,
                20 * mm,
                66 * mm,
                25 * mm,
                24 * mm,
            ],
            repeatRows=1,
        )

        tests_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#DDEEDD"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#D8D8D8"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        3,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        3,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(tests_table)

    else:
        story.append(
            Paragraph(
                "No additional test was recorded for this case.",
                body_style,
            )
        )

    # ========================================================
    # 6. LAB REPORT / CONFIRMED VALUES
    # ========================================================

    confirmed_values = case_data.get(
        "confirmed_values",
        {},
    )

    story.append(
        Paragraph(
            "6. Confirmed Evidence",
            section_style,
        )
    )

    if confirmed_values:

        confirmed_rows = [
            [
                Paragraph(
                    "<b>Parameter</b>",
                    body_style,
                ),
                Paragraph(
                    "<b>Confirmed Value</b>",
                    body_style,
                ),
            ]
        ]

        for key, value in confirmed_values.items():

            confirmed_rows.append(
                [
                    Paragraph(
                        html_safe(
                            str(key)
                            .replace("_", " ")
                            .title()
                        ),
                        body_style,
                    ),
                    Paragraph(
                        html_safe(value),
                        body_style,
                    ),
                ]
            )

        confirmed_table = Table(
            confirmed_rows,
            colWidths=[
                70 * mm,
                90 * mm,
            ],
            repeatRows=1,
        )

        confirmed_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#DDEEDD"),
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#D8D8D8"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        story.append(confirmed_table)

    else:
        story.append(
            Paragraph(
                "No laboratory or field evidence has been confirmed yet.",
                body_style,
            )
        )

    # ========================================================
    # 7. RE-EVALUATION
    # ========================================================

    story.append(
        Paragraph(
            "7. Re-Evaluation After New Evidence",
            section_style,
        )
    )

    if second_assessment:

        change_explanation = second_assessment.get(
            "change_explanation",
            "",
        )

        if change_explanation:

            story.append(
                Paragraph(
                    "<b>Why did our assessment change?</b><br/>"
                    + html_safe(change_explanation),
                    body_style,
                )
            )

        second_plant = second_assessment.get(
            "plant_health",
            {},
        )

        updated_hypotheses = second_plant.get(
            "hypotheses",
            [],
        )

        if updated_hypotheses:

            updated_rows = [
                [
                    Paragraph(
                        "<b>Updated Hypothesis</b>",
                        small_style,
                    ),
                    Paragraph(
                        "<b>Confidence</b>",
                        small_style,
                    ),
                    Paragraph(
                        "<b>Reasoning</b>",
                        small_style,
                    ),
                ]
            ]

            for hypothesis in updated_hypotheses:

                updated_rows.append(
                    [
                        Paragraph(
                            html_safe(
                                hypothesis.get(
                                    "name",
                                    "",
                                )
                            ),
                            small_style,
                        ),
                        Paragraph(
                            html_safe(
                                hypothesis.get(
                                    "confidence",
                                    "",
                                )
                            ),
                            small_style,
                        ),
                        Paragraph(
                            html_safe(
                                hypothesis.get(
                                    "rationale",
                                    "",
                                )
                            ),
                            small_style,
                        ),
                    ]
                )

            updated_table = Table(
                updated_rows,
                colWidths=[
                    52 * mm,
                    28 * mm,
                    80 * mm,
                ],
                repeatRows=1,
            )

            updated_table.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#DDEEDD"),
                        ),
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.HexColor("#D8D8D8"),
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )

            story.append(updated_table)

    else:
        story.append(
            Paragraph(
                "A second-round assessment has not yet been completed. "
                "The current plan may therefore still be based on the "
                "initial assessment.",
                warning_style,
            )
        )

    # ========================================================
    # 8. SAFETY
    # ========================================================

    story.append(
        Paragraph(
            "8. Safety & Human Review Status",
            section_style,
        )
    )

    safety = latest_assessment.get(
        "safety",
        {},
    )

    safety_level = safety.get(
        "level",
        "Not available",
    )

    story.append(
        Paragraph(
            "<b>Safety classification:</b> "
            + html_safe(safety_level),
            body_style,
        )
    )

    safety_reasons = safety.get(
        "reasons",
        [],
    )

    if safety_reasons:

        for reason in safety_reasons:

            story.append(
                Paragraph(
                    "• " + html_safe(reason),
                    body_style,
                )
            )

    if safety.get(
        "requires_expert",
        False,
    ):
        story.append(
            Paragraph(
                "<b>Human expert review is required before "
                "high-impact action.</b>",
                warning_style,
            )
        )

    # ========================================================
    # 9. OPTIONS
    # ========================================================

    story.append(
        Paragraph(
            "9. Cost & Affordability Pathways",
            section_style,
        )
    )

    options = case_data.get(
        "options",
        {},
    )

    pathways = options.get(
        "pathways",
        [],
    ) if isinstance(options, dict) else []

    if pathways:

        for pathway in pathways:

            pathway_name = pathway.get(
                "name",
                "Option",
            )

            if pathway_name == "Best Value":
                display_name = "BEST VALUE"
            else:
                display_name = pathway_name.upper()

            story.append(
                Paragraph(
                    f"<b>{html_safe(display_name)}</b>",
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    "<b>Estimated cost:</b> "
                    + html_safe(
                        safe_money(
                            pathway.get(
                                "estimated_cost_pkr",
                                0,
                            )
                        )
                    )
                    + "<br/>"
                    + "<b>Expected effectiveness:</b> "
                    + html_safe(
                        pathway.get(
                            "effectiveness",
                            "",
                        )
                    )
                    + "<br/>"
                    + "<b>Evidence strength:</b> "
                    + html_safe(
                        pathway.get(
                            "evidence_strength",
                            "",
                        )
                    )
                    + "<br/>"
                    + "<b>Tradeoff:</b> "
                    + html_safe(
                        pathway.get(
                            "tradeoff",
                            "",
                        )
                    ),
                    body_style,
                )
            )

            actions = pathway.get(
                "actions",
                [],
            )

            if actions:

                story.append(
                    Paragraph(
                        "<b>Actions</b>",
                        body_style,
                    )
                )

                for action in actions:

                    story.append(
                        Paragraph(
                            "• " + html_safe(action),
                            body_style,
                        )
                    )

            accessibility = pathway.get(
                "accessibility",
                "",
            )

            if accessibility:

                story.append(
                    Paragraph(
                        "<b>Accessibility:</b> "
                        + html_safe(accessibility),
                        body_style,
                    )
                )

            affordable = pathway.get(
                "affordable",
                None,
            )

            if affordable is not None:

                story.append(
                    Paragraph(
                        "<b>Within entered budget:</b> "
                        + (
                            "Yes"
                            if affordable
                            else "No"
                        ),
                        body_style,
                    )
                )

            finance = pathway.get(
                "finance",
                {},
            )

            if finance:

                remaining_budget = finance.get(
                    "remaining_budget",
                    0,
                )

                break_even = finance.get(
                    "break_even_value",
                    0,
                )

                story.append(
                    Paragraph(
                        "<b>Remaining budget:</b> "
                        + html_safe(
                            safe_money(
                                remaining_budget
                            )
                        )
                        + "<br/>"
                        + "<b>Break-even direct value:</b> "
                        + html_safe(
                            safe_money(
                                break_even
                            )
                        ),
                        body_style,
                    )
                )

            story.append(
                Spacer(
                    1,
                    6,
                )
            )

    else:
        story.append(
            Paragraph(
                "No affordability pathways are available.",
                body_style,
            )
        )

    story.append(
        Paragraph(
            "Cost values are planning estimates and should not be interpreted "
            "as current market quotations. NabatAI does not make unsupported "
            "yield or ROI claims.",
            small_style,
        )
    )

    # ========================================================
    # 10. EXPERT REVIEW
    # ========================================================

    story.append(
        Paragraph(
            "10. Human Expert Review",
            section_style,
        )
    )

    expert_review = case_data.get(
        "expert_review",
        {},
    )

    requires_expert = safety.get(
        "requires_expert",
        False,
    )

    if expert_review:

        decision = expert_review.get(
            "decision",
            "Not recorded",
        )

        note = expert_review.get(
            "note",
            "",
        )

        story.append(
            Paragraph(
                "<b>Decision:</b> "
                + html_safe(decision),
                body_style,
            )
        )

        if note:
            story.append(
                Paragraph(
                    "<b>Expert note:</b> "
                    + html_safe(note),
                    body_style,
                )
            )

        modified_recommendation = expert_review.get(
            "modified_recommendation",
            "",
        )

        if modified_recommendation:
            story.append(
                Paragraph(
                    "<b>Modified recommendation:</b> "
                    + html_safe(modified_recommendation),
                    body_style,
                )
            )

        additional_test = expert_review.get(
            "additional_test",
            "",
        )

        if additional_test:
            story.append(
                Paragraph(
                    "<b>Additional evidence requested:</b> "
                    + html_safe(additional_test),
                    body_style,
                )
            )

    elif requires_expert:

        story.append(
            Paragraph(
                "<b>Status: PENDING EXPERT REVIEW</b><br/>"
                "The Safety Agent has identified this case as requiring "
                "human review. High-impact recommendations should not be "
                "treated as approved until a qualified expert reviews them.",
                warning_style,
            )
        )

    else:

        story.append(
            Paragraph(
                "No mandatory expert review is currently recorded for "
                "this case.",
                body_style,
            )
        )

    # ========================================================
    # 11. CROPCARE PLAN
    # ========================================================

    story.append(
        Paragraph(
            "11. CropCare Action Plan",
            section_style,
        )
    )

    plan = case_data.get(
        "plan",
        {},
    )

    periods = [
        "Today",
        "Next 7 Days",
        "Next 30 Days",
        "Next Crop Stage",
        "Harvest / End of Season",
        "Next Season",
    ]

    for period in periods:

        actions = plan.get(
            period,
            [],
        )

        if not actions:
            continue

        story.append(
            Paragraph(
                f"<b>{html_safe(period)}</b>",
                body_style,
            )
        )

        for action in actions:

            if isinstance(action, dict):

                action_text = action.get(
                    "action",
                    "Action",
                )

                cost = action.get(
                    "cost_pkr",
                    0,
                )

                priority = action.get(
                    "priority",
                    "",
                )

                checkpoint = action.get(
                    "checkpoint",
                    "",
                )

                story.append(
                    Paragraph(
                        "• <b>"
                        + html_safe(action_text)
                        + "</b><br/>"
                        + "Estimated cost: "
                        + html_safe(
                            safe_money(cost)
                        )
                        + " | Priority: "
                        + html_safe(priority)
                        + " | Follow-up: "
                        + html_safe(checkpoint),
                        body_style,
                    )
                )

            else:

                story.append(
                    Paragraph(
                        "• " + html_safe(action),
                        body_style,
                    )
                )

        story.append(
            Spacer(
                1,
                4,
            )
        )

    estimated_plan_cost = plan.get(
        "estimated_plan_cost_pkr",
        0,
    )

    story.append(
        Paragraph(
            "<b>Estimated selected-plan cost:</b> "
            + html_safe(
                safe_money(
                    estimated_plan_cost
                )
            ),
            body_style,
        )
    )

    # ========================================================
    # 12. REFERENCES
    # ========================================================

    references = case_data.get(
        "references",
        [],
    )

    story.append(
        Paragraph(
            "12. Evidence & References",
            section_style,
        )
    )

    if references:

        for index, reference in enumerate(
            references,
            start=1,
        ):

            if isinstance(reference, str):

                story.append(
                    Paragraph(
                        f"{index}. "
                        + html_safe(reference),
                        small_style,
                    )
                )

                continue

            title = reference.get(
                "title",
                "Reference",
            )

            organization = (
                reference.get("organization")
                or reference.get("journal")
                or ""
            )

            year = reference.get(
                "year",
                "",
            )

            evidence_tier = reference.get(
                "evidence_tier",
                reference.get(
                    "tier",
                    "",
                ),
            )

            relevance = reference.get(
                "relevance_summary",
                reference.get(
                    "relevance",
                    "",
                ),
            )

            limitation = reference.get(
                "limitation",
                "",
            )

            url = reference.get(
                "url",
                "",
            )

            reference_text = (
                f"<b>{index}. {html_safe(title)}</b>"
            )

            if organization:
                reference_text += (
                    "<br/>"
                    + html_safe(organization)
                )

            if year:
                reference_text += (
                    " ("
                    + html_safe(year)
                    + ")"
                )

            if evidence_tier:
                reference_text += (
                    "<br/><b>Evidence tier:</b> "
                    + html_safe(evidence_tier)
                )

            if relevance:
                reference_text += (
                    "<br/><b>Relevance:</b> "
                    + html_safe(relevance)
                )

            if limitation:
                reference_text += (
                    "<br/><b>Limitation:</b> "
                    + html_safe(limitation)
                )

            if url:
                reference_text += (
                    "<br/><b>Source:</b> "
                    + html_safe(url)
                )

            story.append(
                Paragraph(
                    reference_text,
                    small_style,
                )
            )

            story.append(
                Spacer(
                    1,
                    5,
                )
            )

    else:

        story.append(
            Paragraph(
                "No validated reference is currently attached to "
                "this exported case.",
                small_style,
            )
        )

    # ========================================================
    # FINAL NOTICE
    # ========================================================

    story.append(
        Spacer(
            1,
            14,
        )
    )

    story.append(
        Paragraph(
            "<b>NabatAI Responsible AI Notice</b><br/>"
            "NabatAI provides agricultural decision support rather than "
            "a guaranteed diagnosis. Laboratory results, local weather, "
            "soil conditions, crop stage, management practices and future "
            "observations may change the recommendation. High-risk crop, "
            "chemical, biotechnology and financial decisions should be "
            "reviewed by qualified local professionals.",
            warning_style,
        )
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()

    buffer.close()

    return pdf_bytes


# ============================================================
# PAGE
# ============================================================

st.title("🌱 5 · CropCare Plan")

st.caption(
    "Your evidence-based action plan, financial schedule, "
    "human-review status and downloadable case report."
)


# ============================================================
# LOAD SESSION DATA
# ============================================================

profile = st.session_state.get(
    "profile",
    {},
)

plan = st.session_state.get(
    "plan",
)

latest_assessment = get_latest_assessment()


# ============================================================
# REQUIRE PLAN
# ============================================================

if not plan:
    st.warning(
        "No CropCare plan is available yet. "
        "Please build your recommendation options first."
    )

    if st.button(
        "← Go to Compare Options",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/4_options.py"
        )

    st.stop()


# ============================================================
# SAFETY / EXPERT STATUS
# ============================================================

safety = latest_assessment.get(
    "safety",
    {},
)

safety_level = safety.get(
    "level",
    "YELLOW",
)

requires_expert = safety.get(
    "requires_expert",
    False,
)

expert_review = st.session_state.get(
    "expert_review",
    {},
)


if safety_level == "RED":

    st.error(
        "🔴 Human review required — this case contains "
        "a potentially high-impact or uncertain decision."
    )

elif safety_level == "YELLOW":

    st.warning(
        "🟡 Proceed cautiously — evidence or follow-up may "
        "still be required before higher-impact decisions."
    )

else:

    st.success(
        "🟢 Current guidance is classified as lower risk."
    )


if requires_expert and not expert_review:

    st.info(
        "This case has not yet been approved by an expert. "
        "You may still download the report, but it will be "
        "marked as **Pending Expert Review**."
    )

    if st.button(
        "🧑‍🌾 Open Expert Mode",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_expert_mode.py"
        )


elif expert_review:

    decision = expert_review.get(
        "decision",
        "Recorded",
    )

    st.success(
        f"Expert review recorded: **{decision}**"
    )


# ============================================================
# CROP SUMMARY
# ============================================================

st.subheader("Case Summary")

summary_col1, summary_col2, summary_col3 = st.columns(
    3
)

with summary_col1:

    st.metric(
        "Crop",
        safe_text(
            profile.get(
                "crop",
                "Not provided",
            )
        ),
    )

with summary_col2:

    location = (
        profile.get("district")
        or profile.get("location")
        or "Not provided"
    )

    st.metric(
        "Location",
        safe_text(location),
    )

with summary_col3:

    st.metric(
        "Available Budget",
        pkr(
            profile.get(
                "budget",
                0,
            )
        ),
    )


# ============================================================
# ACTION PLAN
# ============================================================

st.divider()

st.subheader("📅 CropCare Action Plan")

periods = [
    "Today",
    "Next 7 Days",
    "Next 30 Days",
    "Next Crop Stage",
    "Harvest / End of Season",
    "Next Season",
]

for period in periods:

    actions = plan.get(
        period,
        [],
    )

    if not actions:
        continue

    st.markdown(
        f"### {period}"
    )

    for action in actions:

        if isinstance(action, dict):

            action_text = action.get(
                "action",
                "Action",
            )

            cost = action.get(
                "cost_pkr",
                0,
            )

            priority = action.get(
                "priority",
                "Not specified",
            )

            checkpoint = action.get(
                "checkpoint",
                "Not specified",
            )

            with st.container(
                border=True
            ):

                st.write(
                    f"**{action_text}**"
                )

                col_a, col_b, col_c = st.columns(
                    3
                )

                with col_a:
                    st.caption(
                        f"💰 Estimated cost: {pkr(cost)}"
                    )

                with col_b:
                    st.caption(
                        f"🎯 Priority: {priority}"
                    )

                with col_c:
                    st.caption(
                        f"🔄 Follow-up: {checkpoint}"
                    )

        else:

            with st.container(
                border=True
            ):
                st.write(
                    f"**{safe_text(action)}**"
                )


# ============================================================
# PLAN COST
# ============================================================

st.divider()

estimated_plan_cost = plan.get(
    "estimated_plan_cost_pkr",
    0,
)

cost_col1, cost_col2 = st.columns(
    2
)

with cost_col1:

    st.metric(
        "Estimated Selected-Plan Cost",
        pkr(
            estimated_plan_cost
        ),
    )

with cost_col2:

    budget = float(
        profile.get(
            "budget",
            0,
        )
        or 0
    )

    remaining_budget = (
        budget
        - float(
            estimated_plan_cost
            or 0
        )
    )

    st.metric(
        "Estimated Budget Remaining",
        pkr(
            remaining_budget
        ),
    )


st.caption(
    "Costs are editable planning estimates and are not "
    "presented as current market quotations."
)


# ============================================================
# FOLLOW-UP NOTICE
# ============================================================

st.info(
    "Laboratory results, weather, field conditions and crop "
    "response may change this plan. Re-evaluate the case "
    "whenever meaningful new evidence becomes available."
)


# ============================================================
# EXPORT CASE
# ============================================================

st.divider()

st.subheader("📥 Export Your Case")

st.write(
    "Download the **PDF report** for reading/sharing, "
    "or save the **JSON case file** so the case can be "
    "uploaded later and continued without an account."
)


case_export = build_case_export()


# ------------------------------------------------------------
# JSON
# ------------------------------------------------------------

json_bytes = json.dumps(
    case_export,
    indent=2,
    ensure_ascii=False,
    default=str,
).encode(
    "utf-8"
)


# ------------------------------------------------------------
# PDF
# ------------------------------------------------------------

pdf_bytes = None
pdf_error = None

if REPORTLAB_AVAILABLE:

    try:
        pdf_bytes = generate_case_pdf(
            case_export
        )

    except Exception as exc:
        pdf_error = str(exc)

else:

    pdf_error = (
        "ReportLab is not installed. Add "
        "`reportlab>=4.2.0` to requirements.txt."
    )


if pdf_error:

    st.error(
        f"PDF generation is unavailable: {pdf_error}"
    )


# ------------------------------------------------------------
# DOWNLOAD BUTTONS
# ------------------------------------------------------------

download_col1, download_col2 = st.columns(
    2
)

with download_col1:

    st.download_button(
        label="📄 Download Full PDF Report",
        data=(
            pdf_bytes
            if pdf_bytes
            else b""
        ),
        file_name="NabatAI_Crop_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
        disabled=pdf_bytes is None,
    )


with download_col2:

    st.download_button(
        label="💾 Download Case JSON",
        data=json_bytes,
        file_name="nabat_case.json",
        mime="application/json",
        use_container_width=True,
    )


# ============================================================
# WHAT EACH FILE IS FOR
# ============================================================

with st.expander(
    "What is the difference between PDF and JSON?"
):

    st.markdown(
        """
**PDF Report**

Use this for:

- farmer/grower records
- sharing with an agronomist or plant expert
- hackathon demonstration
- printing
- management review
- reviewing the assessment and CropCare plan

**Case JSON**

Use this for:

- saving the complete NabatAI case
- uploading it again later
- continuing the same crop case
- re-evaluating when new evidence becomes available

The JSON file acts as the portable case memory because
NabatAI does not require a permanent user database.
"""
    )


# ============================================================
# RESPONSIBLE AI NOTICE
# ============================================================

st.divider()

st.caption(
    "NabatAI provides decision support, not guaranteed diagnosis. "
    "Critical agricultural and financial decisions should be "
    "confirmed with qualified local professionals. Laboratory "
    "results and local agronomic conditions may change recommendations."
)
