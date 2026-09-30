"""Metric calculations checked against small hand-worked fixtures."""

import csv

import pytest

from fairhire.evaluate import Condition, ScoreTable, gap_table, in_shortlist, load_scores, relevance_table
from fairhire.statistics import bootstrap_mean, holm, jaccard, pairwise_order_accuracy, spearman, wilcoxon_p


def test_bootstrap_of_constant_values_is_exact():
    ci = bootstrap_mean([2.0] * 10, 500, seed=1)
    assert ci.estimate == ci.low == ci.high == 2.0


def test_bootstrap_is_seeded():
    assert bootstrap_mean([1, 2, 3, 9], 1000, 3) == bootstrap_mean([1, 2, 3, 9], 1000, 3)


def test_holm_matches_hand_calculation():
    # sorted p: 0.01*3=0.03, 0.02*2=0.04, 0.04*1=0.04 (monotone), None stays None
    assert holm([0.04, None, 0.01, 0.02]) == [pytest.approx(0.04), None, pytest.approx(0.03), pytest.approx(0.04)]


def test_wilcoxon_all_zero_is_none():
    assert wilcoxon_p([0, 0, 0]) is None
    assert 0 < wilcoxon_p([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]) < 0.05


def test_pairwise_order_accuracy():
    # tiers 3 > 2 > 1; scores rank 3rd above 2nd, but tie between 2nd and 1st
    assert pairwise_order_accuracy([10, 5, 5], [3, 2, 1]) == [1.0, 1.0, 0.5]
    assert pairwise_order_accuracy([1, 2], [2, 2]) == []


def test_spearman_and_jaccard():
    assert spearman([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)
    assert spearman([1, 1, 1], [1, 2, 3]) is None
    assert jaccard({1, 2}, {2, 3}) == pytest.approx(1 / 3)


def _write(tmp_path, rows):
    path = tmp_path / "scores.csv"
    fields = ["sample_id", "base_resume_id", "job_id", "tier", "transformation_type", "transformation_value",
              "method", "mitigation", "repetition", "score", "parser_status", "model_id", "evidence_validity"]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({f: r.get(f, "") for f in fields})
    return load_scores(path)


def _fixture(tmp_path, gap_delta: float):
    """Five candidates for one job; only base B2 gets a career gap effect of gap_delta."""
    tiers = {"B1": "strong", "B2": "good", "B3": "borderline", "B4": "weak", "B5": "weak"}
    base_scores = {"B1": 80, "B2": 60, "B3": 50, "B4": 40, "B5": 30}
    groups = ["chinese_female", "chinese_male", "malay_female", "malay_male", "indian_female", "indian_male"]
    rows = []
    for b, tier in tiers.items():
        s = base_scores[b]
        common = dict(base_resume_id=b, job_id="DA-01", tier=tier, method="m", mitigation="none", repetition=0)
        rows.append({**common, "sample_id": f"{b}-DA-01-REF", "transformation_type": "none",
                     "transformation_value": "chinese_female", "score": s})
        for g in groups[1:]:
            rows.append({**common, "sample_id": f"{b}-DA-01-NAME-{g}", "transformation_type": "name_cue",
                         "transformation_value": g, "score": s})
        for code, t, v, sc in [("GAP", "career_gap", "12", s + (gap_delta if b == "B2" else 0)),
                               ("INST-HIGH", "institution", "h", s), ("INST-COMP", "institution", "c", s),
                               ("FMT-ALT", "formatting", "a", s)]:
            rows.append({**common, "sample_id": f"{b}-DA-01-{code}", "transformation_type": t,
                         "transformation_value": v, "score": sc})
    return ScoreTable(_write(tmp_path, rows))


def test_gap_and_flip_on_fixture(tmp_path):
    t = _fixture(tmp_path, gap_delta=-25.0)
    cond = Condition("m", "none")
    # B2 is 2nd of 5 at 60; with k=2 it is shortlisted, and at 35 it drops to 4th
    assert in_shortlist(t, cond, "B2-DA-01-REF", "B2", "DA-01", 2) is True
    assert in_shortlist(t, cond, "B2-DA-01-GAP", "B2", "DA-01", 2) is False
    rows = {(r["attribute"], r["comparison"]): r for r in gap_table(t, material=2.0, k=2, seed=1, n_boot=200)}
    gap = rows[("career_gap", "with_break_minus_without")]
    assert gap["mean_signed_gap"] == pytest.approx(-25.0 / 5)
    assert gap["max_abs_gap"] == pytest.approx(25.0)
    assert gap["share_material"] == pytest.approx(1 / 5)
    assert gap["flip_rate"] == pytest.approx(1 / 5)
    assert rows[("name_cue", "name_spread")]["mean_abs_gap"] == 0


def test_relevance_on_fixture(tmp_path):
    t = _fixture(tmp_path, gap_delta=0)
    rel = relevance_table(t, seed=1, n_boot=200)[0]
    # all cross-tier pairs correctly ordered; B4 and B5 are both weak so they are not compared
    assert rel["tier_accuracy"] == pytest.approx(1.0)
    assert rel["n_cross_tier_pairs"] == 9
