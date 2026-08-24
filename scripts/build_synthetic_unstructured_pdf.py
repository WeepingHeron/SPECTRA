#!/usr/bin/env python3
"""Build a realistic synthetic radiation-report PDF and its demo ground truth."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/spectra_synthetic_unstructured_radiation_report.pdf"
GROUND_TRUTH = ROOT / "demo/data/synthetic-unstructured-ground-truth.json"
PAGE_W, PAGE_H = A4

INK = colors.HexColor("#171717")
MUTED = colors.HexColor("#666666")
LINE = colors.HexColor("#B8B8B8")
PAPER = colors.HexColor("#F7F6F1")
ACCENT = colors.HexColor("#0B6B50")
ALERT = colors.HexColor("#A63D2F")


def register_fonts() -> tuple[str, str]:
    regular = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("SpectraArial", str(regular)))
        pdfmetrics.registerFont(TTFont("SpectraArialBold", str(bold)))
        return "SpectraArial", "SpectraArialBold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()
STYLES = getSampleStyleSheet()
BODY = ParagraphStyle(
    "Body",
    parent=STYLES["BodyText"],
    fontName=FONT,
    fontSize=8.6,
    leading=12.2,
    textColor=INK,
    alignment=TA_LEFT,
)
SMALL = ParagraphStyle(
    "Small", parent=BODY, fontSize=7.2, leading=9.4, textColor=MUTED
)


def footer(c: canvas.Canvas, page: int, label: str) -> None:
    c.setStrokeColor(LINE)
    c.line(18 * mm, 15 * mm, PAGE_W - 18 * mm, 15 * mm)
    c.setFont(FONT, 6.8)
    c.setFillColor(MUTED)
    c.drawString(18 * mm, 10.2 * mm, "SYNTHETIC TRAINING DOCUMENT - NOT A REAL TEST REPORT")
    c.drawRightString(PAGE_W - 18 * mm, 10.2 * mm, f"{label}  |  {page} / 4")


def banner(c: canvas.Canvas) -> None:
    c.saveState()
    c.setFillColor(colors.HexColor("#EEE7D5"))
    c.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, fill=1, stroke=0)
    c.setFillColor(ALERT)
    c.setFont(FONT_BOLD, 8)
    c.drawCentredString(
        PAGE_W / 2,
        PAGE_H - 8.2 * mm,
        "SYNTHETIC TRAINING ARTIFACT / VALUES ARE NOT ENGINEERING EVIDENCE",
    )
    c.restoreState()


def paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float, style=BODY) -> float:
    item = Paragraph(text, style)
    _, height = item.wrap(width, PAGE_H)
    item.drawOn(c, x, y - height)
    return y - height


def page_one(c: canvas.Canvas) -> None:
    banner(c)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 9)
    c.drawString(18 * mm, PAGE_H - 26 * mm, "NORTHSTAR ORBITAL LABS / COMPONENT ASSURANCE")
    c.setFont(FONT_BOLD, 27)
    c.drawString(18 * mm, PAGE_H - 48 * mm, "Radiation Test Evidence")
    c.drawString(18 * mm, PAGE_H - 60 * mm, "Candidate Review Package")
    c.setFillColor(ACCENT)
    c.setFont(FONT_BOLD, 11)
    c.drawString(18 * mm, PAGE_H - 72 * mm, "DOCUMENT STR-24-081 / REV A")

    data = [
        ["FIELD", "REPORTED VALUE", "REVIEW NOTE"],
        ["Manufacturer", "Texas Instruments", "String found in supplier block"],
        ["Orderable part", "5962L1420901VXC", "Candidate only; BOM not attached"],
        ["Package / lot", "CFP / not stated", "Identity remains incomplete"],
        ["Mission use", "LEO avionics candidate", "No approved mission linkage"],
    ]
    table = Table(data, colWidths=[34 * mm, 55 * mm, 75 * mm], rowHeights=[9 * mm] + [12 * mm] * 4)
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), FONT, 8),
                ("FONT", (0, 0), (-1, 0), FONT_BOLD, 7),
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#ECEBE5")),
            ]
        )
    )
    table.wrapOn(c, 164 * mm, 70 * mm)
    table.drawOn(c, 18 * mm, PAGE_H - 136 * mm)

    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 12)
    c.drawString(18 * mm, PAGE_H - 154 * mm, "Executive review note")
    paragraph(
        c,
        "This package consolidates excerpts supplied for a <b>TID</b> screening discussion. "
        "It is intentionally incomplete: the approved bill of materials, die traceability, "
        "lot acceptance record, and mission-specific applicability statement are absent.",
        18 * mm,
        PAGE_H - 160 * mm,
        112 * mm,
    )

    c.setFillColor(colors.HexColor("#F0E9D7"))
    c.roundRect(139 * mm, PAGE_H - 194 * mm, 53 * mm, 43 * mm, 2 * mm, fill=1, stroke=0)
    c.setFillColor(ALERT)
    c.setFont(FONT_BOLD, 8)
    c.drawString(145 * mm, PAGE_H - 162 * mm, "REVIEW BOUNDARY")
    paragraph(
        c,
        "No suitability decision. No approved target comparison. Destructive SEE coverage is unresolved.",
        145 * mm,
        PAGE_H - 169 * mm,
        41 * mm,
        SMALL,
    )

    c.saveState()
    c.translate(157 * mm, 50 * mm)
    c.rotate(8)
    c.setStrokeColor(ALERT)
    c.setFillColor(ALERT)
    c.setLineWidth(1.5)
    c.rect(-27 * mm, -8 * mm, 54 * mm, 16 * mm, fill=0, stroke=1)
    c.setFont(FONT_BOLD, 11)
    c.drawCentredString(0, -1.2 * mm, "NOT FOR DECISION")
    c.restoreState()
    footer(c, 1, "COVER / CONTROLLED COPY")


def page_two(c: canvas.Canvas) -> None:
    banner(c)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 18)
    c.drawString(18 * mm, PAGE_H - 28 * mm, "1. Test narrative and extracted conditions")
    c.setFont(FONT_BOLD, 9)
    c.setFillColor(ACCENT)
    c.drawString(18 * mm, PAGE_H - 39 * mm, "LEFT COLUMN / SOURCE NARRATIVE")
    y = PAGE_H - 46 * mm
    y = paragraph(
        c,
        "The source memo describes room-temperature irradiation of biased devices. "
        "Dose points were recorded by the test operator, but the facility certificate and "
        "dosimetry chain are not included in this package.",
        18 * mm,
        y,
        80 * mm,
    )
    y -= 6 * mm
    y = paragraph(
        c,
        "A functional check was reportedly performed after each exposure. The narrative "
        "mentions <b>SEU</b> behavior only as a follow-up topic; no event cross-section table "
        "or beam species record is attached.",
        18 * mm,
        y,
        80 * mm,
    )
    y -= 8 * mm
    c.setFont(FONT_BOLD, 9)
    c.setFillColor(INK)
    c.drawString(18 * mm, y, "Operator note (transcribed)")
    y -= 5 * mm
    paragraph(
        c,
        "\"Electrical parameters remained within the synthetic acceptance band. "
        "This sentence is training content and must not be interpreted as a published result.\"",
        21 * mm,
        y,
        74 * mm,
        SMALL,
    )

    c.setStrokeColor(LINE)
    c.line(105 * mm, 30 * mm, 105 * mm, PAGE_H - 43 * mm)
    c.setFillColor(ACCENT)
    c.setFont(FONT_BOLD, 9)
    c.drawString(113 * mm, PAGE_H - 39 * mm, "RIGHT COLUMN / SYNTHETIC PLOT")
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 11)
    c.drawString(113 * mm, PAGE_H - 49 * mm, "Normalized response vs. dose step")
    x0, y0, w, h = 117 * mm, PAGE_H - 122 * mm, 67 * mm, 54 * mm
    c.setStrokeColor(INK)
    c.line(x0, y0, x0, y0 + h)
    c.line(x0, y0, x0 + w, y0)
    points = [(0, 0.91), (0.2, 0.89), (0.45, 0.86), (0.72, 0.84), (1.0, 0.80)]
    c.setStrokeColor(ACCENT)
    c.setFillColor(ACCENT)
    last = None
    for px, py in points:
        point = (x0 + px * w, y0 + py * h)
        if last:
            c.line(last[0], last[1], point[0], point[1])
        c.circle(point[0], point[1], 1.2 * mm, fill=1, stroke=0)
        last = point
    c.setFillColor(MUTED)
    c.setFont(FONT, 6.5)
    c.drawString(x0, y0 - 5 * mm, "dose step (synthetic)")
    c.saveState()
    c.translate(x0 - 7 * mm, y0 + 8 * mm)
    c.rotate(90)
    c.drawString(0, 0, "normalized response")
    c.restoreState()
    paragraph(
        c,
        "Figure 1. Layout-realistic training graphic. Values are deliberately non-authoritative and are excluded from SPECTRA decision input.",
        113 * mm,
        PAGE_H - 135 * mm,
        74 * mm,
        SMALL,
    )

    c.setFillColor(colors.HexColor("#ECEBE5"))
    c.rect(113 * mm, 43 * mm, 74 * mm, 38 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 8)
    c.drawString(118 * mm, 73 * mm, "MISSING ATTACHMENTS")
    paragraph(
        c,
        "A. facility certificate<br/>B. raw measurement file<br/>C. approved test plan<br/>D. mission applicability review",
        118 * mm,
        68 * mm,
        62 * mm,
        SMALL,
    )
    footer(c, 2, "TECHNICAL NARRATIVE")


def page_three(c: canvas.Canvas) -> None:
    banner(c)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 18)
    c.drawString(18 * mm, PAGE_H - 28 * mm, "2. Single-event effects coverage matrix")
    paragraph(
        c,
        "The matrix below preserves the distinction between a term appearing in a document "
        "and evidence that actually closes a coverage requirement.",
        18 * mm,
        PAGE_H - 36 * mm,
        160 * mm,
    )
    data = [
        ["EVENT", "DOCUMENT STATEMENT", "ATTACHMENT", "REVIEW STATE"],
        ["SEL", "Referenced in planning notes", "None", "UNRESOLVED"],
        ["SEB", "Not tested; destructive setup absent", "None", "GAP"],
        ["SEGR", "Not tested; gate-stress record absent", "None", "GAP"],
        ["Cross-section", "No fluence-normalized result", "None", "DATA UNAVAILABLE"],
    ]
    table = Table(data, colWidths=[22 * mm, 78 * mm, 30 * mm, 42 * mm], rowHeights=[10 * mm] + [15 * mm] * 4)
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), FONT, 8),
                ("FONT", (0, 0), (-1, 0), FONT_BOLD, 7),
                ("FONT", (0, 1), (0, -1), FONT_BOLD, 9),
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (3, 1), (3, -1), colors.HexColor("#F0E9D7")),
                ("TEXTCOLOR", (3, 1), (3, -1), ALERT),
            ]
        )
    )
    table.wrapOn(c, 172 * mm, 75 * mm)
    table.drawOn(c, 18 * mm, PAGE_H - 126 * mm)

    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 12)
    c.drawString(18 * mm, PAGE_H - 146 * mm, "Reviewer interpretation")
    paragraph(
        c,
        "The appearance of an event acronym is a locator candidate, not proof of a test result. "
        "SEU information cannot replace destructive-event coverage. The package therefore "
        "remains unsuitable for an assurance decision.",
        18 * mm,
        PAGE_H - 153 * mm,
        112 * mm,
    )
    c.setFillColor(colors.HexColor("#F0E9D7"))
    c.roundRect(140 * mm, PAGE_H - 190 * mm, 50 * mm, 45 * mm, 2 * mm, fill=1, stroke=0)
    c.setFillColor(ALERT)
    c.setFont(FONT_BOLD, 8)
    c.drawString(146 * mm, PAGE_H - 156 * mm, "FAIL-CLOSED RESULT")
    c.setFont(FONT_BOLD, 20)
    c.drawString(146 * mm, PAGE_H - 169 * mm, "HOLD")
    paragraph(c, "Coverage gaps remain explicit.", 146 * mm, PAGE_H - 176 * mm, 38 * mm, SMALL)
    footer(c, 3, "COVERAGE MATRIX")


def page_four(c: canvas.Canvas) -> None:
    banner(c)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 18)
    c.drawString(18 * mm, PAGE_H - 28 * mm, "Appendix A. Evidence locator index")
    rows = [
        ["LOCATOR", "PAGE", "WHAT A REVIEWER CAN CONFIRM"],
        ["supplier-block", "1", "Manufacturer string and candidate part string"],
        ["tid-narrative", "1", "TID acronym occurs in an incomplete review note"],
        ["seu-follow-up", "2", "SEU acronym occurs without a result table"],
        ["destructive-see", "3", "SEL / SEB / SEGR appear as unresolved coverage"],
    ]
    table = Table(rows, colWidths=[42 * mm, 18 * mm, 112 * mm], rowHeights=[10 * mm] + [15 * mm] * 4)
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), FONT, 8),
                ("FONT", (0, 0), (-1, 0), FONT_BOLD, 7),
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    table.wrapOn(c, 172 * mm, 75 * mm)
    table.drawOn(c, 18 * mm, PAGE_H - 112 * mm)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 12)
    c.drawString(18 * mm, PAGE_H - 135 * mm, "Document control and limitations")
    y = PAGE_H - 143 * mm
    for number, text in enumerate(
        [
            "This file is generated solely to test document parsing and evidence gating.",
            "Northstar Orbital Labs is fictional; no affiliation or certification is claimed.",
            "All plotted values and conditions are synthetic and must not enter engineering calculations.",
            "The expected extraction targets are published in a separate machine-readable ground-truth file.",
        ],
        start=1,
    ):
        c.setFont(FONT_BOLD, 8)
        c.drawString(20 * mm, y, f"{number:02d}")
        y = paragraph(c, text, 31 * mm, y + 2 * mm, 145 * mm, BODY) - 6 * mm
    c.setFillColor(ACCENT)
    c.setFont(FONT_BOLD, 10)
    c.drawString(18 * mm, 45 * mm, "END OF SYNTHETIC TRAINING ARTIFACT")
    footer(c, 4, "APPENDIX")


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    GROUND_TRUTH.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1, invariant=1)
    c.setTitle("SPECTRA Synthetic Unstructured Radiation Report")
    c.setAuthor("SPECTRA synthetic demo generator")
    c.setSubject("Synthetic training artifact; not engineering evidence")
    for draw_page in (page_one, page_two, page_three, page_four):
        c.setFillColor(PAPER)
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        draw_page(c)
        c.showPage()
    c.save()

    ground_truth = {
        "contract_version": "SYNTHETIC_UNSTRUCTURED_GROUND_TRUTH_1.0.0",
        "source_classification": "SYNTHETIC_CONTROL",
        "filename": OUTPUT.name,
        "expected_part": "5962L1420901VXC",
        "manufacturer": "Texas Instruments",
        "expected_candidates": [
            {"field": "ORDERABLE_PART_NUMBER", "value": "5962L1420901VXC", "page": 1},
            {"field": "MANUFACTURER", "value": "Texas Instruments", "page": 1},
            {"field": "EVIDENCE_EVENT_MENTION", "value": "TID", "page": 1},
            {"field": "EVIDENCE_EVENT_MENTION", "value": "SEU", "page": 2},
            {"field": "EVIDENCE_EVENT_MENTION", "value": "SEL", "page": 3},
            {"field": "EVIDENCE_EVENT_MENTION", "value": "SEB", "page": 3},
            {"field": "EVIDENCE_EVENT_MENTION", "value": "SEGR", "page": 3},
        ],
        "expected_decision": "HOLD",
        "expected_blocker": "APPROVED_BOM_TARGET_MISSING",
        "comparison_scope": "EXACT_EXPECTED_CANDIDATE_SET_ONLY",
        "not_claimed": [
            "SCIENTIFIC_ACCURACY",
            "OCR_ACCURACY",
            "REAL_DOCUMENT_GENERALIZATION",
            "RADIATION_ASSURANCE",
        ],
    }
    GROUND_TRUTH.write_text(
        json.dumps(ground_truth, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    build()
