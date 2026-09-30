"""Render structured resumes to plain text.

Plain text is what every ranking method receives, so rendering is deterministic:
the same record always gives the same string. Both members of a pair go through
exactly the same function, which is one of the validity safeguards.
"""

from __future__ import annotations

from datetime import datetime

from fairhire.schemas import Resume

CANONICAL_NAME_PLACEHOLDER = "[Candidate]"
SECTION_TITLES = {"summary": "SUMMARY", "experience": "EXPERIENCE", "education": "EDUCATION", "skills": "SKILLS"}


def format_month(value: str | None) -> str:
    """``2023-03`` becomes ``Mar 2023``. ``None`` becomes ``Present``."""
    if value is None:
        return "Present"
    return datetime.strptime(value, "%Y-%m").strftime("%b %Y")


def render_sections(resume: Resume) -> dict[str, str]:
    """Return each resume section as text, keyed by section name.

    Keys: ``header``, ``summary``, ``experience``, ``education``, ``skills``.
    Certifications and projects are shown under skills and experience
    respectively, because that is where a reader would look for them.
    """
    bullet = resume.render_options.bullet
    ident = resume.identity
    header = [ident.name or CANONICAL_NAME_PLACEHOLDER,
              " | ".join(x for x in (ident.email, ident.phone, ident.location) if x)]
    if ident.pronouns:
        header.append(f"Pronouns: {ident.pronouns}")

    timeline = [(r.start, "role", r) for r in resume.experience]
    timeline += [(b.start, "break", b) for b in resume.career_breaks]
    timeline.sort(key=lambda item: item[0], reverse=True)
    exp: list[str] = []
    for _, kind, item in timeline:
        if kind == "break":
            exp += [f"{item.label} | {format_month(item.start)} - {format_month(item.end)}", ""]
            continue
        exp.append(f"{item.title}, {item.employer} | {item.location} | "
                   f"{format_month(item.start)} - {format_month(item.end)}")
        exp += [f"{bullet} {b}" for b in item.bullets]
        exp.append("")
    if resume.projects:
        exp += ["Projects"] + [f"{bullet} {p.name}: {p.description}" for p in resume.projects]

    edu: list[str] = []
    for e in resume.education:
        grade = f", {e.grade}" if e.grade else ""
        edu += [f"{e.qualification} in {e.subject}{grade}",
                f"{e.institution} | {format_month(e.start)} - {format_month(e.end)}"]
        if e.coursework:
            edu.append("Relevant coursework: " + ", ".join(e.coursework))

    skills = [f"{group}: {', '.join(items)}" for group, items in resume.skills.items()]
    if resume.certifications:
        skills += ["Certifications"] + [f"{bullet} {c}" for c in resume.certifications]

    return {"header": "\n".join(header), "summary": resume.summary.strip(),
            "experience": "\n".join(exp).strip(), "education": "\n".join(edu), "skills": "\n".join(skills)}


def render_text(resume: Resume) -> str:
    """Return the full plain-text rendering in the resume's section order."""
    sections = render_sections(resume)
    parts = [sections["header"]]
    for name in resume.render_options.section_order:
        parts.append(f"{SECTION_TITLES[name]}\n{sections[name]}")
    return "\n\n".join(parts).rstrip() + "\n"
