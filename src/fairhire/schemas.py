"""Typed records for the FairHire Audit benchmark.

Every data file in ``data/`` is validated against one of these models before it
is used. The goal is to catch inconsistent jobs, rubrics and resumes early,
before any ranking method sees them.

Design notes
------------
* Dates are stored as ``YYYY-MM`` strings. Month precision is enough for a
  resume and keeps career-gap arithmetic simple.
* A canonical resume never contains a real name. The identity fields are left
  empty and are filled only when a counterfactual variant is generated.
* ``PERMITTED_FIELDS`` lists which parts of a resume each transformation type
  may change. The pair-integrity tests (checkpoint 4) will use it.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

YEAR_MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def to_months(value: str) -> int:
    """Convert a ``YYYY-MM`` string to a month index for date arithmetic."""
    if not YEAR_MONTH.match(value):
        raise ValueError(f"expected YYYY-MM, got {value!r}")
    year, month = value.split("-")
    return int(year) * 12 + int(month) - 1


class StrictModel(BaseModel):
    """Base model that rejects unknown keys, so typos in YAML fail loudly."""

    model_config = ConfigDict(extra="forbid", frozen=True)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class JobFamily(str, Enum):
    DATA_ANALYST = "data_analyst"
    SOFTWARE_ENGINEER = "software_engineer"
    MARKETING_ANALYST = "marketing_analyst"


class Tier(str, Enum):
    """Intended qualification tier of a resume for a specific job.

    This is the author's design intention. The applicant's blind rubric scores
    are recorded separately and are the reference used in evaluation.
    """

    STRONG = "strong"
    GOOD = "good"
    BORDERLINE = "borderline"
    WEAK = "weak"


class Importance(str, Enum):
    ESSENTIAL = "essential"
    DESIRABLE = "desirable"


class TransformationType(str, Enum):
    NONE = "none"  # the unmodified base rendering
    NAME_CUE = "name_cue"
    CAREER_GAP = "career_gap"
    INSTITUTION = "institution"
    FORMATTING = "formatting"


# Resume fields each transformation may change. Anything else must be
# byte-identical between the two members of a pair.
PERMITTED_FIELDS: dict[TransformationType, frozenset[str]] = {
    TransformationType.NONE: frozenset(),
    TransformationType.NAME_CUE: frozenset({"identity.name", "identity.email", "identity.pronouns"}),
    TransformationType.CAREER_GAP: frozenset({"experience[].start", "experience[].end", "education[].start",
                                              "education[].end", "career_breaks"}),
    TransformationType.INSTITUTION: frozenset({"education[0].institution"}),
    TransformationType.FORMATTING: frozenset({"render_options"}),
}


# ---------------------------------------------------------------------------
# Jobs and rubrics
# ---------------------------------------------------------------------------


class JobDescription(StrictModel):
    job_id: str = Field(pattern=r"^(DA|SE|MA)-\d{2}$")
    family: JobFamily
    title: str
    employer: str = Field(description="Fictional employer name.")
    location: str
    summary: str
    responsibilities: list[str] = Field(min_length=3)
    requirements: list[str] = Field(min_length=3)
    nice_to_have: list[str] = Field(default_factory=list)
    version: str

    @model_validator(mode="after")
    def _prefix_matches_family(self) -> "JobDescription":
        expected = {"DA": JobFamily.DATA_ANALYST, "SE": JobFamily.SOFTWARE_ENGINEER,
                    "MA": JobFamily.MARKETING_ANALYST}[self.job_id[:2]]
        if self.family != expected:
            raise ValueError(f"{self.job_id} prefix does not match family {self.family.value}")
        return self


class Competency(StrictModel):
    competency_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    name: str
    importance: Importance
    weight: float = Field(gt=0, le=1)
    aliases: list[str] = Field(default_factory=list,
                               description="Surface forms the keyword baseline may match.")
    observable_evidence: list[str] = Field(min_length=1,
                                           description="What a reviewer should look for.")
    does_not_count: list[str] = Field(default_factory=list,
                                      description="Evidence that must not raise the score on its own.")


class ScoreLevel(StrictModel):
    level: int = Field(ge=0, le=3)
    meaning: str


class Rubric(StrictModel):
    rubric_id: str
    job_id: str
    version: str
    status: str = Field(pattern=r"^(draft|approved|locked)$")
    scale: list[ScoreLevel] = Field(min_length=4, max_length=4)
    competencies: list[Competency] = Field(min_length=5, max_length=8)
    irrelevant_signals: list[str] = Field(min_length=1,
                                          description="Signals that must never change a score.")

    @model_validator(mode="after")
    def _weights_and_ids(self) -> "Rubric":
        total = round(sum(c.weight for c in self.competencies), 6)
        if total != 1.0:
            raise ValueError(f"{self.rubric_id}: competency weights sum to {total}, expected 1.0")
        ids = [c.competency_id for c in self.competencies]
        if len(ids) != len(set(ids)):
            raise ValueError(f"{self.rubric_id}: duplicate competency ids")
        if [s.level for s in self.scale] != [0, 1, 2, 3]:
            raise ValueError(f"{self.rubric_id}: scale must define levels 0, 1, 2, 3 in order")
        essential = sum(c.weight for c in self.competencies if c.importance == Importance.ESSENTIAL)
        if essential < 0.5:
            raise ValueError(f"{self.rubric_id}: essential competencies carry less than half the weight")
        return self


# ---------------------------------------------------------------------------
# Resumes
# ---------------------------------------------------------------------------


class Identity(StrictModel):
    """Identity fields. Empty in a canonical resume, filled in a variant."""

    name: Optional[str] = None
    email: Optional[str] = None
    pronouns: Optional[str] = None
    phone: str = "+65 9000 0000"  # fixed fictional number, identical for every resume
    location: str = "Singapore"


class Role(StrictModel):
    employer: str
    title: str
    location: str
    start: str
    end: Optional[str] = Field(default=None, description="None means current role.")
    bullets: list[str] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def _dates(self) -> "Role":
        start = to_months(self.start)
        if self.end is not None and to_months(self.end) < start:
            raise ValueError(f"{self.employer}: end {self.end} is before start {self.start}")
        return self


class Education(StrictModel):
    institution: str
    qualification: str = Field(description="e.g. Bachelor of Science")
    subject: str
    start: str
    end: str
    grade: Optional[str] = None
    coursework: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _dates(self) -> "Education":
        if to_months(self.end) <= to_months(self.start):
            raise ValueError(f"{self.institution}: end must be after start")
        return self


class CareerBreak(StrictModel):
    """A career gap inserted by the career-gap transformation."""

    label: str
    start: str
    end: str


class Project(StrictModel):
    name: str
    description: str


class RenderOptions(StrictModel):
    """Presentation-only settings changed by the formatting test."""

    section_order: tuple[str, ...] = ("summary", "experience", "education", "skills")
    bullet: str = "-"

    @model_validator(mode="after")
    def _sections(self) -> "RenderOptions":
        if sorted(self.section_order) != sorted(("summary", "experience", "education", "skills")):
            raise ValueError("section_order must contain summary, experience, education and skills once each")
        return self


class Resume(StrictModel):
    """A fictional resume. Variants may carry identity fields; canonical records may not."""

    resume_id: str = Field(pattern=r"^(DA|SE|MA)-R\d{2}$")
    family: JobFamily
    intended_tier: dict[str, Tier] = Field(description="Intended tier for each job_id in the family.")
    generation_version: str
    status: str = Field(pattern=r"^(draft|approved|locked)$")
    design_notes: str = Field(description="Why this resume sits in its tier. Not shown to any model.")
    identity: Identity = Identity()
    summary: str
    experience: list[Role] = Field(min_length=2,
                                   description="Most recent first. At least two roles so a gap can be inserted.")
    education: list[Education] = Field(min_length=1)
    skills: dict[str, list[str]]
    certifications: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    career_breaks: list[CareerBreak] = Field(default_factory=list)
    render_options: RenderOptions = RenderOptions()

    @model_validator(mode="after")
    def _timeline(self) -> "CanonicalResume":
        roles = self.experience
        if sum(1 for r in roles if r.end is None) > 1:
            raise ValueError(f"{self.resume_id}: more than one current role")
        # most recent first, and no overlapping roles
        for newer, older in zip(roles, roles[1:]):
            if older.end is None:
                raise ValueError(f"{self.resume_id}: only the first listed role may be current")
            if to_months(older.end) >= to_months(newer.start):
                raise ValueError(f"{self.resume_id}: {older.employer} overlaps or is out of order "
                                 f"with {newer.employer}")
        first_job = to_months(roles[-1].start)
        last_study = max(to_months(e.end) for e in self.education)
        if last_study > first_job + 1:
            raise ValueError(f"{self.resume_id}: education ends after the first full-time role starts")
        if not self.skills or any(not v for v in self.skills.values()):
            raise ValueError(f"{self.resume_id}: skills groups must be non-empty")
        prefix = self.resume_id[:2]
        for job_id in self.intended_tier:
            if not job_id.startswith(prefix):
                raise ValueError(f"{self.resume_id}: tier given for job {job_id} outside its family")
        return self

    def months_of_experience(self, as_of: str) -> int:
        """Total months in listed roles up to ``as_of`` (inclusive of start month)."""
        total = 0
        for role in self.experience:
            end = to_months(role.end) if role.end else to_months(as_of)
            total += end - to_months(role.start) + 1
        return total


class CanonicalResume(Resume):
    """A base resume before any counterfactual change. It must not identify anyone."""

    @field_validator("identity")
    @classmethod
    def _canonical_has_no_identity(cls, value: Identity) -> Identity:
        if value.name or value.email or value.pronouns:
            raise ValueError("a canonical resume must not contain a name, email or pronouns")
        return value


# ---------------------------------------------------------------------------
# Generated samples and evaluation outputs (used from checkpoint 4 onward)
# ---------------------------------------------------------------------------


class VariantRecord(StrictModel):
    """One generated resume variant, ready to be scored against one job."""

    sample_id: str
    base_resume_id: str
    job_id: str
    qualification_tier: Tier
    transformation_type: TransformationType
    transformation_value: str
    generation_version: str
    content_hash: str = Field(description="SHA-256 of the canonical record with permitted fields removed.")
    resume: Resume = Field(description="Materialised resume, identity filled in.")


class PairRecord(StrictModel):
    """Two variants of the same base resume that differ in one controlled field."""

    pair_id: str
    base_resume_id: str
    job_id: str
    transformation_type: TransformationType
    sample_a: str
    sample_b: str


class ScoreRecord(StrictModel):
    """One score from one method for one sample and job. Written by the runners."""

    run_id: str
    sample_id: str
    job_id: str
    method: str = Field(pattern=r"^(keyword|embedding|embedding_sectioned|llm_rubric)$")
    mitigation: str = Field(pattern=r"^(none|anonymised|structured_evidence)$")
    repetition: int = Field(ge=0)
    score: Optional[float] = Field(default=None, ge=0, le=100,
                                   description="None when the method failed to produce a valid score.")
    competency_scores: dict[str, float] = Field(default_factory=dict)
    parser_status: str = "ok"
    model_id: Optional[str] = None
    seed: Optional[int] = None
