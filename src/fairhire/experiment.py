"""Score every sample with every method and mitigation, and save the raw scores.

One row per (sample, method, mitigation, repetition). Nothing is summarised
here; the analysis in ``evaluate.py`` reads only the saved file, so every
number in the report and website traces back to these rows.
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from fairhire import __version__
from fairhire.anonymise import anonymise
from fairhire.data_io import CONFIG_DIR, REPO_ROOT
from fairhire.evidence import structured_evidence
from fairhire.rank_embedding import MiniLMEncoder, score_embedding, score_sectioned
from fairhire.rank_keyword import score_keyword
from fairhire.rank_llm import LLMScorer
from fairhire.render_resumes import render_sections, render_text
from fairhire.schemas import JobDescription, Rubric, VariantRecord

RESULT_FIELDS = ["sample_id", "base_resume_id", "job_id", "tier", "transformation_type", "transformation_value",
                 "method", "mitigation", "repetition", "score", "parser_status", "model_id", "evidence_validity"]

# (method, mitigation) combinations run for the deterministic methods.
LOCAL_CONDITIONS = [("keyword", "none"), ("embedding", "none"), ("embedding", "anonymised"),
                    ("embedding", "structured_evidence"), ("embedding_sectioned", "none"),
                    ("embedding_sectioned", "anonymised")]
LLM_CONDITIONS = [("llm_rubric", "none"), ("llm_rubric", "anonymised"), ("llm_rubric", "structured_evidence")]


@dataclass
class ScoreRow:
    sample: VariantRecord
    method: str
    mitigation: str
    repetition: int
    score: Optional[float]
    parser_status: str = "ok"
    model_id: str = ""
    evidence_validity: Optional[float] = None

    def as_dict(self) -> dict[str, Any]:
        s = self.sample
        return {"sample_id": s.sample_id, "base_resume_id": s.base_resume_id, "job_id": s.job_id,
                "tier": s.qualification_tier.value, "transformation_type": s.transformation_type.value,
                "transformation_value": s.transformation_value, "method": self.method,
                "mitigation": self.mitigation, "repetition": self.repetition,
                "score": "" if self.score is None else f"{self.score:.6f}", "parser_status": self.parser_status,
                "model_id": self.model_id,
                "evidence_validity": "" if self.evidence_validity is None else f"{self.evidence_validity:.4f}"}


def input_text(sample: VariantRecord, mitigation: str, rubric: Rubric) -> str:
    """The text a method sees under a mitigation."""
    if mitigation == "anonymised":
        return render_text(anonymise(sample.resume))
    if mitigation == "structured_evidence":
        return structured_evidence(sample.resume, rubric)
    return render_text(sample.resume)


def score_local(samples: Iterable[VariantRecord], jobs: dict[str, JobDescription], rubrics: dict[str, Rubric],
                encoder: MiniLMEncoder, section_weights: dict[str, float],
                progress: Callable[[str], None] = lambda _: None) -> list[ScoreRow]:
    """Keyword and embedding scores. Deterministic, so repetition is always 0."""
    rows: list[ScoreRow] = []
    samples = list(samples)
    for i, s in enumerate(samples):
        job, rubric = jobs[s.job_id], rubrics[s.job_id]
        for method, mitigation in LOCAL_CONDITIONS:
            if method == "keyword":
                score, _ = score_keyword(s.resume, rubric)
            elif method == "embedding":
                score = score_embedding(encoder, input_text(s, mitigation, rubric), job)
            else:
                resume = anonymise(s.resume) if mitigation == "anonymised" else s.resume
                score, _ = score_sectioned(encoder, render_sections(resume), job, section_weights)
            rows.append(ScoreRow(s, method, mitigation, 0, score, model_id=_model_id(method)))
        if (i + 1) % 60 == 0:
            progress(f"scored {i + 1}/{len(samples)} samples")
    return rows


def score_llm(samples: Iterable[VariantRecord], jobs: dict[str, JobDescription], rubrics: dict[str, Rubric],
              scorer: LLMScorer) -> list[ScoreRow]:
    """LLM scores from cache or API. Missing results are kept as rows with status not_run."""
    rows: list[ScoreRow] = []
    for s in samples:
        rubric, job = rubrics[s.job_id], jobs[s.job_id]
        for method, mitigation in LLM_CONDITIONS:
            text = input_text(s, mitigation, rubric)
            for rep in range(scorer.config.repetitions):
                parsed, record = scorer.score(text, rubric, job.title, rep)
                rows.append(ScoreRow(s, method, mitigation, rep, parsed.score, parsed.status,
                                     (record or {}).get("model", scorer.config.model), parsed.evidence_validity))
    return rows


def _model_id(method: str) -> str:
    return "" if method == "keyword" else "sentence-transformers/all-MiniLM-L6-v2 (onnx)"


def write_scores(rows: list[ScoreRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())


def code_version() -> str:
    """Git commit if the repository has one, otherwise a hash of the source files."""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        digest = hashlib.sha256()
        for path in sorted((REPO_ROOT / "src").rglob("*.py")):
            digest.update(path.read_bytes())
        return f"no-git:src-sha256:{digest.hexdigest()[:16]}"


def run_metadata(run_id: str, manifest: dict[str, Any], models_cfg: dict[str, Any], llm_rows: int,
                 llm_status: str) -> dict[str, Any]:
    config_hash = hashlib.sha256(b"".join(p.read_bytes() for p in sorted(CONFIG_DIR.glob("*.yaml")))).hexdigest()
    return {"run_id": run_id, "results_schema_version": RESULTS_SCHEMA_VERSION, "package_version": __version__,
            "code_version": code_version(), "benchmark_version": manifest["benchmark_version"],
            "variants_sha256": manifest["variants_sha256"], "config_sha256": config_hash,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "python": platform.python_version(), "models": models_cfg, "llm_rows": llm_rows, "llm_status": llm_status}


RESULTS_SCHEMA_VERSION = "1"


def save_run(rows: list[ScoreRow], metadata: dict[str, Any], results_dir: Path) -> Path:
    """Write scores and metadata to results/runs/<run_id>/ and copy them to results/ as the current run."""
    run_dir = results_dir / "runs" / metadata["run_id"]
    write_scores(rows, run_dir / "scores.csv")
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    write_scores(rows, results_dir / "scores.csv")
    (results_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return run_dir
