"""Keyword and embedding scores must be bounded and deterministic."""

import pytest

from fairhire.data_io import load_jobs, load_rubrics, load_variants
from fairhire.rank_embedding import CHUNK_BUDGET, MiniLMEncoder, ModelMissingError, score_embedding, score_sectioned
from fairhire.rank_keyword import alias_pattern, competency_level, score_keyword
from fairhire.render_resumes import render_sections, render_text
from fairhire.schemas import Resume

JOBS, RUBRICS, VARIANTS = load_jobs(), load_rubrics(), load_variants()
SAMPLES = [VARIANTS[k] for k in sorted(VARIANTS)[::37]]  # a spread of samples


def test_keyword_bounded_and_deterministic():
    for s in SAMPLES:
        a, _ = score_keyword(s.resume, RUBRICS[s.job_id])
        b, _ = score_keyword(s.resume, RUBRICS[s.job_id])
        assert a == b and 0 <= a <= 100


def test_keyword_skills_list_only_caps_at_level_one():
    s = VARIANTS["DA-R03-DA-01-REF"]
    sql = next(c for c in RUBRICS["DA-01"].competencies if c.competency_id == "sql")
    # DA-R03 lists SQL in skills and in a project, but the project line says SQLite, not SQL
    level, lines = competency_level(s.resume, sql)
    assert level == 1 and lines == []


def test_keyword_plural_and_case_rules():
    assert alias_pattern("API").search("Built REST APIs")
    assert not alias_pattern("Go").search("go to the store")
    assert alias_pattern("Go").search("services written in Go")
    assert not alias_pattern("SQL").search("PostgreSQL only")


def test_keyword_is_blind_to_names():
    ids = [k for k in VARIANTS if k.startswith("SE-R02-SE-01-") and ("NAME" in k or k.endswith("REF"))]
    scores = {score_keyword(VARIANTS[i].resume, RUBRICS["SE-01"])[0] for i in ids}
    assert len(scores) == 1


def test_perfect_resume_scores_100():
    s = VARIANTS["DA-R06-DA-01-REF"].resume
    rubric = RUBRICS["DA-01"]
    bullets = [f"Used {c.aliases[0]} daily for reporting." for c in rubric.competencies]
    data = s.model_dump()
    data["experience"][0]["bullets"] = bullets[:6]
    data["experience"][1]["bullets"] = bullets[:6]
    score, levels = score_keyword(Resume.model_validate(data), rubric)
    assert score == pytest.approx(100.0) and set(levels.values()) == {3}


@pytest.fixture(scope="module")
def encoder():
    try:
        return MiniLMEncoder()
    except ModelMissingError:
        pytest.skip("model not downloaded; run scripts/download_model.py")


def test_embedding_reproduces_published_reference_values(encoder):
    """Values from the sentence-transformers quickstart for all-MiniLM-L6-v2."""
    s = ["The weather is lovely today.", "It's so sunny outside!", "He drove to the stadium."]
    assert encoder.similarity(s[0], s[1]) == pytest.approx(0.6660, abs=1e-4)
    assert encoder.similarity(s[0], s[2]) == pytest.approx(0.1046, abs=1e-4)
    assert encoder.similarity(s[1], s[2]) == pytest.approx(0.1411, abs=1e-4)


def test_embedding_chunks_fit_the_model(encoder):
    text = render_text(VARIANTS["DA-R06-DA-01-GAP"].resume)
    chunks = encoder.chunks(text)
    assert all(encoder._count(c) <= CHUNK_BUDGET for c in chunks)
    assert "".join(c.replace("\n", "") for c in chunks) == "".join(ln for ln in text.splitlines() if ln.strip())


def test_embedding_scores_bounded_and_deterministic(encoder):
    weights = {"header": 0.05, "summary": 0.1, "experience": 0.5, "skills": 0.25, "education": 0.1}
    for s in SAMPLES[:4]:
        fresh = MiniLMEncoder()
        a = score_embedding(encoder, render_text(s.resume), JOBS[s.job_id])
        b = score_embedding(fresh, render_text(s.resume), JOBS[s.job_id])
        assert a == b and 0 <= a <= 100
        c, sims = score_sectioned(encoder, render_sections(s.resume), JOBS[s.job_id], weights)
        assert 0 <= c <= 100 and set(sims) == set(weights)
