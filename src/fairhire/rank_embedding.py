"""Method 2: embedding similarity with all-MiniLM-L6-v2.

The model runs locally through ONNX Runtime, so no API key or GPU is needed.
The model accepts at most 256 word pieces, which is shorter than a resume, so
text is split at line breaks into chunks that fit, each chunk is embedded,
and the chunk vectors are averaged (weighted by their length) and normalised.

Score = 100 * cosine similarity between the job description and the resume,
floored at 0. The number is a comparison score for ranking, not a probability
or a percentage match.

Section-aware variant: each resume section is embedded separately and the
cosine similarities are combined with the weights in ``config/models.yaml``,
so experience and skills count more than the header or education.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from fairhire.data_io import REPO_ROOT
from fairhire.schemas import JobDescription

MODEL_DIR = REPO_ROOT / "models" / "all-MiniLM-L6-v2"
MAX_TOKENS = 256
CHUNK_BUDGET = MAX_TOKENS - 2  # room for the [CLS] and [SEP] tokens


class ModelMissingError(FileNotFoundError):
    """Raised when the model files have not been downloaded yet."""


def job_text(job: JobDescription) -> str:
    """The job description as one plain-text document."""
    parts = [job.title, job.summary.strip(), "Responsibilities:"] + [f"- {r}" for r in job.responsibilities]
    parts += ["Requirements:"] + [f"- {r}" for r in job.requirements]
    if job.nice_to_have:
        parts += ["Nice to have:"] + [f"- {r}" for r in job.nice_to_have]
    return "\n".join(parts)


class MiniLMEncoder:
    """Sentence embeddings from the local ONNX export of all-MiniLM-L6-v2."""

    def __init__(self, model_dir: Path = MODEL_DIR) -> None:
        onnx_path, tok_path = model_dir / "model.onnx", model_dir / "tokenizer.json"
        if not onnx_path.exists() or not tok_path.exists():
            raise ModelMissingError(f"Model files not found in {model_dir}. Run: python scripts/download_model.py")
        import onnxruntime as ort
        from tokenizers import Tokenizer

        options = ort.SessionOptions()
        options.intra_op_num_threads = 1  # single thread keeps results bit-for-bit repeatable
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(onnx_path), sess_options=options, providers=["CPUExecutionProvider"])
        self.tokenizer = Tokenizer.from_file(str(tok_path))
        self.tokenizer.no_padding()
        self.tokenizer.enable_truncation(MAX_TOKENS)
        self._cache: dict[str, np.ndarray] = {}

    def _count(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False).ids)

    def chunks(self, text: str) -> list[str]:
        """Split text at line breaks into pieces of at most CHUNK_BUDGET word pieces."""
        out, current, size = [], [], 0
        for line in (ln for ln in text.splitlines() if ln.strip()):
            n = self._count(line)
            if current and size + n > CHUNK_BUDGET:
                out.append("\n".join(current))
                current, size = [], 0
            current.append(line)
            size += n
        if current:
            out.append("\n".join(current))
        return out or [""]

    def _embed_one(self, text: str) -> tuple[np.ndarray, int]:
        enc = self.tokenizer.encode(text)
        ids = np.array([enc.ids], dtype=np.int64)
        mask = np.array([enc.attention_mask], dtype=np.int64)
        types = np.array([enc.type_ids], dtype=np.int64)
        tokens = self.session.run(["token_embeddings"],
                                  {"input_ids": ids, "attention_mask": mask, "token_type_ids": types})[0]
        pooled = (tokens * mask[..., None]).sum(axis=1) / mask.sum(axis=1, keepdims=True)
        return pooled[0], int(mask.sum())

    def embed(self, text: str) -> np.ndarray:
        """Unit-length embedding of any length of text."""
        key = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if key not in self._cache:
            vectors, weights = zip(*(self._embed_one(c) for c in self.chunks(text)))
            vec = np.average(np.stack(vectors), axis=0, weights=np.array(weights, dtype=float))
            self._cache[key] = vec / np.linalg.norm(vec)
        return self._cache[key]

    def similarity(self, a: str, b: str) -> float:
        return float(self.embed(a) @ self.embed(b))


def score_embedding(encoder: MiniLMEncoder, resume_text: str, job: JobDescription) -> float:
    return round(max(0.0, 100.0 * encoder.similarity(resume_text, job_text(job))), 6)


def score_sectioned(encoder: MiniLMEncoder, sections: dict[str, str], job: JobDescription,
                    weights: dict[str, float]) -> tuple[float, dict[str, float]]:
    """Weighted section similarities. Returns (score, similarity per section)."""
    jt = job_text(job)
    sims = {name: encoder.similarity(sections[name], jt) for name in weights}
    total = sum(weights.values())
    score = 100.0 * sum(weights[n] * sims[n] for n in weights) / total
    return round(max(0.0, score), 6), sims
