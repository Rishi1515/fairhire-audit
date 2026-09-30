"""The LLM parser must handle valid, invalid, partial and missing replies."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from fairhire.data_io import load_rubrics
from fairhire.rank_llm import LLMConfig, LLMScorer, build_prompt, parse_response

FIXTURES = Path(__file__).parent / "fixtures" / "llm"
RESUME = (FIXTURES / "fixture_resume.txt").read_text()
RUBRIC = load_rubrics()["DA-01"]
IDS = [c.competency_id for c in RUBRIC.competencies]


def reply(levels: dict[str, int], evidence: dict[str, list[str]] | None = None) -> str:
    evidence = evidence or {}
    return json.dumps({"competencies": [{"competency_id": i, "level": levels.get(i, 0),
                                         "evidence": evidence.get(i, []), "missing_evidence": ""} for i in IDS],
                       "uncertainty": "medium", "recommendation": "hold", "rationale": "fixture"})


def test_valid_reply_is_scored_with_rubric_weights():
    raw = reply({"sql": 3, "dashboarding": 2}, {"sql": ["Wrote SQL queries joining orders and customers tables"],
                                                 "dashboarding": ["Built a Tableau dashboard"]})
    parsed = parse_response(raw, RUBRIC, RESUME)
    assert parsed.status == "ok"
    assert parsed.score == pytest.approx(100 * (0.25 * 3 / 3 + 0.20 * 2 / 3))
    assert parsed.evidence_validity == 1.0


def test_code_fenced_reply_is_accepted():
    parsed = parse_response("Here you go:\n```json\n" + reply({}) + "\n```", RUBRIC, RESUME)
    assert parsed.status == "ok" and parsed.score == 0


@pytest.mark.parametrize("raw,status", [
    (None, "empty"), ("   ", "empty"), ("not json at all", "invalid_json"), ('{"competencies": [', "invalid_json"),
    ('{"competencies": [], "uncertainty": "unsure", "recommendation": "hold"}', "schema_error"),
])
def test_bad_replies_get_a_status_not_a_score(raw, status):
    parsed = parse_response(raw, RUBRIC, RESUME)
    assert parsed.status == status and parsed.score is None


def test_out_of_range_level_is_a_schema_error():
    raw = reply({"sql": 5})
    assert parse_response(raw, RUBRIC, RESUME).status == "schema_error"


def test_missing_competency_is_rejected():
    data = json.loads(reply({}))
    data["competencies"] = data["competencies"][:-1]
    assert parse_response(json.dumps(data), RUBRIC, RESUME).status == "competency_mismatch"


def test_uncited_nonzero_level_is_flagged_and_strict_mode_rejects_it():
    raw = reply({"sql": 2})
    assert parse_response(raw, RUBRIC, RESUME).status == "uncited_nonzero"
    strict = parse_response(raw, RUBRIC, RESUME, strict_evidence=True)
    assert strict.status == "uncited_nonzero" and strict.score is None


def test_invented_quotes_lower_evidence_validity():
    raw = reply({"sql": 2, "dashboarding": 2}, {"sql": ["Wrote SQL queries joining orders and customers tables"],
                                                 "dashboarding": ["Led a team of 20 BI engineers"]})
    assert parse_response(raw, RUBRIC, RESUME).evidence_validity == 0.5


class FakeClient:
    """Stands in for the Anthropic client; counts calls."""

    def __init__(self, text: str) -> None:
        self.calls = 0
        self.messages = SimpleNamespace(create=self._create)
        self.text = text

    def _create(self, **kwargs):
        self.calls += 1
        return SimpleNamespace(content=[SimpleNamespace(text=self.text)], model=kwargs["model"],
                               usage=SimpleNamespace(input_tokens=100, output_tokens=50))


def config() -> LLMConfig:
    return LLMConfig(model="fixture-model", temperature=1.0, max_output_tokens=500, repetitions=2,
                     price_per_mtok_input=1.0, price_per_mtok_output=5.0)


def test_scorer_caches_and_reuses_outputs(tmp_path):
    client = FakeClient(reply({}))
    scorer = LLMScorer(config(), tmp_path, client)
    first, record = scorer.score(RESUME, RUBRIC, "Data Analyst", 0)
    again, _ = scorer.score(RESUME, RUBRIC, "Data Analyst", 0)
    assert client.calls == 1 and first.score == again.score == 0
    assert record["prompt"] == build_prompt(RESUME, RUBRIC, "Data Analyst") and record["raw_response"]
    scorer.score(RESUME, RUBRIC, "Data Analyst", 1)
    assert client.calls == 2  # a new repetition is a new call


def test_scorer_without_key_or_cache_returns_not_run(tmp_path):
    parsed, record = LLMScorer(config(), tmp_path, None).score(RESUME, RUBRIC, "Data Analyst", 0)
    assert parsed.status == "not_run" and record is None


def test_cost_estimate_counts_repetitions(tmp_path):
    est = LLMScorer(config(), tmp_path, None).estimate_cost([build_prompt(RESUME, RUBRIC, "Data Analyst")] * 3)
    assert est["calls"] == 6 and est["usd"] > 0
