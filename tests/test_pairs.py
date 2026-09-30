"""Counterfactual pairs must differ only in their permitted fields."""

import json

import pytest

from fairhire.anonymise import anonymise
from fairhire.data_io import GENERATED_DIR, load_config, load_jobs, load_resumes
from fairhire.generate_pairs import build_benchmark, insert_career_gap
from fairhire.integrity import PairIntegrityError, check_pair, content_hash
from fairhire.render_resumes import render_text
from fairhire.schemas import Resume, TransformationType as T

CFG = load_config()
RECORDS, PAIRS, REF_GROUPS = build_benchmark(load_resumes(), load_jobs(), CFG)
BY_ID = {r.sample_id: r for r in RECORDS}


def test_counts():
    assert len(REF_GROUPS) == 24
    assert len(RECORDS) == 24 * 2 * 10
    assert len(PAIRS) == 24 * 2 * 18


def test_every_pair_passes_integrity():
    for p in PAIRS:
        check_pair(BY_ID[p.sample_a].resume, BY_ID[p.sample_b].resume, p.transformation_type)


def test_pair_with_an_extra_change_is_rejected():
    p = next(p for p in PAIRS if p.transformation_type == T.NAME_CUE)
    a, b = BY_ID[p.sample_a].resume, BY_ID[p.sample_b].resume
    data = b.model_dump()
    data["experience"][0]["bullets"][0] += " Extra claim."
    with pytest.raises(PairIntegrityError, match="outside"):
        check_pair(a, Resume.model_validate(data), T.NAME_CUE)


def test_identical_pair_is_rejected():
    a = BY_ID[PAIRS[0].sample_a].resume
    with pytest.raises(PairIntegrityError, match="identical"):
        check_pair(a, a, T.NAME_CUE)


def test_name_change_is_not_allowed_in_a_career_gap_pair():
    ref = BY_ID["DA-R01-DA-01-REF"].resume
    gap = BY_ID["DA-R01-DA-01-GAP"].resume
    renamed = Resume.model_validate({**gap.model_dump(), "identity": {**gap.identity.model_dump(), "name": "Other Name"}})
    with pytest.raises(PairIntegrityError):
        check_pair(ref, renamed, T.CAREER_GAP)


def test_career_gap_keeps_total_experience_and_adds_twelve_months():
    for base_id in {r.base_resume_id for r in RECORDS}:
        ref = BY_ID[f"{base_id}-{sorted(load_resumes()[base_id].intended_tier)[0]}-REF"].resume
        gap = insert_career_gap(ref, 12, "Career break")
        assert gap.months_of_experience("2026-09") == ref.months_of_experience("2026-09")
        assert "Career break" in render_text(gap)


def test_generation_is_reproducible():
    again, pairs_again, _ = build_benchmark(load_resumes(), load_jobs(), CFG)
    assert [r.model_dump_json() for r in again] == [r.model_dump_json() for r in RECORDS]
    assert [p.model_dump_json() for p in pairs_again] == [p.model_dump_json() for p in PAIRS]


def test_saved_benchmark_matches_the_code():
    """Fails if data/generated_pairs is stale compared with the source files."""
    import hashlib

    manifest = json.loads((GENERATED_DIR / "manifest.json").read_text())
    fresh = "".join(r.model_dump_json() + "\n" for r in RECORDS)
    assert hashlib.sha256(fresh.encode()).hexdigest() == manifest["variants_sha256"]


def test_every_name_group_is_the_reference_equally_often():
    counts = {}
    for g in REF_GROUPS.values():
        counts[g] = counts.get(g, 0) + 1
    assert set(counts.values()) == {4}


def test_content_hash_ignores_only_permitted_fields():
    a = BY_ID["SE-R01-SE-01-INST-COMP"].resume
    b = BY_ID["SE-R01-SE-01-INST-HIGH"].resume
    assert content_hash(a, T.INSTITUTION) == content_hash(b, T.INSTITUTION)
    assert content_hash(a, T.NONE) != content_hash(b, T.NONE)


def test_anonymisation_removes_identity_but_keeps_evidence():
    name_samples = [r for r in RECORDS if r.base_resume_id == "MA-R03" and r.job_id == "MA-02"
                    and r.transformation_type in (T.NAME_CUE, T.NONE)]
    texts = {render_text(anonymise(r.resume)) for r in name_samples}
    assert len(texts) == 1  # all six names collapse to one text
    text = texts.pop()
    assert "@" not in text and "Candidate" in text.splitlines()[0]
    for bullet in name_samples[0].resume.experience[0].bullets:
        assert bullet in text
    assert name_samples[0].resume.education[0].institution in text
