"""Compute every result table from results/scores.csv.

Usage:
    python scripts/analyse_results.py

Writes results/tables/*.csv, results/final_metrics.csv and results/summary.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fairhire.data_io import GENERATED_DIR, load_config, load_rubrics, load_variants  # noqa: E402
from fairhire.evaluate import load_human_scores  # noqa: E402
from fairhire.failure_notes import explain  # noqa: E402
from fairhire.rank_embedding import MiniLMEncoder, ModelMissingError  # noqa: E402
from fairhire.reporting import build_summary, write_outputs  # noqa: E402


def main() -> None:
    cfg = load_config()
    results = REPO / "results"
    metadata = json.loads((results / "run_metadata.json").read_text(encoding="utf-8"))
    manifest = json.loads((GENERATED_DIR / "manifest.json").read_text(encoding="utf-8"))
    if metadata["variants_sha256"] != manifest["variants_sha256"]:
        sys.exit("The scores were produced from a different benchmark version. Re-run scripts/run_experiment.py.")
    variants, rubrics = load_variants(), load_rubrics()
    try:
        encoder = MiniLMEncoder()
    except ModelMissingError:
        encoder = None  # failure notes then skip the chunk-count check
    summary = build_summary(results / "scores.csv", metadata, manifest, cfg["analysis"],
                            cfg["scope"]["shortlist_k"], cfg["seeds"]["bootstrap"],
                            explain_case=lambda c: explain(c, variants, rubrics, encoder),
                            human_scores=load_human_scores(REPO / "data" / "human_labels" / "applicant_scores.csv", rubrics))
    write_outputs(summary, results)
    print(f"wrote results/summary.json with {len(summary['gaps'])} gap rows and "
          f"{len(summary['failure_cases'])} failure cases")
    for h in summary["headlines"]:
        print(f"- {h['title']}: {h['text']}")


if __name__ == "__main__":
    main()
