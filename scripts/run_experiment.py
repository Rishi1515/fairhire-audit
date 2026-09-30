"""Run the experiment and save raw scores.

Usage:
    python scripts/run_experiment.py            # full run: all 480 samples
    python scripts/run_experiment.py --demo     # quick check: 2 base resumes only
    python scripts/run_experiment.py --llm      # also run the LLM scorer (needs ANTHROPIC_API_KEY)
    python scripts/run_experiment.py --llm-cost # print the estimated LLM cost and stop

Without --llm, any LLM outputs already in results/llm_cache are still used, so
saved outputs can be re-analysed without paying for new calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from fairhire.data_io import GENERATED_DIR, load_config, load_jobs, load_rubrics, load_variants  # noqa: E402
from fairhire.experiment import (run_metadata, save_run, score_llm, score_local, input_text,  # noqa: E402
                                 LLM_CONDITIONS)
from fairhire.rank_embedding import MiniLMEncoder  # noqa: E402
from fairhire.rank_llm import LLMConfig, LLMScorer, build_prompt, make_client  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--demo", action="store_true", help="score only the first two base resumes")
    parser.add_argument("--llm", action="store_true", help="call the LLM API for missing outputs")
    parser.add_argument("--llm-cost", action="store_true", help="estimate LLM cost and exit")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    models = load_config("models.yaml")
    manifest = json.loads((GENERATED_DIR / "manifest.json").read_text(encoding="utf-8"))
    jobs, rubrics, variants = load_jobs(), load_rubrics(), load_variants()
    samples = sorted(variants.values(), key=lambda v: v.sample_id)
    if args.demo:
        keep = sorted({s.base_resume_id for s in samples})[:2]
        samples = [s for s in samples if s.base_resume_id in keep]

    llm_cfg = LLMConfig.from_yaml(models["llm_rubric"])
    client = make_client() if args.llm else None
    if args.llm and client is None:
        sys.exit("ANTHROPIC_API_KEY is not set. Put it in your environment, or run without --llm.")
    scorer = LLMScorer(llm_cfg, REPO / models["llm_rubric"]["cache_dir"], client)

    if args.llm_cost:
        prompts = [build_prompt(input_text(s, m, rubrics[s.job_id]), rubrics[s.job_id], jobs[s.job_id].title)
                   for s in samples for _, m in LLM_CONDITIONS]
        print(json.dumps(scorer.estimate_cost(prompts), indent=2))
        return

    print(f"scoring {len(samples)} samples with keyword and embedding methods")
    rows = score_local(samples, jobs, rubrics, MiniLMEncoder(), models["embedding"]["sectioned_weights"], print)
    llm_rows = score_llm(samples, jobs, rubrics, scorer)
    done = sum(r.parser_status != "not_run" for r in llm_rows)
    llm_status = "not_run" if done == 0 else ("complete" if done == len(llm_rows) else f"partial ({done}/{len(llm_rows)})")
    print(f"LLM scorer: {llm_status}")
    rows += [r for r in llm_rows if r.parser_status != "not_run"]

    run_id = args.run_id or ("demo" if args.demo else f"run-{manifest['benchmark_version']}")
    meta = run_metadata(run_id, manifest, models, done, llm_status)
    meta["demo"] = args.demo
    run_dir = save_run(rows, meta, REPO / "results")
    print(f"saved {len(rows)} score rows to {run_dir.relative_to(REPO)} and results/scores.csv")


if __name__ == "__main__":
    main()
