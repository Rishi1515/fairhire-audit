"""Method 1: a transparent weighted keyword baseline.

This is not a copy of any real applicant-tracking system. It only looks for the
aliases listed in each rubric competency, and it follows the rubric's own rule:
a skill that appears only in the skills list, summary, coursework or
certifications counts as "mentioned" (level 1). A skill that appears in one
experience or project line is "applied" (level 2), and in two or more lines is
"applied with depth" (level 3).

score = 100 * sum(weight * level / 3) over the rubric's competencies
"""

from __future__ import annotations

import re
from functools import lru_cache

from fairhire.render_resumes import render_sections
from fairhire.schemas import Competency, Resume, Rubric


@lru_cache(maxsize=None)
def alias_pattern(alias: str) -> re.Pattern[str]:
    """Whole-word pattern for an alias, allowing a plural 's' or 'es'.

    Short all-capital aliases such as 'R', 'Go' or 'SQL' are matched with case,
    so that ordinary words like 'go' are not counted as the Go language.
    """
    flags = 0 if len(alias) <= 3 else re.IGNORECASE
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(alias)}(?:e?s)?(?![A-Za-z0-9])", flags)


def matches(line: str, competency: Competency) -> bool:
    return any(alias_pattern(a).search(line) for a in competency.aliases)


def evidence_lines(resume: Resume) -> list[str]:
    """Experience bullets and project descriptions: the lines that can show applied skill."""
    lines = [b for role in resume.experience for b in role.bullets]
    lines += [f"{p.name}: {p.description}" for p in resume.projects]
    return lines


def mention_text(resume: Resume) -> str:
    """Places where a skill can only be mentioned, not demonstrated."""
    sections = render_sections(resume)
    return "\n".join([sections["summary"], sections["skills"], sections["education"]])


def competency_level(resume: Resume, competency: Competency) -> tuple[int, list[str]]:
    """Return the keyword level (0 to 3) and the lines that produced it."""
    hits = [line for line in evidence_lines(resume) if matches(line, competency)]
    if len(hits) >= 2:
        return 3, hits
    if len(hits) == 1:
        return 2, hits
    if matches(mention_text(resume), competency):
        return 1, []
    return 0, []


def score_keyword(resume: Resume, rubric: Rubric) -> tuple[float, dict[str, int]]:
    """Score one resume against one rubric. Returns (score 0-100, level per competency)."""
    levels = {c.competency_id: competency_level(resume, c)[0] for c in rubric.competencies}
    score = 100.0 * sum(c.weight * levels[c.competency_id] / 3 for c in rubric.competencies)
    return round(score, 6), levels
