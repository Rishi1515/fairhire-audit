"""Create a blank scoring sheet for the applicant's blind rubric labels.

Usage:
    python scripts/make_scoring_sheet.py

Writes data/human_labels/scoring_sheet_blank.csv with one row per resume, job and
competency, and data/human_labels/resumes_to_score.md with each resume shown
without a name, in a shuffled order and without its intended tier. Score each row
0 to 3 using the rubric scale, save the filled file as applicant_scores.csv, then
run scripts/analyse_results.py again.
"""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fairhire.data_io import load_jobs, load_resumes, load_rubrics  # noqa: E402
from fairhire.render_resumes import render_text  # noqa: E402

OUT = REPO / "data" / "human_labels"


def main() -> None:
    jobs, rubrics, resumes = load_jobs(), load_rubrics(), load_resumes()
    order = sorted(resumes)
    random.Random(20260929).shuffle(order)  # so tiers are not in a predictable order
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "scoring_sheet_blank.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["resume_id", "job_id", "competency_id", "competency_name", "weight", "level", "note"])
        for rid in order:
            for job in sorted(resumes[rid].intended_tier):
                for c in rubrics[job].competencies:
                    w.writerow([rid, job, c.competency_id, c.name, f"{c.weight:.2f}", "", ""])
    parts = ["# Resumes to score", "", "Score each resume against both jobs in its family before looking at any "
             "model result, the review sheet or the design notes, so the scores stay blind. Levels: 0 no evidence, "
             "1 mentioned only, 2 applied, 3 applied with depth and a stated outcome. A skill that appears only in the "
             "skills list is at most 1.", "", "## Rubrics", ""]
    for job in jobs.values():
        parts += [f"### {job.job_id} {job.title}", ""]
        parts += [f"- `{c.competency_id}` {c.name} (weight {c.weight:.2f}): {' '.join(c.observable_evidence)}"
                  for c in rubrics[job.job_id].competencies]
        parts.append("")
    parts += ["## Resumes", ""]
    for rid in order:
        r = resumes[rid]
        parts += [f"### {rid} (score for {', '.join(jobs[j].job_id + ' ' + jobs[j].title for j in sorted(r.intended_tier))})",
                  "", "```text", render_text(r).rstrip(), "```", ""]
    (OUT / "resumes_to_score.md").write_text("\n".join(parts), encoding="utf-8")
    print("wrote data/human_labels/scoring_sheet_blank.csv and resumes_to_score.md")


if __name__ == "__main__":
    main()
