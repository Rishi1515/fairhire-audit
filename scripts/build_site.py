"""Build the evidence browser from the frozen result files.

Usage:
    python scripts/build_site.py

Reads results/summary.json, results/scores.csv, data/generated_pairs/ and the
job and rubric files, and writes one self-contained page to site/index.html.
No number is typed into the page: every figure is read from the embedded data,
which is copied from the result files at build time.

The page refuses to render if the summary was produced by an incompatible
version of the analysis code.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fairhire.data_io import GENERATED_DIR, load_config, load_jobs, load_rubrics, load_variants  # noqa: E402
from fairhire.render_resumes import render_text  # noqa: E402
from fairhire.reporting import SUMMARY_VERSION  # noqa: E402

TEMPLATE = REPO / "site_src" / "template.html"
OUT_DIR = REPO / "site"


class IncompatibleResultsError(RuntimeError):
    """The result files do not match what this version of the site expects."""


def load_summary(path: Path) -> dict:
    summary = json.loads(path.read_text(encoding="utf-8"))
    if summary.get("summary_version") != SUMMARY_VERSION:
        raise IncompatibleResultsError(
            f"results/summary.json has summary_version {summary.get('summary_version')!r}, "
            f"but this site expects {SUMMARY_VERSION!r}. Re-run scripts/analyse_results.py.")
    return summary


def site_data(summary: dict) -> dict:
    manifest = json.loads((GENERATED_DIR / "manifest.json").read_text(encoding="utf-8"))
    if summary["run"]["variants_sha256"] != manifest["variants_sha256"]:
        raise IncompatibleResultsError("summary.json was built from a different benchmark than data/generated_pairs.")
    variants, jobs, rubrics = load_variants(), load_jobs(), load_rubrics()
    cfg = load_config()

    texts: list[str] = []
    text_index: dict[str, int] = {}
    samples = {}
    for sid, v in sorted(variants.items()):
        text = render_text(v.resume)
        if text not in text_index:
            text_index[text] = len(texts)
            texts.append(text)
        samples[sid] = [v.base_resume_id, v.job_id, v.qualification_tier.value, v.transformation_type.value,
                        v.transformation_value, text_index[text]]

    scores: dict[str, dict[str, float]] = {}
    with (REPO / "results" / "scores.csv").open(encoding="utf-8") as fh:
        acc: dict[tuple[str, str], list[float]] = {}
        for row in csv.DictReader(fh):
            if row["score"]:
                acc.setdefault((f"{row['method']}|{row['mitigation']}", row["sample_id"]), []).append(float(row["score"]))
    for (cond, sid), vals in acc.items():
        scores.setdefault(cond, {})[sid] = round(sum(vals) / len(vals), 2)

    return {
        "version": SUMMARY_VERSION,
        "summary": summary,
        "jobs": [{"job_id": j.job_id, "family": j.family.value, "title": j.title, "employer": j.employer,
                  "competencies": [{"name": c.name, "weight": c.weight, "importance": c.importance.value}
                                   for c in rubrics[j.job_id].competencies]}
                 for j in jobs.values()],
        "samples": samples,
        "texts": texts,
        "scores": scores,
        "transformations": cfg["transformations"],
        "scope": cfg["scope"],
        "models": load_config("models.yaml"),
    }


def build(summary_path: Path = REPO / "results" / "summary.json", out_dir: Path = OUT_DIR) -> Path:
    data = site_data(load_summary(summary_path))
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8").replace("__SITE_DATA__", blob)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
                                        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, "
                                        "viewport-fit=cover\">\n" + page + "\n</body>\n</html>\n", encoding="utf-8")
    # The same page without the document wrapper, for hosts that add their own.
    (out_dir / "fragment.html").write_text(page.replace("</head>\n<body>", ""), encoding="utf-8")
    return out_dir / "index.html"


if __name__ == "__main__":
    try:
        path = build()
    except IncompatibleResultsError as exc:
        sys.exit(str(exc))
    print(f"wrote {path.relative_to(REPO)} ({path.stat().st_size // 1024} KB)")
