from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def _safe(value, default="Not provided"):
    if value is None or value == "":
        return default
    return str(value)


def _money(value):
    try:
        return f"Rs. {float(value):,.0f}"
    except (TypeError, ValueError):
        return "Not available"


def generate_case_pdf(case_data: dict) -> bytes:
    """
    Generate complete NabatAI human-readable PDF report.
    Nothing is written to disk.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="NabatAI Crop Decision Support Report",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "NabatTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=body_style,
        fontSize=8,
        leading=11,
        textColor=colors.grey,
    )

    story = []

    # -------------------------------------------------
    # COVER
    # -------------------------------------------------

    story.append(Paragraph("NabatAI", title_style))
    story.append(
        Paragraph(
            "Evidence-Based Plant Biotechnology & Crop Decision Support",
            styles["Heading3"],
        )
    )

    story.append(Spacer(1, 10))

    profile = case_data.get("profile", {})

    crop = profile.get("crop", "Crop case")
    location = profile.get("location", profile.get("district", ""))

    story.append(
        Paragraph(
            f"<b>Crop:</b> {_safe(crop)}<br/>"
            f"<b>Location:</b> {_safe(location)}",
            body_style,
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>Important:</b> NabatAI provides decision support, "
            "not guaranteed diagnosis. Critical agricultural and financial "
            "decisions should be confirmed with qualified local professionals.",
            small_style,
        )
    )

    story.append(PageBreak())

    # -------------------------------------------------
    # 1. CASE PROFILE
    # -------------------------------------------------

    story.append(Paragraph("1. Crop & Farmer Profile", section_style))

    profile_rows = [
        ["Crop", _safe(profile.get("crop"))],
        ["Variety", _safe(profile.get("variety"))],
        ["Location", _safe(profile.get("location", profile.get("district")))],
        ["Area", f"{_safe(profile.get('area'))} {_safe(profile.get('area_unit'), '')}"],
        ["Crop Age", _safe(profile.get("crop_age"))],
        ["Growth Stage", _safe(profile.get("growth_stage"))],
        ["Irrigation", _safe(profile.get("irrigation_source"))],
        ["Available Budget", _money(profile.get("budget"))],
        ["Expected Crop Value", _money(profile.get("expected_crop_value"))],
    ]

    table = Table(profile_rows, colWidths=[50 * mm, 115 * mm])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF4EA")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(table)

    # -------------------------------------------------
    # PROBLEM
    # -------------------------------------------------

    story.append(Paragraph("2. Reported Problem", section_style))

    problem = (
        case_data.get("problem_description")
        or profile.get("problem_description")
        or profile.get("problem")
    )

    story.append(Paragraph(_safe(problem), body_style))

    # -------------------------------------------------
    # FIRST ASSESSMENT
    # -------------------------------------------------

    first = case_data.get("first_assessment", {})

    story.append(Paragraph("3. Initial AI Assessment", section_style))

    summary = first.get("summary", first.get("preliminary_assessment"))

    if summary:
        story.append(Paragraph(_safe(summary), body_style))

    hypotheses = first.get("hypotheses", [])

    if hypotheses:
        rows = [["Possible Cause", "Confidence", "Reason"]]

        for item in hypotheses:
            rows.append(
                [
                    _safe(item.get("name", item.get("hypothesis"))),
                    _safe(item.get("confidence")),
                    _safe(item.get("reason", item.get("reasoning"))),
                ]
            )

        table = Table(
            rows,
            colWidths=[45 * mm, 28 * mm, 92 * mm],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEEDD")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        story.append(table)

    # -------------------------------------------------
    # SKEPTIC FINDINGS
    # -------------------------------------------------

    skeptic = first.get("skeptic", {})

    if skeptic:
        story.append(Paragraph("4. Skeptic Review & Uncertainty", section_style))

        for key in [
            "competing_explanations",
            "missing_evidence",
            "unsupported_assumptions",
            "contradictions",
        ]:
            values = skeptic.get(key, [])

            if values:
                story.append(
                    Paragraph(
                        f"<b>{key.replace('_', ' ').title()}</b>",
                        body_style,
                    )
                )

                for value in values:
                    story.append(
                        Paragraph(f"• {_safe(value)}", body_style)
                    )

    # -------------------------------------------------
    # TESTS
    # -------------------------------------------------

    tests = case_data.get(
        "requested_tests",
        first.get("recommended_tests", [])
    )

    story.append(Paragraph("5. Recommended Evidence / Tests", section_style))

    if tests:
        rows = [["Test / Check", "Why", "Priority", "Estimated Cost"]]

        for test in tests:
            rows.append(
                [
                    _safe(test.get("name", test.get("test"))),
                    _safe(test.get("why_needed", test.get("reason"))),
                    _safe(test.get("priority")),
                    _money(test.get("estimated_cost_pkr")),
                ]
            )

        table = Table(
            rows,
            colWidths=[38 * mm, 72 * mm, 25 * mm, 30 * mm],
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEEDD")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        story.append(table)

    # -------------------------------------------------
    # CONFIRMED LAB DATA
    # -------------------------------------------------

    confirmed = case_data.get("confirmed_values", {})

    if confirmed:
        story.append(Paragraph("6. Confirmed Laboratory Evidence", section_style))

        rows = [["Parameter", "Confirmed Value"]]

        for key, value in confirmed.items():
            rows.append(
                [
                    key.replace("_", " ").title(),
                    _safe(value),
                ]
            )

        table = Table(rows, colWidths=[70 * mm, 95 * mm])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEEDD")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )

        story.append(table)

    # -------------------------------------------------
    # SECOND ASSESSMENT
    # -------------------------------------------------

    second = case_data.get("second_assessment", {})

    if second:
        story.append(Paragraph("7. Re-Evaluation After Evidence", section_style))

        explanation = second.get(
            "why_assessment_changed",
            second.get("change_explanation"),
        )

        if explanation:
            story.append(
                Paragraph(
                    f"<b>Why did our assessment change?</b><br/>{_safe(explanation)}",
                    body_style,
                )
            )

        hypotheses = second.get("hypotheses", [])

        if hypotheses:
            rows = [["Updated Hypothesis", "Confidence", "Reason"]]

            for item in hypotheses:
                rows.append(
                    [
                        _safe(item.get("name", item.get("hypothesis"))),
                        _safe(item.get("confidence")),
                        _safe(item.get("reason", item.get("reasoning"))),
                    ]
                )

            table = Table(
                rows,
                colWidths=[45 * mm, 28 * mm, 92 * mm],
                repeatRows=1,
            )

            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEEDD")),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )

            story.append(table)

    # -------------------------------------------------
    # DON'T SPEND YET
    # -------------------------------------------------

    latest = second or first

    dont_spend = latest.get("dont_spend_yet", [])

    if dont_spend:
        story.append(Paragraph("8. Don't Spend Yet", section_style))

        for item in dont_spend:
            story.append(
                Paragraph(
                    f"• {_safe(item)}",
                    body_style,
                )
            )

    # -------------------------------------------------
    # OPTIONS
    # -------------------------------------------------

    options = case_data.get("recommendations", case_data.get("options", {}))

    story.append(Paragraph("9. Affordability Options", section_style))

    if isinstance(options, dict):

        for key in [
            "minimum_cost",
            "best_value",
            "comprehensive",
        ]:
            option = options.get(key)

            if not option:
                continue

            story.append(
                Paragraph(
                    f"<b>{key.replace('_', ' ').title()}</b>",
                    body_style,
                )
            )

            story.append(
                Paragraph(
                    f"Estimated cost: <b>{_money(option.get('estimated_cost_pkr'))}</b><br/>"
                    f"Expected effectiveness: {_safe(option.get('effectiveness'))}<br/>"
                    f"Evidence strength: {_safe(option.get('evidence_strength'))}<br/>"
                    f"Main tradeoff: {_safe(option.get('tradeoff', option.get('reason')))}",
                    body_style,
                )
            )

            story.append(Spacer(1, 5))

    # -------------------------------------------------
    # FINANCE
    # -------------------------------------------------

    finance = case_data.get("financial_summary", {})

    if finance:
        story.append(Paragraph("10. Financial Decision Support", section_style))

        rows = [["Metric", "Value"]]

        for key, value in finance.items():
            label = key.replace("_", " ").title()

            if "cost" in key or "budget" in key or "value" in key:
                value = _money(value)

            rows.append([label, _safe(value)])

        table = Table(rows, colWidths=[80 * mm, 85 * mm])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEEDD")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )

        story.append(table)

    # -------------------------------------------------
    # EXPERT REVIEW
    # -------------------------------------------------

    expert = case_data.get("expert_review", {})

    story.append(Paragraph("11. Human Expert Review", section_style))

    if expert:
        story.append(
            Paragraph(
                f"<b>Decision:</b> {_safe(expert.get('decision'))}<br/>"
                f"<b>Expert note:</b> {_safe(expert.get('note'))}",
                body_style,
            )
        )
    else:
        story.append(
            Paragraph(
                "No expert review has been recorded for this session.",
                body_style,
            )
        )

    # -------------------------------------------------
    # CROP PLAN
    # -------------------------------------------------

    plan = case_data.get("plan", {})

    story.append(Paragraph("12. CropCare Action Plan", section_style))

    stages = [
        ("today", "Today"),
        ("next_7_days", "Next 7 Days"),
        ("next_30_days", "Next 30 Days"),
        ("next_growth_stage", "Next Growth Stage"),
        ("harvest", "Harvest / End of Season"),
        ("next_season", "Next Season"),
    ]

    for key, heading in stages:

        value = plan.get(key)

        if not value:
            continue

        story.append(
            Paragraph(
                f"<b>{heading}</b>",
                body_style,
            )
        )

        if isinstance(value, list):
            for action in value:

                if isinstance(action, dict):
                    text = action.get(
                        "action",
                        action.get("description", str(action)),
                    )

                    cost = action.get("estimated_cost_pkr")

                    line = f"• {_safe(text)}"

                    if cost is not None:
                        line += f" — {_money(cost)}"

                    story.append(Paragraph(line, body_style))

                else:
                    story.append(
                        Paragraph(
                            f"• {_safe(action)}",
                            body_style,
                        )
                    )

        else:
            story.append(Paragraph(_safe(value), body_style))

    # -------------------------------------------------
    # REFERENCES
    # -------------------------------------------------

    refs = case_data.get("references", [])

    if refs:
        story.append(Paragraph("13. Evidence & References", section_style))

        for i, ref in enumerate(refs, start=1):

            story.append(
                Paragraph(
                    f"<b>{i}. {_safe(ref.get('title'))}</b><br/>"
                    f"{_safe(ref.get('organization', ref.get('journal')))} "
                    f"({_safe(ref.get('year'))})<br/>"
                    f"Evidence tier: {_safe(ref.get('evidence_tier'))}<br/>"
                    f"Relevance: {_safe(ref.get('relevance_summary'))}<br/>"
                    f"Limitation: {_safe(ref.get('limitation'))}",
                    small_style,
                )
            )

    # -------------------------------------------------
    # FINAL DISCLAIMER
    # -------------------------------------------------

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>NabatAI Responsible AI Notice</b><br/>"
            "NabatAI provides agricultural decision support rather than a "
            "guaranteed diagnosis. Laboratory results, weather, crop stage, "
            "local soil conditions and management practices may change the "
            "appropriate recommendation. High-risk decisions should be "
            "reviewed by qualified local agricultural professionals.",
            small_style,
        )
    )

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
