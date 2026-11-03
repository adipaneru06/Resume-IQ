"""
Resumely AI — PDF Report Generator
Produces a high-fidelity, editorial PDF evaluation report matching the design tokens.
Built with ReportLab.
"""

import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)

# Design Token Colors
PRIMARY = colors.HexColor("#00563E")
SECONDARY = colors.HexColor("#006C4B")
TERTIARY = colors.HexColor("#723D00")
CRITICAL = colors.HexColor("#BA1A1A")
TEXT_PRIMARY = colors.HexColor("#1C1B1B")
TEXT_MUTED = colors.HexColor("#6F7973")
BORDER_HAIRLINE = colors.HexColor("#E6E2DA")
BG_CANVAS = colors.HexColor("#FAF8F4")
BG_CARD = colors.HexColor("#FFFFFF")
BG_GREEN_TINT = colors.HexColor("#EBF5F0")
BG_AMBER_TINT = colors.HexColor("#FEF6EC")
BG_RED_TINT = colors.HexColor("#FDEDED")


def build_custom_stylesheet():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=TEXT_MUTED
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="BodyTextMuted",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MUTED
    ))

    styles.add(ParagraphStyle(
        name="TagStyle",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="ScoreNum",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="ScoreLabel",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=TEXT_MUTED
    ))

    return styles


def generate_pdf_report(record: Dict[str, Any], analysis: Dict[str, Any]) -> bytes:
    """
    Generates a professional multi-page PDF audit report in memory.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = build_custom_stylesheet()
    story = []

    # 1. Header Banner
    story.append(Paragraph("RESUMELY AI", styles["ReportTitle"]))
    story.append(Paragraph("Editorial ATS Resume Diagnostic Audit &amp; Improvement Plan", styles["ReportSubtitle"]))
    story.append(Spacer(1, 6))

    # Meta Table
    filename = record.get("filename", "Uploaded Resume")
    created = record.get("created_at", datetime.now().isoformat())[:10]
    target_role = record.get("target_role") or "General Critique (No target role specified)"

    meta_data = [
        [
            Paragraph(f"<b>Document:</b> {filename}", styles["BodyTextCustom"]),
            Paragraph(f"<b>Evaluation Date:</b> {created}", styles["BodyTextCustom"]),
            Paragraph(f"<b>Target Role:</b> {target_role}", styles["BodyTextCustom"])
        ]
    ]
    meta_table = Table(meta_data, colWidths=[180, 150, 210])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CANVAS),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 2. Key Score Cards Table
    overall_score = analysis.get("overall_score", 0)
    ats_score = analysis.get("ats", {}).get("score", 0)
    job_match = analysis.get("job_match")

    score_cells = [
        [
            Paragraph(f"<b>{overall_score}</b> / 100", styles["ScoreNum"]),
            Paragraph(f"<b>{ats_score}</b> / 100", styles["ScoreNum"]),
        ]
    ]
    labels_row = [
        Paragraph("OVERALL SCORE<br/>Weighted Composite", styles["ScoreLabel"]),
        Paragraph("ATS COMPATIBILITY<br/>Parsability Benchmark", styles["ScoreLabel"]),
    ]

    if job_match:
        score_cells[0].append(Paragraph(f"<b>{job_match.get('percentage', 0)}%</b>", styles["ScoreNum"]))
        labels_row.append(Paragraph("JOB MATCH<br/>Role Alignment Depth", styles["ScoreLabel"]))
        col_w = [180, 180, 180]
    else:
        col_w = [270, 270]

    score_table_data = [score_cells[0], labels_row]
    score_table = Table(score_table_data, colWidths=col_w)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CARD),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # 3. Executive Assessment
    story.append(Paragraph("Executive Assessment Verdict", styles["SectionHeader"]))
    summary_text = analysis.get("summary", "No summary provided.")
    summary_table = Table([[Paragraph(summary_text, styles["BodyTextCustom"])]], colWidths=[540])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CANVAS),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # 4. Section Benchmarks Table
    story.append(Paragraph("Section Benchmarks", styles["SectionHeader"]))
    sections = analysis.get("sections", [])
    sec_rows = [["Section", "Score", "Evaluation & Guidance"]]
    for sec in sections:
        sec_name = sec.get("name", "")
        sec_score = f"{sec.get('score', 0)} / 100"
        sec_desc = sec.get("reasoning", "")
        sec_rows.append([
            Paragraph(f"<b>{sec_name}</b>", styles["BodyTextCustom"]),
            Paragraph(f"<b>{sec_score}</b>", styles["BodyTextCustom"]),
            Paragraph(sec_desc, styles["BodyTextCustom"])
        ])
    sec_table = Table(sec_rows, colWidths=[100, 70, 370])
    sec_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_CANVAS),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sec_table)
    story.append(Spacer(1, 10))

    # 5. Rubric Performance
    story.append(Paragraph("Rubric Criteria Performance (8 Transparent Dimensions)", styles["SectionHeader"]))
    criteria = analysis.get("criteria_scores", [])
    crit_rows = [["Criterion", "Score", "Reasoning"]]
    for c in criteria:
        crit_rows.append([
            Paragraph(f"<b>{c.get('name', '')}</b>", styles["BodyTextCustom"]),
            Paragraph(f"{c.get('score', 0)}/100", styles["BodyTextCustom"]),
            Paragraph(c.get("reasoning", ""), styles["BodyTextCustom"])
        ])
    crit_table = Table(crit_rows, colWidths=[150, 60, 330])
    crit_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_CANVAS),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(crit_table)
    story.append(Spacer(1, 10))

    # 6. Strengths & Weaknesses
    story.append(Paragraph("Strengths &amp; Identified Gaps", styles["SectionHeader"]))
    strengths = analysis.get("strengths", [])
    weaknesses = analysis.get("weaknesses", [])

    st_paras = [Paragraph(f"• {s}", styles["BodyTextCustom"]) for s in strengths]
    wk_paras = [Paragraph(f"• {w}", styles["BodyTextCustom"]) for w in weaknesses]

    sw_data = [
        [Paragraph("<b>Key Strengths to Preserve</b>", styles["TagStyle"]), Paragraph("<b>Gaps to Address</b>", styles["TagStyle"])],
        [st_paras, wk_paras]
    ]
    sw_table = Table(sw_data, colWidths=[270, 270])
    sw_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BG_GREEN_TINT),
        ("BACKGROUND", (1, 0), (1, 0), BG_RED_TINT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(sw_table)
    story.append(Spacer(1, 10))

    # 7. Prioritized Suggestions
    story.append(Paragraph("Prioritized Actionable Suggestions", styles["SectionHeader"]))
    suggestions = analysis.get("suggestions", [])
    sug_rows = [["Priority", "Identified Issue", "Recommended Actionable Fix"]]
    for sug in suggestions:
        prio = sug.get("priority", "medium").upper()
        sug_rows.append([
            Paragraph(f"<b>{prio}</b>", styles["BodyTextCustom"]),
            Paragraph(sug.get("issue", ""), styles["BodyTextCustom"]),
            Paragraph(sug.get("fix", ""), styles["BodyTextCustom"])
        ])
    sug_table = Table(sug_rows, colWidths=[70, 200, 270])
    sug_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG_CANVAS),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sug_table)
    story.append(Spacer(1, 10))

    # 8. Bullet Rewrites
    story.append(Paragraph("Before / After Bullet Point Rewrites", styles["SectionHeader"]))
    bullet_rewrites = analysis.get("bullet_rewrites", [])
    if bullet_rewrites:
        for bw in bullet_rewrites:
            bw_data = [
                [Paragraph("<b>Before (Original):</b>", styles["BodyTextMuted"]), Paragraph(f"<i>\"{bw.get('before', '')}\"</i>", styles["BodyTextCustom"])],
                [Paragraph("<b>After (Rewrite):</b>", styles["TagStyle"]), Paragraph(f"<b>\"{bw.get('after', '')}\"</b>", styles["BodyTextCustom"])],
                [Paragraph("<b>Impact Context:</b>", styles["BodyTextMuted"]), Paragraph(bw.get("why", ""), styles["BodyTextMuted"])]
            ]
            bw_table = Table(bw_data, colWidths=[110, 430])
            bw_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), BG_CANVAS),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(bw_table)
            story.append(Spacer(1, 6))

    # 9. Language Issues
    lang_issues = analysis.get("language_issues", [])
    if lang_issues:
        story.append(Paragraph("Language &amp; Grammar Audit", styles["SectionHeader"]))
        lang_rows = [["Type", "Original Phrasing", "Recommended Correction"]]
        for li in lang_issues:
            lang_rows.append([
                Paragraph(f"<b>{li.get('type', '').upper()}</b>", styles["BodyTextCustom"]),
                Paragraph(f"<strike>{li.get('original', '')}</strike>", styles["BodyTextMuted"]),
                Paragraph(li.get("suggestion", ""), styles["BodyTextCustom"])
            ])
        lang_table = Table(lang_rows, colWidths=[90, 225, 225])
        lang_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BG_CANVAS),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_HAIRLINE),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(lang_table)
        story.append(Spacer(1, 10))

    # Footer Disclaimer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_HAIRLINE, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        "© Resumely AI — Editorial ATS Intelligence Desk. Scores and feedback are advisory benchmarks based on standard recruiting algorithms.",
        styles["BodyTextMuted"]
    ))

    doc.build(story)
    return buffer.getvalue()

