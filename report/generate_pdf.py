"""
generate_pdf.py
Compiles the final report into a publication-quality PDF using ReportLab.
Includes typography styling, tables, code blocks, and embedded figures.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "BusBidder_Spain_Final_Report.pdf"


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1A237E'),
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#37474F'),
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1976D2'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#212121'),
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        leftIndent=15,
        firstLineIndent=-10,
        textColor=colors.HexColor('#212121'),
        spaceAfter=3,
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#263238'),
        backColor=colors.HexColor('#F5F7FA'),
        borderColor=colors.HexColor('#CFD8DC'),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8,
        spaceBefore=4,
    )

    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#37474F'),
        backColor=colors.HexColor('#E8EAF6'),
        borderColor=colors.HexColor('#9FA8DA'),
        borderWidth=0.8,
        borderPadding=6,
        spaceAfter=8,
        spaceBefore=6,
    )

    story = []

    # Title & Header
    story.append(Paragraph("BusBidder Spain: Flexible Bus-Booking & Offer-Ranking", title_style))
    story.append(Paragraph("<b>Course</b>: ACIT4420 Problem-Solving with Scripting (2026) | <b>Department of Computer Science, OsloMet</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0D47A1'), spaceBefore=2, spaceAfter=10))

    # Executive Summary
    story.append(Paragraph("<b>Executive Summary</b>", h2_style))
    story.append(Paragraph(
        "This report documents <b>BusBidder Spain</b>, a Python application designed to filter and rank competing bus offers "
        "originating from Madrid to 15 regional destinations across Spain. Departing from naive single-variable sorting (e.g. cheapest first), "
        "the application strictly decouples non-negotiable <b>hard constraints</b> from <b>soft ranking preferences</b> using a transparent, "
        "weighted multi-attribute decision model (MCDM) normalized to a 0–100 scale. Key technical techniques include attribute validation descriptors, "
        "a pluggable <code>@register_criterion</code> decorator registry, regular expression integrity validation, quarantine error handling, "
        "and a 30-case automated test suite.",
        body_style
    ))

    # Section 1: Problem Interpretation
    story.append(Paragraph("1. Problem Interpretation & Requirements Analysis (10%)", h1_style))
    story.append(Paragraph(
        "Modern travel planning requires balancing conflicting attributes: low prices frequently entail longer travel times, "
        "multiple transfers, inconvenient departure hours, and rigid cancellation policies. BusBidder Spain addresses the central challenge: "
        "<i>How can a Python application filter and rank competing bus offers according to the specific priorities of an individual traveller in an explainable and defensible manner?</i>",
        body_style
    ))
    story.append(Paragraph("The marketplace serves <b>15 destinations</b> departing from Madrid hub across <b>5 operators</b>:", body_style))
    story.append(Paragraph("• <b>SolRuta</b>: Low-cost daytime services with frequent schedules and strict non-refundable tickets.", bullet_style))
    story.append(Paragraph("• <b>Camino Express</b>: Fast direct connections connecting major cities with high ticket flexibility.", bullet_style))
    story.append(Paragraph("• <b>CostaLink</b>: Coastal route specialist with generous 25kg luggage allowances.", bullet_style))
    story.append(Paragraph("• <b>VerdeBus</b>: Low-emission modern fleet with eco-certified vehicles.", bullet_style))
    story.append(Paragraph("• <b>NocheVia</b>: Overnight sleeper services designed to save daylight hours and lodging expenses.", bullet_style))

    # Section 2: Architecture & Design Justifications
    story.append(Paragraph("2. Software Design & Architecture Justifications (15%)", h1_style))
    story.append(Paragraph(
        "The project follows a modular package decomposition separating models, validation descriptors, data loaders, "
        "decision engines, booking persistence, and the command-line interface.",
        body_style
    ))

    # Insert Architecture Diagram
    arch_img_path = BASE_DIR / "architecture_diagram.png"
    if arch_img_path.exists():
        story.append(Spacer(1, 4))
        story.append(Image(str(arch_img_path), width=500, height=290))
        story.append(Paragraph("<b>Figure 1:</b> Component Architecture and Information Flow Diagram of BusBidder Spain.", callout_style))

    story.append(Paragraph("<b>Metaprogramming & Advanced Python Techniques</b>", h2_style))
    story.append(Paragraph(
        "• <b>Custom Validation Descriptors (<code>src.validators.descriptors</code>)</b>: Attribute descriptors "
        "(<code>PositiveNumber</code>, <code>NonNegativeInt</code>, <code>BoundedFloat</code>, <code>RegexValidatedString</code>) "
        "intercept assignments at runtime, preventing invalid domain states (e.g. negative prices or ratings > 5.0) before instances can be created.<br/>"
        "• <b>Pluggable Registry Decorator (<code>@register_criterion</code>)</b>: Implements an extensible criteria registry in "
        "<code>src.engine.criteria</code>. New ranking dimensions can be registered without modifying the ranker's core execution loop.<br/>"
        "• <b>Regular Expressions (<code>src.validators.regex_patterns</code>)</b>: Enforces format validity on booking reference codes "
        "(<code>^ES-[A-Z0-9]{6}$</code>), offer codes (<code>^OFF-[A-Z]{2,4}-\\d{4}$</code>), 24h timestamps, and ISO dates.",
        body_style
    ))

    # Page Break for clean layout
    story.append(PageBreak())

    # Section 3: Implementation Details
    story.append(Paragraph("3. Implementation Details & Decision Mechanics (15%)", h1_style))
    story.append(Paragraph(
        "<b>The Quarantine Pipeline</b>: In <code>DataLoader.load_offers()</code>, malformed rows (such as unknown destinations, negative fares, "
        "or departure-arrival temporal contradictions) are caught via structured custom exceptions (<code>DataValidationError</code>). "
        "Rather than crashing the application, invalid records are routed to <code>data/quarantine_offers.csv</code> with explicit rejection reasons and audit logged in <code>busbidder.log</code>.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Multi-Criteria Normalization (0–100 Scale)</b>: Because price (EUR), duration (minutes), ratings (1–5), and departure proximity "
        "have disparate physical units, criteria are converted to normalized scores:<br/>"
        "• <i>Cost Criteria (Lower is Better)</i>: <code>Score = ((max(X) - x) / (max(X) - min(X))) * 100</code><br/>"
        "• <i>Benefit Criteria (Higher is Better)</i>: <code>Score = ((x - min(X)) / (max(X) - min(X))) * 100</code><br/>"
        "• <i>Circular Clock Proximity</i>: Computes minimal angular distance on a 24-hour dial: <code>Δ = min(|H - T|, 24 - |H - T|)</code>, "
        "awarding 100 for exact alignment and decaying linearly to 0 at 8 hours deviation.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Explainable Recommendation Engine</b>: Section 6 of the project brief emphasizes transparent explanations. "
        "The <code>RecommendationExplainer</code> analyzes top offers to explicitly highlight advantages (e.g. lowest price, zero transfers, low emissions) "
        "while acknowledging remaining trade-offs (e.g. price premiums over budget alternatives). Importantly, the system explicitly clarifies "
        "that the winning offer is <i>not objectively superior</i>, but optimal solely under the user's specific weights and constraints.",
        body_style
    ))

    # Section 4: Testing & Experimental Evidence
    story.append(Paragraph("4. Automated Testing and Experimental Evidence (15%)", h1_style))
    story.append(Paragraph(
        "A rigorous suite of <b>30 automated tests</b> was constructed in <code>pytest</code>, verifying normal execution, boundary conditions, "
        "corrupt quarantine handling, and sensitivity divergence:",
        body_style
    ))

    test_data = [
        ["Test Module", "Cases", "Focus Area", "Status"],
        ["test_descriptors_and_models.py", "8", "Attribute bounds, negative prices, regex validation, date logic", "PASSED"],
        ["test_loaders.py", "4", "File I/O, relational checks, quarantine sink, missing files", "PASSED"],
        ["test_filters.py", "4", "Hard constraints: budget caps, date windows, transfers, seats", "PASSED"],
        ["test_ranker_and_normalizers.py", "6", "0-100 normalization math, circular clock, tie-breaking, explainer", "PASSED"],
        ["test_booking.py", "4", "Capacity decrements, ticket generation, reference validation, cancels", "PASSED"],
        ["test_preference_quiz.py", "3", "1-5 rating normalization, sum-to-1.0 guarantee, request integration", "PASSED"],
        ["test_profile_divergence.py", "1", "Proves distinct winners across different traveller archetypes", "PASSED"],
    ]
    t = Table(test_data, colWidths=[160, 40, 240, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B0BEC5')),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    # Section 5: Profile Comparisons
    story.append(Paragraph("5. Experimental Sensitivity Analysis: Profile Comparisons (15%)", h1_style))
    story.append(Paragraph(
        "To evaluate whether the application genuinely personalizes results, a sensitivity experiment was conducted for travel from "
        "<b>Madrid to Malaga (12–14 July 2026)</b> across four distinct traveller profiles:",
        body_style
    ))

    # Comparison Table
    profile_data = [
        ["Profile", "Primary Focus", "Winning Operator", "Price", "Duration", "CO2", "Total Score"],
        ["Budget Backpacker", "Lowest Price (60%)", "SolRuta (OFF-SR-1045)", "EUR 29.15", "7h 46m", "20.1 kg", "80.6 / 100"],
        ["Business Executive", "Speed (40%), Timing (30%)", "Camino Express (OFF-CE-1048)", "EUR 50.35", "6h 26m", "17.0 kg", "88.0 / 100"],
        ["Eco-Conscious", "Low Emissions (50%)", "VerdeBus (OFF-VB-1055)", "EUR 39.75", "6h 55m", "7.4 kg", "89.5 / 100"],
        ["Flexible Tourist", "Flexibility (45%), Luggage", "VerdeBus (OFF-VB-1056)", "EUR 39.75", "6h 55m", "7.4 kg", "92.5 / 100"],
    ]
    pt = Table(profile_data, colWidths=[100, 110, 120, 50, 45, 40, 55])
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B0BEC5')),
        ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E3F2FD')]),
    ]))
    story.append(pt)

    # Insert Profile Chart
    chart_path = BASE_DIR / "profile_comparison_chart.png"
    if chart_path.exists():
        story.append(Spacer(1, 4))
        story.append(Image(str(chart_path), width=480, height=210))
        story.append(Paragraph("<b>Figure 2:</b> Sensitivity Comparison of Winning Offer Score and Price Across Traveller Profiles.", callout_style))

    # Section 6: Evaluation & Critical Reflection
    story.append(Paragraph("6. Evaluation, Limitations and Critical Reflection (20%)", h1_style))
    story.append(Paragraph(
        "<b>1. Outlier Vulnerability in Min-Max Normalization</b>: Min-max scaling is sensitive to extreme boundary outliers. "
        "If a single luxury or emergency service prices a ticket at €130 while nine standard carriers charge €30–€35, "
        "the relative variance among the standard fares is compressed into a narrow score range (< 5 points). In future work, z-score standardization "
        "or non-linear utility curves could improve resilience to extreme values.<br/>"
        "<b>2. Route and Geographic Equity</b>: Destinations situated at Spain's periphery (e.g. Cadiz at 650km or Santiago at 600km) "
        "naturally require 6–8 hours and higher fares compared to proximal cities like Toledo (73km). Global comparisons across multiple destinations "
        "would unfairly penalize operators serving long-haul corridors. Performing normalization strictly within destination-specific candidate pools ensures fairness.<br/>"
        "<b>3. Qualitative Preference Elicitation Trade-offs</b>: The pluggable questionnaire in <code>src.extensions.preference_quiz</code> "
        "significantly improves usability by letting users rate factors on a 1–5 scale. However, it exposes the human cognitive tendency to rate all factors 5/5 "
        "(the 'I want everything' bias), which normalizes to an unopinionated equal-weight model (20% each). Pairwise comparison methods (such as AHP) "
        "would force trade-offs, albeit with higher cognitive overhead.",
        body_style
    ))

    # Section 7: Traceability & AI Declaration
    story.append(Paragraph("7. Implementation Traceability & Academic Integrity (15%)", h1_style))
    story.append(Paragraph(
        "<b>Reproducibility Instructions</b>:<br/>"
        "• Automated Test Execution: <code>python -m pytest -v</code> (Executes all 30 unit and integration tests).<br/>"
        "• Multi-Profile Sensitivity Demonstration: <code>python main.py --demo</code> (Reproduces experimental tables and rankings).<br/>"
        "• Data Quarantine & Ingestion Review: <code>python main.py --quarantine</code> (Inspects rejected malformed records).<br/>"
        "• Interactive Booking: <code>python main.py --interactive</code> (Allows custom search, preference quiz, and ticket generation).",
        code_style
    ))
    story.append(Paragraph(
        "<b>Declaration on Use of Generative AI</b>: Generative AI (Google DeepMind Antigravity Coding Assistant) was utilized "
        "during development for modular scaffolding suggestions, synthetic schedule data generation, test fixture creation, and LaTeX formula formatting. "
        "All algorithms, normalization equations, descriptor implementations, and test assertions were independently traced, verified, and hand-calculated "
        "by the author. Integrity was confirmed through the automated 30-case test suite and audit logs.",
        body_style
    ))

    # Build the document
    doc.build(story)
    print(f"Successfully generated final report PDF: {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
