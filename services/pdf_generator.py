import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_complaint_pdf(draft_text: str, reference_code: str) -> io.BytesIO:
    """
    Generates a clean, professional PDF document from complaint draft text using ReportLab.
    Returns a BytesIO stream.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#7c3aed"),
        spaceAfter=14
    )

    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=8
    )

    story = [
        Paragraph("SHESHIELD — FORMAL COMPLAINT DRAFT", title_style),
        Paragraph(f"Reference Code: {reference_code} | Prepared for Statutory Authority Submission", meta_style),
        Spacer(1, 10)
    ]

    # Split lines and append as formatted paragraphs
    for line in draft_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        else:
            # Escape XML entities for ReportLab Paragraph
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if safe_line.startswith(("To:", "SUBJECT:", "1.", "2.", "3.", "4.", "5.", "VERIFICATION:", "घोषणा:", "विषय:")):
                story.append(Paragraph(f"<b>{safe_line}</b>", body_style))
            else:
                story.append(Paragraph(safe_line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
