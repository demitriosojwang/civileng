"""
Report Generator — Foundation Design Reports
Generates professional PDF reports from pipeline results.

Phase 2.5: Report Generator
"""

import os
import math
from datetime import datetime
from typing import Optional
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

from app.pipeline.site_to_design import SiteAssessmentPipelineResult


# ─── Font Registration ───
# Use Liberation Serif (metrically equivalent to Times New Roman) and
# Liberation Sans (equivalent to Arial/Helvetica) as these work reliably.
import os as _os

_SERIF_PATH = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
_SANS_PATH = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
_DEJAVU = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

_SERIF_FONT = 'LiberationSerif' if _os.path.exists(_SERIF_PATH) else 'DejaVuSans'
_SANS_FONT = 'LiberationSans' if _os.path.exists(_SANS_PATH) else 'DejaVuSans'

if _os.path.exists(_SERIF_PATH):
    pdfmetrics.registerFont(TTFont('LiberationSerif', _SERIF_PATH))
    registerFontFamily('LiberationSerif', normal='LiberationSerif', bold='LiberationSerif')
if _os.path.exists(_SANS_PATH):
    pdfmetrics.registerFont(TTFont('LiberationSans', _SANS_PATH))
    registerFontFamily('LiberationSans', normal='LiberationSans', bold='LiberationSans')

# Always have DejaVu as fallback
pdfmetrics.registerFont(TTFont('DejaVuSans', _DEJAVU))
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans')


# ─── Color Palette ───
PRIMARY = colors.HexColor('#374a54')
ACCENT = colors.HexColor('#bd522e')
TEXT_DARK = colors.HexColor('#1e2021')
TEXT_MUTED = colors.HexColor('#7e8487')
TABLE_HEADER_BG = colors.HexColor('#374a54')
TABLE_STRIPE = colors.HexColor('#ebeded')


# ─── Styles ───
def _build_styles():
    """Build paragraph styles for the report."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontName=_SERIF_FONT,
        fontSize=24,
        leading=30,
        textColor=PRIMARY,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name='ReportSubtitle',
        fontName=_SERIF_FONT,
        fontSize=14,
        leading=18,
        textColor=TEXT_MUTED,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName=_SERIF_FONT,
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=18,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name='SubHeading',
        fontName=_SERIF_FONT,
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name='BodyText2',
        fontName=_SERIF_FONT,
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName=_SERIF_FONT,
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name='TableCell',
        fontName=_SERIF_FONT,
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name='TableCellLeft',
        fontName=_SERIF_FONT,
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name='Warning',
        fontName=_SERIF_FONT,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#9d8149'),
        leftIndent=20,
        spaceBefore=2,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        name='Note',
        fontName=_SERIF_FONT,
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED,
        leftIndent=20,
        spaceBefore=2,
        spaceAfter=2,
    ))

    styles.add(ParagraphStyle(
        name='Footer',
        fontName=_SERIF_FONT,
        fontSize=8,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
    ))

    return styles


def _make_table(data, col_widths, styles_obj):
    """Create a styled table."""
    t = Table(data, colWidths=col_widths, hAlign='CENTER')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), _SERIF_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bccbd3')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, TABLE_STRIPE]),
    ]))
    return t


def generate_foundation_design_report(
    result: SiteAssessmentPipelineResult,
    assessment: dict,
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a professional PDF foundation design report from pipeline results.

    Returns: Path to the generated PDF file.
    """
    if output_path is None:
        output_path = f"/tmp/foundation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    styles = _build_styles()
    story = []
    page_width = A4[0]
    available_width = page_width - 2 * inch

    # ── Title Page ──
    story.append(Spacer(1, 80))
    story.append(Paragraph("Foundation Design Report", styles['ReportTitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        assessment.get('project_name', 'Construction Project'),
        styles['ReportSubtitle']
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Prepared by: {assessment.get('engineer_name', 'CivilEng User')}",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        f"Date: {assessment.get('assessment_date', datetime.now().strftime('%Y-%m-%d'))}",
        styles['BodyText2']
    ))
    story.append(Paragraph(
        f"Report generated by CivilEng v0.2.0",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "<i>This report presents foundation design calculations based on site assessment data. "
        "All calculations are performed in accordance with BS 8004:2015, BS 8110:1997, "
        "and EN 1997-1:2004. Results must be verified by a licensed structural engineer "
        "before construction.</i>",
        styles['Note']
    ))
    story.append(PageBreak())

    # ── 1. Site Assessment Summary ──
    story.append(Paragraph("<b>1. Site Assessment Summary</b>", styles['SectionHeading']))

    site_data = [
        [Paragraph('<b>Parameter</b>', styles['TableHeader']),
         Paragraph('<b>Value</b>', styles['TableHeader'])],
        [Paragraph('Location', styles['TableCellLeft']),
         Paragraph(assessment.get('location_description', 'Not specified'), styles['TableCellLeft'])],
        [Paragraph('Terrain', styles['TableCellLeft']),
         Paragraph(assessment.get('terrain_type', 'Not specified'), styles['TableCellLeft'])],
        [Paragraph('Slope Angle', styles['TableCellLeft']),
         Paragraph(f"{assessment.get('slope_angle_deg', 0)} degrees", styles['TableCell'])],
        [Paragraph('Groundwater', styles['TableCellLeft']),
         Paragraph(assessment.get('groundwater_condition', 'Not observed'), styles['TableCellLeft'])],
        [Paragraph('Water Table Depth', styles['TableCellLeft']),
         Paragraph(f"{assessment.get('water_table_depth_m', 'Not determined')} m", styles['TableCell'])],
        [Paragraph('Adjacent Structures', styles['TableCellLeft']),
         Paragraph('Yes' if assessment.get('adjacent_structures') else 'No', styles['TableCell'])],
    ]

    story.append(Spacer(1, 6))
    story.append(_make_table(site_data, [available_width * 0.45, available_width * 0.55], styles))
    story.append(Spacer(1, 12))

    # ── 2. Soil Classification ──
    story.append(Paragraph("<b>2. Soil Classification</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"Classification performed per BS 5930:2015 / ISO 14688.",
        styles['BodyText2']
    ))

    sc = result.soil_classification
    soil_data = [
        [Paragraph('<b>Parameter</b>', styles['TableHeader']),
         Paragraph('<b>Value</b>', styles['TableHeader'])],
        [Paragraph('Classification', styles['TableCellLeft']),
         Paragraph(sc.bs5930_name, styles['TableCellLeft'])],
        [Paragraph('Primary Group', styles['TableCellLeft']),
         Paragraph(sc.primary_group.value, styles['TableCell'])],
        [Paragraph('Coarse Fraction', styles['TableCellLeft']),
         Paragraph(f"{sc.coarse_fraction_pct}%", styles['TableCell'])],
        [Paragraph('Fine Fraction', styles['TableCellLeft']),
         Paragraph(f"{sc.fine_fraction_pct}%", styles['TableCell'])],
        [Paragraph('Plasticity', styles['TableCellLeft']),
         Paragraph(sc.plasticity or 'N/A (granular)', styles['TableCell'])],
        [Paragraph('Est. Bearing Capacity', styles['TableCellLeft']),
         Paragraph(f"{sc.estimated_bearing_capacity_kPa} kPa", styles['TableCell'])],
        [Paragraph('Est. Cohesion', styles['TableCellLeft']),
         Paragraph(f"{sc.estimated_cohesion_kPa or 'N/A'} kPa", styles['TableCell'])],
        [Paragraph('Est. Angle of Shearing Resistance', styles['TableCellLeft']),
         Paragraph(f"{sc.estimated_angle_of_shearing_resistance_deg or 'N/A'} degrees", styles['TableCell'])],
    ]

    story.append(Spacer(1, 6))
    story.append(_make_table(soil_data, [available_width * 0.50, available_width * 0.50], styles))

    # Suitability notes
    if sc.suitability_notes:
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Suitability Notes:</b>", styles['SubHeading']))
        for note in sc.suitability_notes:
            story.append(Paragraph(f"- {note}", styles['Note']))

    story.append(Spacer(1, 12))

    # ── 3. Bearing Capacity Analysis ──
    story.append(Paragraph("<b>3. Bearing Capacity Analysis</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"Analysed for a 2.0 m x 2.0 m foundation at 1.0 m depth. "
        f"Recommended allowable bearing capacity: <b>{result.recommended_bearing_capacity_kPa} kPa</b> "
        f"(conservative value from three methods).",
        styles['BodyText2']
    ))

    bc_data = [
        [Paragraph('<b>Method</b>', styles['TableHeader']),
         Paragraph('<b>q<sub>ult</sub> (kPa)</b>', styles['TableHeader']),
         Paragraph('<b>q<sub>net</sub> (kPa)</b>', styles['TableHeader']),
         Paragraph('<b>q<sub>all</sub> (kPa)</b>', styles['TableHeader']),
         Paragraph('<b>FoS</b>', styles['TableHeader'])],
        [Paragraph('Terzaghi', styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_terzaghi.ultimate_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_terzaghi.net_ultimate_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_terzaghi.allowable_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_terzaghi.factor_of_safety}", styles['TableCell'])],
        [Paragraph('Meyerhof', styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_meyerhof.ultimate_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_meyerhof.net_ultimate_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_meyerhof.allowable_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_meyerhof.factor_of_safety}", styles['TableCell'])],
        [Paragraph('Vesic', styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_vesic.ultimate_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_vesic.net_ultimate_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_vesic.allowable_bearing_capacity}", styles['TableCell']),
         Paragraph(f"{result.bearing_capacity_vesic.factor_of_safety}", styles['TableCell'])],
    ]

    story.append(Spacer(1, 6))
    story.append(_make_table(bc_data,
        [available_width * 0.20, available_width * 0.20, available_width * 0.20,
         available_width * 0.20, available_width * 0.20], styles))

    # Code reference
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Reference: {result.bearing_capacity_terzaghi.code_reference}",
        styles['Note']
    ))
    story.append(Spacer(1, 12))

    # ── 4. Foundation Recommendation ──
    story.append(Paragraph("<b>4. Foundation Type Recommendation</b>", styles['SectionHeading']))

    fr = result.foundation_recommendation
    rec_data = [
        [Paragraph('<b>Parameter</b>', styles['TableHeader']),
         Paragraph('<b>Value</b>', styles['TableHeader'])],
        [Paragraph('Recommended Type', styles['TableCellLeft']),
         Paragraph(f"<b>{fr.recommended.value.upper()}</b>", styles['TableCellLeft'])],
        [Paragraph('Confidence', styles['TableCellLeft']),
         Paragraph(f"{fr.confidence:.0%}", styles['TableCell'])],
        [Paragraph('Cost Indicator', styles['TableCellLeft']),
         Paragraph(fr.cost_indicator, styles['TableCell'])],
        [Paragraph('Constructability', styles['TableCellLeft']),
         Paragraph(fr.constructability, styles['TableCell'])],
        [Paragraph('Alternatives', styles['TableCellLeft']),
         Paragraph(', '.join(a.value for a in fr.alternatives), styles['TableCellLeft'])],
    ]

    story.append(Spacer(1, 6))
    story.append(_make_table(rec_data, [available_width * 0.40, available_width * 0.60], styles))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Justification:</b>", styles['SubHeading']))
    story.append(Paragraph(fr.justification, styles['BodyText2']))

    if fr.risk_factors:
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Risk Factors:</b>", styles['SubHeading']))
        for risk in fr.risk_factors:
            story.append(Paragraph(f"! {risk}", styles['Warning']))

    story.append(Spacer(1, 12))

    # ── 5. Foundation Design ──
    story.append(Paragraph("<b>5. Foundation Design</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"Design per BS 8110:1997 and BS 8004:2015. "
        f"Concrete grade: {assessment.get('concrete_grade', 'C30')}. "
        f"Reinforcement grade: {assessment.get('rebar_grade', 'B500')}.",
        styles['BodyText2']
    ))

    design = result.foundation_design
    if design:
        design_rows = [
            [Paragraph('<b>Parameter</b>', styles['TableHeader']),
             Paragraph('<b>Value</b>', styles['TableHeader'])],
        ]
        for key, val in design.items():
            if isinstance(val, (int, float, str, bool)):
                display_key = key.replace('_', ' ').title()
                display_val = str(val)
                # Format common keys
                if '_mm' in key and isinstance(val, (int, float)):
                    display_val = f"{val} mm"
                elif '_kN' in key and isinstance(val, (int, float)):
                    display_val = f"{val} kN"
                elif '_kPa' in key and isinstance(val, (int, float)):
                    display_val = f"{val} kPa"
                elif '_MPa' in key and isinstance(val, (int, float)):
                    display_val = f"{val} MPa"
                elif '_m2' in key and isinstance(val, (int, float)):
                    display_val = f"{val} m2"
                elif '_m3' in key and isinstance(val, (int, float)):
                    display_val = f"{val} m3"
                elif '_kg' in key and isinstance(val, (int, float)):
                    display_val = f"{val} kg"
                elif isinstance(val, bool):
                    display_val = "Yes" if val else "No"

                design_rows.append([
                    Paragraph(display_key, styles['TableCellLeft']),
                    Paragraph(display_val, styles['TableCell']),
                ])

        if len(design_rows) > 1:
            story.append(Spacer(1, 6))
            story.append(_make_table(design_rows,
                [available_width * 0.50, available_width * 0.50], styles))

    story.append(Spacer(1, 12))

    # ── 6. Bill of Quantities ──
    story.append(Paragraph("<b>6. Bill of Quantities — Foundation</b>", styles['SectionHeading']))

    mq = result.material_quantities
    boq_data = [
        [Paragraph('<b>Item</b>', styles['TableHeader']),
         Paragraph('<b>Quantity</b>', styles['TableHeader']),
         Paragraph('<b>Unit</b>', styles['TableHeader'])],
        [Paragraph('Concrete (incl. wastage)', styles['TableCellLeft']),
         Paragraph(f"{mq.total_concrete_with_wastage_m3}", styles['TableCell']),
         Paragraph('m3', styles['TableCell'])],
        [Paragraph('Reinforcement (incl. wastage)', styles['TableCellLeft']),
         Paragraph(f"{mq.total_rebar_with_wastage_kg}", styles['TableCell']),
         Paragraph('kg', styles['TableCell'])],
        [Paragraph('Formwork', styles['TableCellLeft']),
         Paragraph(f"{mq.total_formwork_m2}", styles['TableCell']),
         Paragraph('m2', styles['TableCell'])],
        [Paragraph('Rebar Density', styles['TableCellLeft']),
         Paragraph(f"{mq.rebar_density_kg_per_m3}", styles['TableCell']),
         Paragraph('kg/m3', styles['TableCell'])],
    ]

    story.append(Spacer(1, 6))
    story.append(_make_table(boq_data,
        [available_width * 0.50, available_width * 0.25, available_width * 0.25], styles))

    story.append(Spacer(1, 12))

    # ── 7. Warnings & Design Notes ──
    if result.warnings:
        story.append(Paragraph("<b>7. Warnings</b>", styles['SectionHeading']))
        for i, w in enumerate(result.warnings, 1):
            story.append(Paragraph(f"{i}. {w}", styles['Warning']))
        story.append(Spacer(1, 12))

    if result.design_notes:
        story.append(Paragraph("<b>8. Design Notes</b>", styles['SectionHeading']))
        for n in result.design_notes:
            story.append(Paragraph(f"- {n}", styles['Note']))

    # ── Disclaimer ──
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "<i>Disclaimer: This report is generated by CivilEng software as a calculation aid. "
        "It does not constitute professional engineering advice. All designs and calculations "
        "must be reviewed and certified by a licensed structural/geotechnical engineer before "
        "use in construction. The software developers accept no liability for designs based "
        "on this report.</i>",
        styles['Note']
    ))

    # ── Build PDF ──
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    doc.build(story)
    return output_path
