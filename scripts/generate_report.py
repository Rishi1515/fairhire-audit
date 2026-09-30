"""Write docs/final_report.md and docs/model_prompts.md from the saved results.

Usage:
    python scripts/generate_report.py

All numbers come from results/summary.json. The discussion section is read from
docs/discussion.md, which is written by hand for one specific run. If that run id
does not match the current results, the report says so instead of pairing old
words with new numbers.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fairhire.data_io import load_rubrics  # noqa: E402
from fairhire.rank_llm import SYSTEM_PROMPT, build_prompt  # noqa: E402

LABEL = {"keyword": "Keyword", "embedding": "Embedding", "embedding_sectioned": "Sectioned embedding",
         "llm_rubric": "LLM rubric"}
MIT = {"none": "", "anonymised": ", anonymised", "structured_evidence": ", evidence only"}
ATTR = {"name_cue": "Name", "career_gap": "Career break", "institution": "University", "formatting": "Formatting"}


def cond(r: dict) -> str:
    return LABEL[r["method"]] + MIT[r["mitigation"]]


def num(x, d=2) -> str:
    return "n/a" if x is None else f"{x:.{d}f}"


def sgn(x, d=2) -> str:
    return "n/a" if x is None else f"{x:+.{d}f}"


def pval(p) -> str:
    return "not testable" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def hypotheses(s: dict) -> list[str]:
    gaps, rel = s["gaps"], {(r["method"], r["mitigation"]): r for r in s["relevance"]}
    thr = s["settings"]["material_gap_points"]
    out = []
    base = [c for c in s["conditions"] if c["mitigation"] == "none"]
    passing = [LABEL[c["method"]] for c in base
               if all(r["share_material"] == 0 for r in gaps if r["method"] == c["method"] and r["mitigation"] == "none")]
    failing = [LABEL[c["method"]] for c in base if LABEL[c["method"]] not in passing]
    flipping = [LABEL[c["method"]] for c in base if LABEL[c["method"]] in passing and any(
        (r["flip_rate"] or 0) > 0 for r in gaps if r["method"] == c["method"] and r["mitigation"] == "none")]
    text = (f"**H1, identical evidence gets similar scores.** Held for {', '.join(passing) or 'no method'} in the sense "
            f"that no pair moved by more than {thr} points. Did not hold for {', '.join(failing) or 'any other method'}, "
            f"where at least one changed field moved scores by more than {thr} points.")
    if flipping:
        text += (f" Even gaps below the threshold still flipped some shortlist decisions for {', '.join(flipping)}, "
                 f"because candidates close to the cut-off can swap places.")
    out.append(text)
    kw, emb, ev = rel.get(("keyword", "none")), rel.get(("embedding", "none")), rel.get(("embedding", "structured_evidence"))
    if kw and emb:
        overlap = kw["tier_accuracy_low"] <= emb["tier_accuracy_high"]
        out.append(f"**H2, structured scoring agrees more with the rubric than raw similarity.** Keyword rubric "
                   f"scoring reached tier accuracy {num(kw['tier_accuracy'])} against {num(emb['tier_accuracy'])} for "
                   f"whole-resume embedding ({'intervals overlap' if overlap else 'intervals do not overlap'}). Scoring "
                   f"only the extracted evidence with embedding gave {num(ev['tier_accuracy']) if ev else 'n/a'}. "
                   f"Supported in direction, with the caveat that the intended tiers and the keyword lists share an author.")
    spread_anon = next((r for r in gaps if r["method"] == "embedding" and r["mitigation"] == "anonymised"
                        and r["comparison"] == "name_spread"), None)
    proxies = [r for r in gaps if r["method"] == "embedding" and r["mitigation"] == "anonymised"
               and r["attribute"] in ("career_gap", "institution") and r["mean_abs_gap"] > 0]
    if spread_anon:
        out.append(f"**H3, anonymisation reduces identity gaps but not proxies.** Name spread after anonymisation: "
                   f"{num(spread_anon['mean_abs_gap'])} points. Career-break and university changes still moved "
                   f"scores after anonymisation in {len(proxies)} of 2 comparisons. Consistent with H3.")
    llm = s["run"]["llm_status"]
    out.append("**H4, LLM scoring is persuasive but less stable.** " +
               ("Not tested: the LLM scorer was not run for this version." if llm == "not_run"
                else f"LLM status: {llm}. See the stability table."))
    return out


def report(s: dict) -> str:
    b, run, st = s["benchmark"], s["run"], s["settings"]
    lines = [
        "# FairHire Audit: final report",
        "",
        f"Run `{run['run_id']}`, benchmark v{b['benchmark_version']}, generated from `results/summary.json`. "
        f"Every number below is produced by `scripts/generate_report.py`; none is typed by hand.",
        "",
        "All resumes, names and employers in this study are fictional.",
        "",
        "## Question",
        "",
        "When two resumes show the same job-relevant evidence, do keyword, embedding and LLM ranking methods give them "
        "the same score? Which method agrees best with a rubric written before any method was run? Do anonymisation or "
        "evidence-only scoring reduce the differences, and at what cost?",
        "",
        "## Setup",
        "",
        f"- {b['n_base_resumes']} fictional base resumes across 3 job families, 2 jobs per family, 2 resumes per intended "
        f"tier per job.",
        f"- {b['n_samples']} scored variants and {b['n_pairs']} controlled pairs: "
        + ", ".join(f"{v} {ATTR[k].lower()}" for k, v in b["pairs_by_type"].items()) + ".",
        "- Methods and mitigations run: " + "; ".join(cond(c) for c in s["conditions"]) + ".",
        f"- LLM rubric scorer: {run['llm_status'].replace('_', ' ')}.",
        f"- Shortlist = top {st['shortlist_k']} of the 8 candidates for a job. Material gap = more than "
        f"{st['material_gap_points']} points. Confidence intervals: {st['bootstrap_resamples']} bootstrap resamples of "
        f"base resumes (seed {st['bootstrap_seed']}). Tests: Wilcoxon signed-rank on one value per base resume, Holm "
        f"adjustment across all {sum(r['p_holm'] is not None for r in s['gaps'])} testable comparisons.",
        f"- Code version `{run['code_version']}`, config SHA-256 `{run['config_sha256'][:16]}`, variants SHA-256 "
        f"`{run['variants_sha256'][:16]}`, run at {run['timestamp_utc']}.",
        "",
        "## Headline findings",
        "",
    ]
    for h in s["headlines"]:
        lines += [f"**{h['title']}.** {h['text']}", ""]

    lines += ["## 1. How much does one changed field move the score?", "",
              "Mean absolute gap in points with 95% confidence interval, signed gap for the main comparison, share of "
              "resume-job rows with a material gap, shortlist flip rate, and Holm-adjusted p-value.", ""]
    main = {"name_cue": "name_spread", "career_gap": "with_break_minus_without",
            "institution": "higher_minus_comparison", "formatting": "alternative_minus_standard"}
    rows = []
    for attr, comp in main.items():
        for r in (g for g in s["gaps"] if g["attribute"] == attr and g["comparison"] == comp):
            rows.append([ATTR[attr], cond(r), f"{num(r['mean_abs_gap'])} ({num(r['abs_low'])} to {num(r['abs_high'])})",
                         "spread" if r["mean_signed_gap"] is None else f"{sgn(r['mean_signed_gap'])} ({sgn(r['signed_low'])} to {sgn(r['signed_high'])})",
                         f"{r['share_material']:.0%}", "" if r["flip_rate"] is None else f"{r['flip_rate']:.0%}",
                         "" if r["mean_signed_gap"] is None else pval(r["p_holm"])])
    lines += [table(["Field", "Method", "Mean abs gap (95% CI)", "Signed gap (95% CI)", "Material", "Flips", "p (Holm)"], rows), ""]
    lines += ["Name comparisons by direction (positive means the first group scored higher):", ""]
    rows = [[cond(r), r["comparison"].replace("_", " "), f"{sgn(r['mean_signed_gap'])} ({sgn(r['signed_low'])} to {sgn(r['signed_high'])})",
             pval(r["p_holm"])] for r in s["gaps"] if r["attribute"] == "name_cue" and r["comparison"] != "name_spread"
            and r["mitigation"] == "none"]
    lines += [table(["Method", "Comparison", "Signed gap (95% CI)", "p (Holm)"], rows), ""]

    lines += ["## 2. Agreement with the intended tiers", ""]
    rows = [[cond(r), f"{num(r['tier_accuracy'])} ({num(r['tier_accuracy_low'])} to {num(r['tier_accuracy_high'])})",
             f"{num(r['spearman_mean'])} ({num(r['spearman_min'])} to {num(r['spearman_max'])})", str(r["n_cross_tier_pairs"])]
            for r in s["relevance"]]
    lines += [table(["Method", "Tier accuracy (95% CI)", "Spearman, mean (range over jobs)", "Pairs"], rows), "",
              "The reference is the intended tier set by the resume author. Human reference labels have not been "
              "collected yet (see `data/human_labels/README.md`).", ""]

    lines += ["## 3. Stability", ""]
    rows = [[cond(r), num(r["format_topk_jaccard"]), num(r["format_rank_spearman"]), str(r["repeat_runs"]),
             "deterministic" if r["deterministic"] else num(r["mean_within_sample_sd"])] for r in s["stability"]]
    lines += [table(["Method", "Top-4 overlap after reformatting", "Rank agreement after reformatting", "Runs",
                     "Spread across runs"], rows), ""]

    lines += ["## 4. Mitigations", ""]
    rows = []
    for c in s["conditions"]:
        g = {r["comparison"]: r for r in s["gaps"] if r["method"] == c["method"] and r["mitigation"] == c["mitigation"]}
        rel = next(r for r in s["relevance"] if r["method"] == c["method"] and r["mitigation"] == c["mitigation"])
        rows.append([cond(c), num(rel["tier_accuracy"]), num(g["name_spread"]["mean_abs_gap"]),
                     num(g["with_break_minus_without"]["mean_abs_gap"]), num(g["higher_minus_comparison"]["mean_abs_gap"]),
                     num(g["alternative_minus_standard"]["mean_abs_gap"])])
    lines += [table(["Method", "Tier accuracy", "Name spread", "Career break", "University", "Formatting"], rows), ""]

    lines += ["## 5. Hypotheses", ""] + [h + "\n" for h in hypotheses(s)]
    lines += ["## 6. Failure cases", "", "Selected by fixed rules in `src/fairhire/evaluate.py`, not by hand.", ""]
    for c in s["failure_cases"]:
        lines.append(f"- **{c['case_id']}** ({cond(c)}, {c['job_id']}): {c.get('explanation', '')}")
    lines.append("")

    disc_path = REPO / "docs" / "discussion.md"
    disc = disc_path.read_text(encoding="utf-8") if disc_path.exists() else ""
    m = re.search(r"^run_id:\s*(\S+)", disc, re.MULTILINE)
    lines += ["## 7. Discussion", ""]
    if m and m.group(1) == run["run_id"] and s["run"]["variants_sha256"][:16] in disc:
        lines.append(disc.split("---", 2)[2].strip())
    else:
        lines.append("The written discussion in `docs/discussion.md` belongs to a different run, so it is not shown. "
                     "Update it for this run before quoting any interpretation.")
    lines += ["", "## Reproduce", "", "```bash", "pip install -r requirements.txt", "python scripts/download_model.py",
              "python scripts/build_dataset.py", "python scripts/run_experiment.py", "python scripts/analyse_results.py",
              "python scripts/generate_report.py", "python scripts/build_site.py", "pytest", "```", ""]
    return "\n".join(lines)


def prompts_doc(models: dict) -> str:
    rubric = load_rubrics()["DA-01"]
    example = (REPO / "tests" / "fixtures" / "llm" / "fixture_resume.txt").read_text(encoding="utf-8")
    llm = models["llm_rubric"]
    return "\n".join([
        "# Model prompts and parameters", "",
        "Generated by `scripts/generate_report.py` from `src/fairhire/rank_llm.py` and `config/models.yaml`, so it "
        "always matches the code.", "",
        "## LLM rubric scorer", "",
        f"- Model: `{llm['model']}`", f"- Temperature: {llm['temperature']}", f"- Repetitions per input: {llm['repetitions']}",
        f"- Maximum output tokens: {llm['max_output_tokens']}",
        f"- Strict evidence rule: {llm['strict_evidence']} (when true, a non-zero level without a quote invalidates the reply)",
        "- The overall score is computed from the per-competency levels with the rubric weights, never taken from the model.",
        "- Parser statuses: ok, uncited_nonzero, invalid_json, schema_error, competency_mismatch, empty, not_run.",
        "- Every call is cached in `results/llm_cache/` with the prompt, parameters, raw reply and token counts.", "",
        "### System prompt", "", "```text", SYSTEM_PROMPT, "```", "",
        "### User prompt, filled with a fixture resume that is not part of the benchmark", "",
        "```text", build_prompt(example, rubric, "Data Analyst, Retail Operations"), "```", "",
        "## Embedding model", "",
        f"- Model: `{models['embedding']['model']}` (ONNX), source `{models['embedding']['source_repo']}` at commit "
        f"`{models['embedding']['source_commit']}`",
        f"- SHA-256: " + ", ".join(f"`{k}` {v}" for k, v in models["embedding"]["sha256"].items()),
        "- Text is split at line breaks into pieces of at most 254 word pieces, embedded with mean pooling, averaged "
        "(weighted by piece length) and normalised. Score = 100 x cosine similarity, floored at 0.",
        f"- Section weights for the sectioned variant: {models['embedding']['sectioned_weights']}", "",
    ])


def main() -> None:
    import yaml

    s = json.loads((REPO / "results" / "summary.json").read_text(encoding="utf-8"))
    (REPO / "docs" / "final_report.md").write_text(report(s), encoding="utf-8")
    models = yaml.safe_load((REPO / "config" / "models.yaml").read_text(encoding="utf-8"))
    (REPO / "docs" / "model_prompts.md").write_text(prompts_doc(models), encoding="utf-8")
    print("wrote docs/final_report.md and docs/model_prompts.md")


if __name__ == "__main__":
    main()
