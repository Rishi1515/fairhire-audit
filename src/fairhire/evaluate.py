"""Turn saved scores into the result tables.

Input: results/scores.csv (one row per sample, method, mitigation, repetition).
Output: plain Python structures that ``reporting.py`` writes to CSV and JSON.

Definitions (also shown on the website next to each result):

* Signed gap: score of variant b minus score of variant a for the same base
  resume and job (for example, with a career break minus without).
* Absolute gap: the size of the signed gap, ignoring direction.
* Material gap: an absolute gap larger than ``material_gap_points``.
* Flip: the shortlist decision (top k of the 8 candidates for a job) changes
  between the two variants, with the other 7 candidates held at their
  reference versions.
* Tier accuracy: for every two candidates in different intended tiers, did
  the higher tier get the higher score? A tie counts as half.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Optional

from fairhire.statistics import (bootstrap_mean, holm, jaccard, pairwise_order_accuracy, spearman, wilcoxon_p)

TIER_ORDER = {"weak": 1, "borderline": 2, "good": 3, "strong": 4}
NAME_GROUPS = ["chinese_female", "chinese_male", "malay_female", "malay_male", "indian_female", "indian_male"]


@dataclass(frozen=True)
class Condition:
    method: str
    mitigation: str

    @property
    def label(self) -> str:
        return f"{self.method} / {self.mitigation}"


def load_scores(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["score"] = float(r["score"]) if r["score"] != "" else None
        r["repetition"] = int(r["repetition"])
    return rows


class ScoreTable:
    """Scores averaged over repetitions, indexed for fast lookup."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        acc: dict[tuple, list[float]] = defaultdict(list)
        self.meta: dict[str, dict[str, Any]] = {}
        for r in rows:
            if r["score"] is None:
                continue
            acc[(r["method"], r["mitigation"], r["sample_id"])].append(r["score"])
            self.meta[r["sample_id"]] = r
        self.mean = {k: mean(v) for k, v in acc.items()}
        self.reps = dict(acc)
        self.conditions = sorted({Condition(m, g) for m, g, _ in self.mean},
                                 key=lambda c: (c.method, c.mitigation != "none", c.mitigation))
        self.bases = sorted({r["base_resume_id"] for r in rows})
        self.jobs_of: dict[str, list[str]] = defaultdict(list)
        for base, job in sorted({(r["base_resume_id"], r["job_id"]) for r in rows}):
            self.jobs_of[base].append(job)
        self.tier = {(r["base_resume_id"], r["job_id"]): r["tier"] for r in rows}

    def get(self, cond: Condition, sample_id: str) -> Optional[float]:
        return self.mean.get((cond.method, cond.mitigation, sample_id))

    def sample_id(self, base: str, job: str, code: str) -> str:
        return f"{base}-{job}-{code}"

    def name_code(self, base: str, job: str, group: str) -> str:
        """Sample id for a name group; the reference group is stored as REF."""
        ref = self.sample_id(base, job, "REF")
        if self.meta.get(ref, {}).get("transformation_value") == group:
            return ref
        return self.sample_id(base, job, f"NAME-{group}")


# --------------------------------------------------------------------------- relevance


def load_human_scores(path: Path, rubrics: dict) -> dict[tuple[str, str], float]:
    """Applicant rubric scores per (base resume, job), on the same 0-100 formula as the methods.

    The CSV has columns resume_id, job_id, competency_id, level (0-3). Rows with an
    empty level are ignored; a resume-job is used only when every competency is scored.
    """
    if not path.exists():
        return {}
    levels: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["level"].strip() == "":
                continue
            level = int(row["level"])
            if not 0 <= level <= 3:
                raise ValueError(f"{path.name}: level must be 0 to 3, got {level}")
            levels[(row["resume_id"], row["job_id"])][row["competency_id"]] = level
    out = {}
    for (rid, job), lv in levels.items():
        comps = rubrics[job].competencies
        if all(c.competency_id in lv for c in comps):
            out[(rid, job)] = 100.0 * sum(c.weight * lv[c.competency_id] / 3 for c in comps)
    return out


def human_relevance_table(t: ScoreTable, human: dict[tuple[str, str], float]) -> list[dict[str, Any]]:
    """Spearman correlation between each method and the applicant's blind rubric scores, per job."""
    out = []
    if not human:
        return out
    jobs = sorted({j for (_, j) in human})
    for cond in t.conditions:
        per_job = {}
        for job in jobs:
            bases = [b for b in t.bases if (b, job) in human]
            scores = [t.get(cond, t.sample_id(b, job, "REF")) for b in bases]
            if len(bases) < 3 or None in scores:
                continue
            per_job[job] = spearman(scores, [human[(b, job)] for b in bases])
        vals = [v for v in per_job.values() if v is not None]
        if vals:
            out.append({"method": cond.method, "mitigation": cond.mitigation, "reference": "applicant_labels",
                        "n_jobs": len(vals), "spearman_mean": mean(vals), "spearman_min": min(vals),
                        "spearman_max": max(vals), "per_job": per_job})
    return out


def relevance_table(t: ScoreTable, seed: int, n_boot: int) -> list[dict[str, Any]]:
    out = []
    jobs = sorted({j for js in t.jobs_of.values() for j in js})
    for cond in t.conditions:
        pooled: list[float] = []
        rhos = []
        per_job = {}
        for job in jobs:
            bases = [b for b in t.bases if job in t.jobs_of[b]]
            scores = [t.get(cond, t.sample_id(b, job, "REF")) for b in bases]
            if any(s is None for s in scores):
                continue
            tiers = [TIER_ORDER[t.tier[(b, job)]] for b in bases]
            acc = pairwise_order_accuracy(scores, tiers)
            rho = spearman(scores, tiers)
            pooled += acc
            rhos.append(rho)
            per_job[job] = {"tier_accuracy": mean(acc), "spearman": rho}
        if not pooled:
            continue
        ci = bootstrap_mean(pooled, n_boot, seed)
        out.append({"method": cond.method, "mitigation": cond.mitigation, "reference": "intended_tier",
                    "n_jobs": len(per_job), "n_cross_tier_pairs": len(pooled),
                    "tier_accuracy": ci.estimate, "tier_accuracy_low": ci.low, "tier_accuracy_high": ci.high,
                    "spearman_mean": mean(r for r in rhos if r is not None),
                    "spearman_min": min(r for r in rhos if r is not None),
                    "spearman_max": max(r for r in rhos if r is not None), "per_job": per_job})
    return out


# --------------------------------------------------------------------------- pair gaps


def _diffs_name(t: ScoreTable, cond: Condition, base: str, job: str) -> dict[str, float]:
    s = {g: t.get(cond, t.name_code(base, job, g)) for g in NAME_GROUPS}
    if any(v is None for v in s.values()):
        return {}
    eth = ["chinese", "malay", "indian"]
    by = lambda e, g: s[f"{e}_{g}"]  # noqa: E731
    return {
        "female_minus_male": mean(by(e, "female") - by(e, "male") for e in eth),
        "malay_minus_chinese": mean(by("malay", g) - by("chinese", g) for g in ("female", "male")),
        "indian_minus_chinese": mean(by("indian", g) - by("chinese", g) for g in ("female", "male")),
        "indian_minus_malay": mean(by("indian", g) - by("malay", g) for g in ("female", "male")),
        "name_spread": max(s.values()) - min(s.values()),
    }


SIMPLE = {"career_gap": ("with_break_minus_without", "REF", "GAP"),
          "institution": ("higher_minus_comparison", "INST-COMP", "INST-HIGH"),
          "formatting": ("alternative_minus_standard", "REF", "FMT-ALT")}


def in_shortlist(t: ScoreTable, cond: Condition, sample_id: str, base: str, job: str, k: int) -> Optional[bool]:
    """Would this sample be in the top k if the other candidates keep their reference versions?"""
    own = t.get(cond, sample_id)
    if own is None:
        return None
    pool = [(own, base)]
    for other in t.bases:
        if other != base and job in t.jobs_of[other]:
            score = t.get(cond, t.sample_id(other, job, "REF"))
            if score is None:
                return None
            pool.append((score, other))
    ranked = sorted(pool, key=lambda x: (-x[0], x[1]))
    return [b for _, b in ranked].index(base) < k


def gap_table(t: ScoreTable, material: float, k: int, seed: int, n_boot: int) -> list[dict[str, Any]]:
    """One row per condition and comparison."""
    out = []
    for cond in t.conditions:
        per_comparison: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        flips: dict[str, list[bool]] = defaultdict(list)
        for base in t.bases:
            for job in t.jobs_of[base]:
                for comp, d in _diffs_name(t, cond, base, job).items():
                    per_comparison[("name_cue", comp)][base].append(d)
                decisions = {in_shortlist(t, cond, t.name_code(base, job, g), base, job, k) for g in NAME_GROUPS}
                if None not in decisions:
                    flips["name_cue"].append(len(decisions) > 1)
                for attr, (comp, a, b) in SIMPLE.items():
                    sa, sb = t.get(cond, t.sample_id(base, job, a)), t.get(cond, t.sample_id(base, job, b))
                    if sa is None or sb is None:
                        continue
                    per_comparison[(attr, comp)][base].append(sb - sa)
                    da = in_shortlist(t, cond, t.sample_id(base, job, a), base, job, k)
                    db = in_shortlist(t, cond, t.sample_id(base, job, b), base, job, k)
                    flips[attr].append(da != db)
        for (attr, comp), by_base in per_comparison.items():
            rows = [d for ds in by_base.values() for d in ds]
            unit_signed = [mean(ds) for ds in by_base.values()]
            unit_abs = [mean(abs(d) for d in ds) for ds in by_base.values()]
            signed_ci = bootstrap_mean(unit_signed, n_boot, seed)
            abs_ci = bootstrap_mean(unit_abs, n_boot, seed)
            is_spread = comp == "name_spread"
            flip_list = flips.get(attr, []) if (is_spread or attr != "name_cue") else []
            out.append({
                "method": cond.method, "mitigation": cond.mitigation, "attribute": attr, "comparison": comp,
                "n_base_resumes": len(unit_signed), "n_resume_job_rows": len(rows),
                "mean_signed_gap": None if is_spread else signed_ci.estimate,
                "signed_low": None if is_spread else signed_ci.low,
                "signed_high": None if is_spread else signed_ci.high,
                "mean_abs_gap": abs_ci.estimate, "abs_low": abs_ci.low, "abs_high": abs_ci.high,
                "max_abs_gap": max(abs(d) for d in rows),
                "share_material": mean(abs(d) > material for d in rows),
                "flip_rate": mean(flip_list) if flip_list else None, "n_flip_rows": len(flip_list),
                "p_wilcoxon": None if is_spread else wilcoxon_p(unit_signed),
            })
    adjusted = holm([r["p_wilcoxon"] for r in out])
    for r, p in zip(out, adjusted):
        r["p_holm"] = p
    return out


# --------------------------------------------------------------------------- stability


def stability_table(t: ScoreTable, k: int) -> list[dict[str, Any]]:
    """Formatting robustness for every condition, and repeat-run spread for the LLM."""
    out = []
    jobs = sorted({j for js in t.jobs_of.values() for j in js})
    for cond in t.conditions:
        overlaps, rhos = [], []
        for job in jobs:
            bases = [b for b in t.bases if job in t.jobs_of[b]]
            std = [t.get(cond, t.sample_id(b, job, "REF")) for b in bases]
            alt = [t.get(cond, t.sample_id(b, job, "FMT-ALT")) for b in bases]
            if None in std or None in alt:
                continue
            top = lambda sc: {b for _, b in sorted(zip(sc, bases), key=lambda x: (-x[0], x[1]))[:k]}  # noqa: E731
            overlaps.append(jaccard(top(std), top(alt)))
            rho = spearman(std, alt)
            rhos.append(rho if rho is not None else 1.0)
        rep_sd = [pstdev(v) for (m, g, _), v in t.reps.items() if (m, g) == (cond.method, cond.mitigation) and len(v) > 1]
        out.append({"method": cond.method, "mitigation": cond.mitigation,
                    "format_topk_jaccard": mean(overlaps) if overlaps else None,
                    "format_rank_spearman": mean(rhos) if rhos else None,
                    "repeat_runs": max((len(v) for (m, g, _), v in t.reps.items()
                                        if (m, g) == (cond.method, cond.mitigation)), default=0),
                    "mean_within_sample_sd": mean(rep_sd) if rep_sd else 0.0,
                    "deterministic": not rep_sd})
    return out


# --------------------------------------------------------------------------- failure cases


def failure_cases(t: ScoreTable, gaps: list[dict[str, Any]], k: int) -> list[dict[str, Any]]:
    """Pick concrete examples by fixed rules, so they are not hand-chosen to tell a story.

    Rules, for each method with no mitigation:
    1. The largest tier inversion: a lower-tier candidate scored above a higher-tier one by the most points.
    2. The largest single name gap.
    3. The largest single career-break gap and the largest single institution gap.
    4. Every shortlist flip caused by a single changed field.
    """
    cases = []
    base_conds = [c for c in t.conditions if c.mitigation == "none"]
    for cond in base_conds:
        best = None
        for job in sorted({j for js in t.jobs_of.values() for j in js}):
            bases = [b for b in t.bases if job in t.jobs_of[b]]
            for hi in bases:
                for lo in bases:
                    if TIER_ORDER[t.tier[(hi, job)]] <= TIER_ORDER[t.tier[(lo, job)]]:
                        continue
                    s_hi, s_lo = t.get(cond, t.sample_id(hi, job, "REF")), t.get(cond, t.sample_id(lo, job, "REF"))
                    if s_hi is None or s_lo is None:
                        continue
                    margin = s_lo - s_hi
                    if margin > 0 and (best is None or margin > best["margin"]):
                        best = {"kind": "tier_inversion", "method": cond.method, "mitigation": cond.mitigation,
                                "job_id": job, "margin": margin,
                                "higher_tier": {"sample_id": t.sample_id(hi, job, "REF"), "tier": t.tier[(hi, job)], "score": s_hi},
                                "lower_tier": {"sample_id": t.sample_id(lo, job, "REF"), "tier": t.tier[(lo, job)], "score": s_lo}}
        if best:
            cases.append(best)

        for attr, codes in [("name_cue", None), ("career_gap", ("REF", "GAP")), ("institution", ("INST-COMP", "INST-HIGH"))]:
            top = None
            for base in t.bases:
                for job in t.jobs_of[base]:
                    if codes is None:
                        cands = [(t.name_code(base, job, g1), t.name_code(base, job, g2))
                                 for i, g1 in enumerate(NAME_GROUPS) for g2 in NAME_GROUPS[i + 1:]]
                    else:
                        cands = [(t.sample_id(base, job, codes[0]), t.sample_id(base, job, codes[1]))]
                    for a, b in cands:
                        sa, sb = t.get(cond, a), t.get(cond, b)
                        if sa is None or sb is None:
                            continue
                        if top is None or abs(sb - sa) > abs(top["gap"]):
                            top = {"kind": f"largest_{attr}_gap", "method": cond.method, "mitigation": cond.mitigation,
                                   "job_id": job, "gap": sb - sa, "a": {"sample_id": a, "score": sa},
                                   "b": {"sample_id": b, "score": sb}}
            if top and abs(top["gap"]) > 0:
                cases.append(top)

        for base in t.bases:
            for job in t.jobs_of[base]:
                for attr, (_, a, b) in SIMPLE.items():
                    ia, ib = t.sample_id(base, job, a), t.sample_id(base, job, b)
                    da, db = in_shortlist(t, cond, ia, base, job, k), in_shortlist(t, cond, ib, base, job, k)
                    if da is not None and db is not None and da != db:
                        cases.append({"kind": "shortlist_flip", "method": cond.method, "mitigation": cond.mitigation,
                                      "job_id": job, "attribute": attr,
                                      "a": {"sample_id": ia, "score": t.get(cond, ia), "shortlisted": da},
                                      "b": {"sample_id": ib, "score": t.get(cond, ib), "shortlisted": db}})
                names = {g: in_shortlist(t, cond, t.name_code(base, job, g), base, job, k) for g in NAME_GROUPS}
                if None not in names.values() and len(set(names.values())) > 1:
                    cases.append({"kind": "shortlist_flip", "method": cond.method, "mitigation": cond.mitigation,
                                  "job_id": job, "attribute": "name_cue",
                                  "by_group": {g: {"sample_id": t.name_code(base, job, g),
                                                   "score": t.get(cond, t.name_code(base, job, g)), "shortlisted": v}
                                               for g, v in names.items()}})
    for i, c in enumerate(cases, 1):
        c["case_id"] = f"F{i:02d}"
    return cases
