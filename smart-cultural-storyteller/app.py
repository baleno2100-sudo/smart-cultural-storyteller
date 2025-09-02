# ======== PDF Export (Refined) ========
def create_pdf(story_title, story_body, moral_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=colors.HexColor(accent_color),
        alignment=1,
        spaceAfter=12,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.black
    )
    moral_style = ParagraphStyle(
        "MoralStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor(accent_color),
        spaceBefore=12
    )

    story_elements = [Paragraph(story_title, title_style), Spacer(1, 12)]
    for line in story_body.split("\n"):
        if line.strip():
            story_elements.append(Paragraph(line.strip(), body_style))
            story_elements.append(Spacer(1, 4))

    if moral_text:
        story_elements.append(Paragraph("Moral: " + moral_text, moral_style))

    doc.build(story_elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer
