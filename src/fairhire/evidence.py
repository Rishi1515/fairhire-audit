"""Structured evidence mitigation: score only rubric-relevant evidence.

Instead of the whole resume, each ranking method receives a short list of the
lines that match a rubric competency, grouped by competency. Names, contact
details, dates, career breaks and universities are not included, so by
construction they cannot affect the score. The cost is that anything the
rubric aliases miss is also dropped, which may hurt relevance. The report
measures that trade-off instead of assuming it away.
"""

from __future__ import annotations

from fairhire.rank_keyword import evidence_lines, matches
from fairhire.render_resumes import render_sections
from fairhire.schemas import Resume, Rubric


def structured_evidence(resume: Resume, rubric: Rubric) -> str:
    """Return the evidence representation of a resume for one rubric."""
    applied = evidence_lines(resume)
    skills_lines = [ln for ln in render_sections(resume)["skills"].splitlines() if ln.strip()]
    blocks: list[str] = []
    for comp in rubric.competencies:
        hits = [ln for ln in applied if matches(ln, comp)]
        listed = [ln for ln in skills_lines if matches(ln, comp)]
        lines = [f"- {ln}" for ln in hits] + [f"- Listed skill: {ln.lstrip('-* ')}" for ln in listed]
        blocks.append(f"{comp.name}:\n" + ("\n".join(lines) if lines else "- No evidence found"))
    return "\n\n".join(blocks) + "\n"
