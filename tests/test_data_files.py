"""Checks across the whole data folder, not just single files."""

import re

import pytest

from fairhire.data_io import DATA_DIR, load_jobs, load_resumes, load_rubrics
from fairhire.render_resumes import CANONICAL_NAME_PLACEHOLDER, render_text

JOBS = load_jobs()
RUBRICS = load_rubrics()
RESUMES = load_resumes()


def test_every_job_has_exactly_one_rubric():
    assert set(JOBS) == set(RUBRICS)


def test_two_jobs_per_family():
    families = [job.family for job in JOBS.values()]
    assert all(families.count(f) == 2 for f in set(families))
    assert len(set(families)) == 3


@pytest.mark.parametrize("resume_id", sorted(RESUMES))
def test_resume_has_a_tier_for_every_job_in_its_family(resume_id):
    resume = RESUMES[resume_id]
    family_jobs = {j.job_id for j in JOBS.values() if j.family == resume.family}
    assert set(resume.intended_tier) == family_jobs


@pytest.mark.parametrize("rubric_id", sorted(RUBRICS))
def test_rubric_competencies_have_aliases(rubric_id):
    """The keyword baseline can only match what the rubric lists."""
    for comp in RUBRICS[rubric_id].competencies:
        assert comp.aliases, f"{comp.competency_id} has no aliases"


@pytest.mark.parametrize("resume_id", sorted(RESUMES))
def test_render_is_deterministic_and_anonymous(resume_id):
    resume = RESUMES[resume_id]
    first, second = render_text(resume), render_text(resume)
    assert first == second
    assert first.startswith(CANONICAL_NAME_PLACEHOLDER)
    assert "@" not in first


def test_no_real_contact_details_in_data():
    """Only example.com emails (reserved) and the fixed fictional phone number may appear."""
    email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
    phone = re.compile(r"\+65\s?\d{4}\s?\d{4}")
    for path in DATA_DIR.rglob("*.yaml"):
        text = path.read_text(encoding="utf-8")
        for match in email.findall(text):
            assert match.endswith("@example.com"), f"{path.name}: {match}"
        for match in phone.findall(text):
            assert match == "+65 9000 0000", f"{path.name}: {match}"
