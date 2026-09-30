"""Write result tables, a machine-readable summary and the headline findings.

Everything here is computed from results/scores.csv. Headline sentences are
chosen by fixed rules from the numbers (for example, a difference is only
called "detectable" when its Holm-adjusted p-value is below alpha), so the
wording cannot drift away from the data.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Optional

from fairhire.evaluate import (ScoreTable, failure_cases, gap_table, human_relevance_table, load_scores,
                               relevance_table, stability_table)

SUMMARY_VERSION = "1"

METRIC_DEFINITIONS = {
    "signed_gap": "Score of the changed version minus the score of the original version, for the same resume and job. "
                  "Positive means the change raised the score.",
    "abs_gap": "How far the score moved, ignoring direction.",
    "name_spread": "For one resume and job, the highest score minus the lowest score across the six names.",
    "share_material": "Share of resume-job rows where the score moved by more than the material threshold.",
    "flip_rate": "Share of resume-job rows where the shortlist decision (top 4 of 8 candidates) changed "
                 "because of the single changed field.",
    "tier_accuracy": "For every two candidates in different intended tiers, the share where the stronger one "
                     "scored higher (ties count as half).",
    "spearman": "Rank correlation between scores and intended tier order, from -1 to 1.",
    "p_holm": "Wilcoxon signed-rank p-value on one value per base resume, adjusted for the number of tests "
              "with the Holm method.",
    "format_topk_jaccard": "Overlap between the top 4 candidates under standard and alternative formatting "
                           "(1 means the same shortlist).",
}


def _fmt(x: Optional[float], digits: int = 1) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def _find(rows: list[dict], **kw: Any) -> Optional[dict]:
    return next((r for r in rows if all(r.get(k) == v for k, v in kw.items())), None)


def headline_findings(relevance: list[dict], gaps: list[dict], alpha: float, material: float,
                      cases: Optional[list[dict]] = None) -> list[dict[str, str]]:
    """Three findings in plain language, each chosen by a rule from the numbers."""
    out = []
    spread = _find(gaps, method="embedding", mitigation="none", comparison="name_spread")
    name_rows = [r for r in gaps if r["method"] == "embedding" and r["mitigation"] == "none"
                 and r["attribute"] == "name_cue" and r["comparison"] != "name_spread"]
    detectable = [r for r in name_rows if r["p_holm"] is not None and r["p_holm"] < alpha]
    if spread:
        direction = ("Some groups were scored consistently differently: " + ", ".join(
                         r["comparison"].replace("_", " ") for r in detectable) + "."
                     if detectable else
                     "No gender or group was consistently favoured. The scores moved around rather than leaning "
                     "one way.")
        out.append({"title": "Names changed the scores of one method",
                    "text": f"When only the name changed, the meaning-matching method's score for the same resume "
                            f"moved by {_fmt(spread['mean_abs_gap'])} points out of 100 on average (up to "
                            f"{_fmt(spread['max_abs_gap'])}). That was enough to change who made the top 4 in "
                            f"{spread['flip_rate']:.0%} of cases. " + direction})
    emb = _find(relevance, method="embedding", mitigation="none")
    anon = _find(relevance, method="embedding", mitigation="anonymised")
    gap_anon = _find(gaps, method="embedding", mitigation="anonymised", comparison="with_break_minus_without")
    fmt_anon = _find(gaps, method="embedding", mitigation="anonymised", comparison="alternative_minus_standard")
    if emb and anon and gap_anon and fmt_anon:
        better = anon["tier_accuracy"] > emb["tier_accuracy"]
        out.append({"title": "Hiding names fixed the name problem only",
                    "text": f"When names and emails were hidden before scoring, the name effect disappeared"
                            + (f" and the method got better at ranking stronger candidates above weaker ones "
                               f"({emb['tier_accuracy']:.0%} of the time before, {anon['tier_accuracy']:.0%} after)."
                               if better else ".")
                            + f" A career break still moved scores by {_fmt(gap_anon['mean_abs_gap'])} points on "
                              f"average, and changing the section order by {_fmt(fmt_anon['mean_abs_gap'])}."})
    kw = _find(relevance, method="keyword", mitigation="none")
    kw_gaps = [r for r in gaps if r["method"] == "keyword"]
    if kw and emb:
        invariant = all(r["max_abs_gap"] == 0 for r in kw_gaps)
        best = max(relevance, key=lambda r: r["tier_accuracy"])
        text = (f"Keyword counting {'gave the same score to both versions in every pair' if invariant else 'changed some pair scores'}. "
                f"It ranked stronger candidates above weaker ones {kw['tier_accuracy']:.0%} of the time, against "
                f"{emb['tier_accuracy']:.0%} for meaning-matching. Its word lists and the intended strong-to-weak order "
                f"were written by the same person, which helps it.")
        inversion = next((c for c in (cases or []) if c["kind"] == "tier_inversion" and c["method"] == "keyword"), None)
        if inversion and "explanation" in inversion:
            text += f" It still made mistakes. {inversion['explanation']}"
        out.append({"title": "Keyword counting never moved, but it can be fooled" if best is kw and invariant
                    else "Keyword counting had its own problems", "text": text})
    return out


def write_csv(rows: list[dict], path: Path, drop: tuple[str, ...] = ()) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [k for k in rows[0] if k not in drop] if rows else []
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6f}" if isinstance(v, float) else ("" if v is None else v)) for k, v in r.items()
                        if k in fields})


def long_metrics(relevance: list[dict], gaps: list[dict], stability: list[dict]) -> list[dict[str, Any]]:
    """Everything in one long table: table, method, mitigation, subject, metric, value, low, high, n."""
    out = []
    for r in relevance:
        out.append(dict(table="relevance", method=r["method"], mitigation=r["mitigation"], subject="intended_tier",
                        metric="tier_accuracy", value=r["tier_accuracy"], low=r["tier_accuracy_low"],
                        high=r["tier_accuracy_high"], n=r["n_cross_tier_pairs"]))
        out.append(dict(table="relevance", method=r["method"], mitigation=r["mitigation"], subject="intended_tier",
                        metric="spearman_mean", value=r["spearman_mean"], low=r["spearman_min"],
                        high=r["spearman_max"], n=r["n_jobs"]))
    for r in gaps:
        subj = f"{r['attribute']}:{r['comparison']}"
        base = dict(table="pair_gaps", method=r["method"], mitigation=r["mitigation"], subject=subj)
        if r["mean_signed_gap"] is not None:
            out.append({**base, "metric": "mean_signed_gap", "value": r["mean_signed_gap"], "low": r["signed_low"],
                        "high": r["signed_high"], "n": r["n_base_resumes"]})
        out.append({**base, "metric": "mean_abs_gap", "value": r["mean_abs_gap"], "low": r["abs_low"],
                    "high": r["abs_high"], "n": r["n_base_resumes"]})
        out.append({**base, "metric": "share_material", "value": r["share_material"], "low": None, "high": None,
                    "n": r["n_resume_job_rows"]})
        if r["flip_rate"] is not None:
            out.append({**base, "metric": "flip_rate", "value": r["flip_rate"], "low": None, "high": None,
                        "n": r["n_flip_rows"]})
        if r["p_holm"] is not None:
            out.append({**base, "metric": "p_holm", "value": r["p_holm"], "low": None, "high": None,
                        "n": r["n_base_resumes"]})
    for r in stability:
        base = dict(table="stability", method=r["method"], mitigation=r["mitigation"], subject="formatting", low=None, high=None, n=6)
        out.append({**base, "metric": "format_topk_jaccard", "value": r["format_topk_jaccard"]})
        out.append({**base, "metric": "mean_within_sample_sd", "value": r["mean_within_sample_sd"],
                    "subject": "repeat_runs", "n": r["repeat_runs"]})
    return out


def build_summary(scores_path: Path, metadata: dict, manifest: dict, analysis_cfg: dict, k: int,
                  seed: int, explain_case=None, human_scores: Optional[dict] = None) -> dict[str, Any]:
    t = ScoreTable(load_scores(scores_path))
    n_boot, material, alpha = analysis_cfg["bootstrap_resamples"], analysis_cfg["material_gap_points"], analysis_cfg["alpha"]
    relevance = relevance_table(t, seed, n_boot)
    gaps = gap_table(t, material, k, seed, n_boot)
    stability = stability_table(t, k)
    cases = failure_cases(t, gaps, k)
    if explain_case is not None:
        cases = [explain_case(c) for c in cases]
    return {"summary_version": SUMMARY_VERSION, "run": metadata, "benchmark": manifest,
            "settings": {"shortlist_k": k, "material_gap_points": material, "alpha": alpha,
                         "bootstrap_resamples": n_boot, "bootstrap_seed": seed},
            "definitions": METRIC_DEFINITIONS,
            "conditions": [{"method": c.method, "mitigation": c.mitigation} for c in t.conditions],
            "headlines": headline_findings(relevance, gaps, alpha, material, cases),
            "relevance": relevance, "human_relevance": human_relevance_table(t, human_scores or {}),
            "n_human_labelled": len(human_scores or {}), "gaps": gaps, "stability": stability, "failure_cases": cases}


def write_outputs(summary: dict[str, Any], results_dir: Path) -> None:
    tables = results_dir / "tables"
    write_csv(summary["relevance"], tables / "relevance.csv", drop=("per_job",))
    per_job = [{"method": r["method"], "mitigation": r["mitigation"], "job_id": j, **v}
               for r in summary["relevance"] for j, v in r["per_job"].items()]
    write_csv(per_job, tables / "relevance_by_job.csv")
    write_csv(summary["gaps"], tables / "pair_gaps.csv")
    write_csv(summary["stability"], tables / "stability.csv")
    write_csv(long_metrics(summary["relevance"], summary["gaps"], summary["stability"]), results_dir / "final_metrics.csv")
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
