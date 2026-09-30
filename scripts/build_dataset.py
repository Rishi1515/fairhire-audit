"""Build the frozen benchmark: variants, pairs and a manifest.

Usage:
    python scripts/build_dataset.py          # variants, pairs, manifest
    python scripts/build_dataset.py --pdf    # also render the 24 reference resumes as PDFs

Reads data/jobs, data/rubrics, data/canonical_resumes and config/experiment.yaml.
Writes data/generated_pairs/{variants.jsonl, pairs.jsonl, manifest.json}.
Running it twice gives byte-identical files.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fairhire.data_io import GENERATED_DIR, load_config, load_jobs, load_resumes, source_file_hashes  # noqa: E402
from fairhire.generate_pairs import build_benchmark, write_benchmark  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="store_true", help="render reference resumes to data/rendered_pdf/")
    args = parser.parse_args()
    cfg = load_config()
    records, pairs, ref_groups = build_benchmark(load_resumes(), load_jobs(), cfg)
    manifest = write_benchmark(records, pairs, ref_groups, GENERATED_DIR, cfg, source_file_hashes())
    print(f"benchmark {manifest['benchmark_version']}: {manifest['n_base_resumes']} base resumes, "
          f"{manifest['n_samples']} samples, {manifest['n_pairs']} pairs {manifest['pairs_by_type']}")
    print("all pairs passed the integrity check")
    if args.pdf:
        from fairhire.render_pdf import render_pdf

        out = GENERATED_DIR.parent / "rendered_pdf"
        refs = {r.base_resume_id: r for r in records if r.sample_id.endswith("-REF")}
        for base_id, rec in sorted(refs.items()):
            render_pdf(rec.resume, out / f"{base_id}.pdf")
        print(f"rendered {len(refs)} PDFs to {out.relative_to(GENERATED_DIR.parents[1])}")


if __name__ == "__main__":
    main()
