"""Load and validate benchmark data files from ``data/``."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, ValidationError

from fairhire.schemas import CanonicalResume, JobDescription, Rubric

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

M = TypeVar("M", bound=BaseModel)


class DataFileError(ValueError):
    """Raised when a data file cannot be parsed or fails validation."""


def load_yaml_model(path: Path, model: type[M]) -> M:
    """Parse one YAML file into ``model``, naming the file in any error."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise DataFileError(f"{path.name}: invalid YAML: {exc}") from exc
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        raise DataFileError(f"{path.name}: {exc}") from exc


def _load_dir(folder: Path, model: type[M]) -> list[M]:
    return [load_yaml_model(p, model) for p in sorted(folder.glob("*.yaml"))]


def load_jobs(data_dir: Path = DATA_DIR) -> dict[str, JobDescription]:
    return {j.job_id: j for j in _load_dir(data_dir / "jobs", JobDescription)}


def load_rubrics(data_dir: Path = DATA_DIR) -> dict[str, Rubric]:
    """Rubrics keyed by job_id. Exactly one rubric per job is expected."""
    rubrics: dict[str, Rubric] = {}
    for rubric in _load_dir(data_dir / "rubrics", Rubric):
        if rubric.job_id in rubrics:
            raise DataFileError(f"two rubrics found for {rubric.job_id}")
        rubrics[rubric.job_id] = rubric
    return rubrics


def load_resumes(data_dir: Path = DATA_DIR) -> dict[str, CanonicalResume]:
    return {r.resume_id: r for r in _load_dir(data_dir / "canonical_resumes", CanonicalResume)}


CONFIG_DIR = REPO_ROOT / "config"
GENERATED_DIR = DATA_DIR / "generated_pairs"


def load_config(name: str = "experiment.yaml") -> dict:
    """Load a YAML config file from ``config/``."""
    return yaml.safe_load((CONFIG_DIR / name).read_text(encoding="utf-8"))


def source_file_hashes(data_dir: Path = DATA_DIR) -> dict[str, str]:
    """SHA-256 of every job, rubric and canonical resume file, keyed by relative path."""
    import hashlib

    out = {}
    for folder in ("jobs", "rubrics", "canonical_resumes"):
        for path in sorted((data_dir / folder).glob("*.yaml")):
            out[f"{folder}/{path.name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    cfg = CONFIG_DIR / "experiment.yaml"
    out["config/experiment.yaml"] = hashlib.sha256(cfg.read_bytes()).hexdigest()
    return out


def load_variants(path: Path = GENERATED_DIR / "variants.jsonl"):
    """Load generated variant records keyed by sample_id."""
    from fairhire.schemas import VariantRecord

    if not path.exists():
        raise DataFileError(f"{path} not found. Run: python scripts/build_dataset.py")
    records = [VariantRecord.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return {r.sample_id: r for r in records}


def load_pairs(path: Path = GENERATED_DIR / "pairs.jsonl"):
    from fairhire.schemas import PairRecord

    if not path.exists():
        raise DataFileError(f"{path} not found. Run: python scripts/build_dataset.py")
    return [PairRecord.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines()]
