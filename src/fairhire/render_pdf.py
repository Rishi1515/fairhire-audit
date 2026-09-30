"""Render a resume to a simple one-page PDF from the same sections as the text version.

PDFs are for people to look at. The ranking methods always read the plain-text
rendering, so fonts and page layout cannot affect any score.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from fairhire.render_resumes import SECTION_TITLES, render_sections
from fairhire.schemas import Resume


def render_pdf(resume: Resume, path: Path) -> None:
    styles = getSampleStyleSheet()
    body, head = styles["BodyText"], styles["Heading4"]
    sections = render_sections(resume)
    story = []
    first, *rest = sections["header"].splitlines()
    story += [Paragraph(escape(first), styles["Title"])] + [Paragraph(escape(x), body) for x in rest]
    for name in resume.render_options.section_order:
        story += [Spacer(1, 3 * mm), Paragraph(SECTION_TITLES[name], head)]
        story += [Paragraph(escape(line), body) for line in sections[name].splitlines() if line.strip()]
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title="Fictional benchmark resume",
                            author="FairHire Audit (fictional data)", invariant=1)
    doc.build(story)
