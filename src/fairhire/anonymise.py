"""Anonymisation mitigation: remove explicit identity fields before ranking.

Only the fields that name or describe the person are removed (name, email,
pronouns). Job-relevant evidence, dates and education are kept, so anonymisation
cannot hide proxy signals such as a career break or a university name. That is
deliberate: hypothesis H3 is about exactly this limit.
"""

from __future__ import annotations

from fairhire.schemas import Resume

ANONYMOUS_LABEL = "Candidate"


def anonymise(resume: Resume) -> Resume:
    """Return a copy with identity fields replaced by a neutral label."""
    identity = resume.identity.model_copy(update={"name": ANONYMOUS_LABEL, "email": None, "pronouns": None})
    return resume.model_copy(update={"identity": identity})
