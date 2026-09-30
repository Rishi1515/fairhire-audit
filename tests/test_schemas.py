"""The schemas must reject the mistakes that would quietly break the benchmark."""

import copy

import pytest
import yaml
from pydantic import ValidationError

from fairhire.data_io import DATA_DIR
from fairhire.schemas import CanonicalResume, JobDescription, Rubric, to_months


def _raw(folder: str, name: str) -> dict:
    return yaml.safe_load((DATA_DIR / folder / name).read_text(encoding="utf-8"))


@pytest.fixture
def rubric_raw() -> dict:
    return _raw("rubrics", "RUB-DA-01.yaml")


@pytest.fixture
def resume_raw() -> dict:
    return _raw("canonical_resumes", "DA-R01.yaml")


def test_to_months_rejects_bad_format():
    assert to_months("2024-01") - to_months("2023-12") == 1
    with pytest.raises(ValueError):
        to_months("2024-13")


def test_rubric_weights_must_sum_to_one(rubric_raw):
    rubric_raw["competencies"][0]["weight"] += 0.05
    with pytest.raises(ValidationError, match="sum to"):
        Rubric.model_validate(rubric_raw)


def test_rubric_rejects_unknown_keys(rubric_raw):
    rubric_raw["culture_fit"] = 0.1
    with pytest.raises(ValidationError):
        Rubric.model_validate(rubric_raw)


def test_rubric_needs_five_to_eight_competencies(rubric_raw):
    rubric_raw["competencies"] = rubric_raw["competencies"][:4]
    with pytest.raises(ValidationError):
        Rubric.model_validate(rubric_raw)


def test_job_prefix_must_match_family():
    raw = _raw("jobs", "DA-01.yaml")
    raw["family"] = "software_engineer"
    with pytest.raises(ValidationError, match="prefix"):
        JobDescription.model_validate(raw)


def test_canonical_resume_cannot_carry_a_name(resume_raw):
    resume_raw["identity"] = {"name": "Test Person"}
    with pytest.raises(ValidationError, match="must not contain a name"):
        CanonicalResume.model_validate(resume_raw)


def test_overlapping_roles_are_rejected(resume_raw):
    bad = copy.deepcopy(resume_raw)
    bad["experience"][1]["end"] = "2023-05"  # overlaps the role that starts 2023-03
    with pytest.raises(ValidationError, match="overlaps"):
        CanonicalResume.model_validate(bad)


def test_education_after_first_job_is_rejected(resume_raw):
    resume_raw["education"][0]["end"] = "2022-06"
    with pytest.raises(ValidationError, match="education ends after"):
        CanonicalResume.model_validate(resume_raw)


def test_tier_for_job_outside_family_is_rejected(resume_raw):
    resume_raw["intended_tier"]["SE-01"] = "weak"
    with pytest.raises(ValidationError, match="outside its family"):
        CanonicalResume.model_validate(resume_raw)


def test_months_of_experience(resume_raw):
    resume = CanonicalResume.model_validate(resume_raw)
    # Jul 2021 to Feb 2023 is 20 months; Mar 2023 to Sep 2026 is 43 months
    assert resume.months_of_experience("2026-09") == 63
