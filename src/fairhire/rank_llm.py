"""Method 3: an LLM rubric scorer with strict output validation.

The model is asked for a level (0 to 3) per competency, exact quotes from the
resume as evidence, what evidence is missing, its uncertainty and a
recommendation. The overall score is NOT taken from the model: it is computed
from the per-competency levels with the rubric weights, using the same formula
as the keyword baseline, so all methods share one 0-100 scale.

Every call is cached on disk with its full prompt, parameters, raw response,
parser status and token counts. If no API key is set, the scorer reads the
cache only and returns ``not_run`` for anything missing. The rest of the
project never depends on this module being able to call an API.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from fairhire.schemas import Rubric

SYSTEM_PROMPT = """You score resumes against a job rubric for a research benchmark on automated screening.
Rules:
1. Score only what is written in the resume. Do not credit skills the resume does not support.
2. Do not infer or consider gender, ethnicity, religion, age, nationality or any other personal attribute.
   The candidate's name, university name and career breaks must not change any score.
3. For every competency with a level above 0, quote one or more exact phrases from the resume as evidence.
4. Reply with a single JSON object and nothing else."""

USER_TEMPLATE = """JOB: {job_title}

RUBRIC (level scale: {scale})
{competencies}

RESUME
<<<
{resume}
>>>

Return JSON with exactly this shape:
{{"competencies": [{{"competency_id": "<id>", "level": <0-3>, "evidence": ["<exact quote>"], "missing_evidence": "<short text>"}}],
 "uncertainty": "low" | "medium" | "high",
 "recommendation": "advance" | "hold" | "reject",
 "rationale": "<at most 60 words>"}}
Include every competency id listed above exactly once."""


def build_prompt(resume_text: str, rubric: Rubric, job_title: str) -> str:
    scale = "; ".join(f"{s.level} = {s.meaning}" for s in rubric.scale)
    comps = "\n".join(f"- {c.competency_id} ({c.name}, weight {c.weight:.2f}): look for "
                      + " ".join(c.observable_evidence) for c in rubric.competencies)
    return USER_TEMPLATE.format(job_title=job_title, scale=scale, competencies=comps, resume=resume_text.strip())


# --------------------------------------------------------------------------- parsing


class CompetencyJudgement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    competency_id: str
    level: int = Field(ge=0, le=3)
    evidence: list[str] = Field(default_factory=list)
    missing_evidence: str = ""


class LLMJudgement(BaseModel):
    model_config = ConfigDict(extra="ignore")
    competencies: list[CompetencyJudgement]
    uncertainty: Literal["low", "medium", "high"]
    recommendation: Literal["advance", "hold", "reject"]
    rationale: str = ""


@dataclass
class ParsedScore:
    status: str  # ok | uncited_nonzero | invalid_json | schema_error | competency_mismatch | empty | not_run
    score: Optional[float] = None
    levels: dict[str, int] = field(default_factory=dict)
    judgement: Optional[LLMJudgement] = None
    evidence_total: int = 0
    evidence_found: int = 0

    @property
    def evidence_validity(self) -> Optional[float]:
        return self.evidence_found / self.evidence_total if self.evidence_total else None


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _extract_json(raw: str) -> Any:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    return json.loads(text[start:end + 1])


def parse_response(raw: Optional[str], rubric: Rubric, resume_text: str, strict_evidence: bool = False) -> ParsedScore:
    """Validate a raw model reply and turn it into a score.

    ``strict_evidence`` is the optional consistency rule: a non-zero level
    without a quote makes the whole response invalid instead of just flagged.
    """
    if raw is None or not raw.strip():
        return ParsedScore("empty")
    try:
        data = _extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        return ParsedScore("invalid_json")
    try:
        judgement = LLMJudgement.model_validate(data)
    except ValidationError:
        return ParsedScore("schema_error")
    expected = [c.competency_id for c in rubric.competencies]
    got = [c.competency_id for c in judgement.competencies]
    if sorted(got) != sorted(expected):
        return ParsedScore("competency_mismatch", judgement=judgement)

    levels = {c.competency_id: c.level for c in judgement.competencies}
    haystack = _normalise(resume_text)
    quotes = [q for c in judgement.competencies for q in c.evidence if q.strip()]
    found = sum(_normalise(q) in haystack for q in quotes)
    uncited = any(c.level > 0 and not [q for q in c.evidence if q.strip()] for c in judgement.competencies)
    status = "uncited_nonzero" if uncited else "ok"
    if uncited and strict_evidence:
        return ParsedScore(status, None, levels, judgement, len(quotes), found)
    score = 100.0 * sum(c.weight * levels[c.competency_id] / 3 for c in rubric.competencies)
    return ParsedScore(status, round(score, 6), levels, judgement, len(quotes), found)


# --------------------------------------------------------------------------- calling and caching


class MessageClient(Protocol):
    """The small part of the Anthropic client this module uses (easy to fake in tests)."""

    messages: Any


@dataclass
class LLMConfig:
    model: str
    temperature: float
    max_output_tokens: int
    repetitions: int
    price_per_mtok_input: float
    price_per_mtok_output: float
    strict_evidence: bool = False

    @classmethod
    def from_yaml(cls, cfg: dict[str, Any]) -> "LLMConfig":
        return cls(model=cfg["model"], temperature=cfg["temperature"], max_output_tokens=cfg["max_output_tokens"],
                   repetitions=cfg["repetitions"], price_per_mtok_input=cfg["price_per_mtok_input"],
                   price_per_mtok_output=cfg["price_per_mtok_output"], strict_evidence=cfg.get("strict_evidence", False))


def make_client() -> Optional[MessageClient]:
    """Return an Anthropic client if ANTHROPIC_API_KEY is set, otherwise None."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    import anthropic

    return anthropic.Anthropic()


class LLMScorer:
    def __init__(self, config: LLMConfig, cache_dir: Path, client: Optional[MessageClient] = None) -> None:
        self.config, self.cache_dir, self.client = config, cache_dir, client
        cache_dir.mkdir(parents=True, exist_ok=True)

    def cache_key(self, prompt: str, repetition: int) -> str:
        c = self.config
        blob = json.dumps([c.model, c.temperature, c.max_output_tokens, SYSTEM_PROMPT, prompt, repetition])
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def call(self, prompt: str, repetition: int) -> Optional[dict[str, Any]]:
        """Return the cached record for this prompt and repetition, calling the API if needed and possible."""
        path = self.cache_dir / f"{self.cache_key(prompt, repetition)}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if self.client is None:
            return None
        c = self.config
        response = self.client.messages.create(model=c.model, max_tokens=c.max_output_tokens,
                                               temperature=c.temperature, system=SYSTEM_PROMPT,
                                               messages=[{"role": "user", "content": prompt}])
        raw = "".join(getattr(block, "text", "") for block in response.content)
        record = {"model": getattr(response, "model", c.model), "requested_model": c.model,
                  "temperature": c.temperature, "max_output_tokens": c.max_output_tokens, "repetition": repetition,
                  "system": SYSTEM_PROMPT, "prompt": prompt, "raw_response": raw,
                  "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        path.write_text(json.dumps(record, indent=1), encoding="utf-8")
        return record

    def score(self, resume_text: str, rubric: Rubric, job_title: str, repetition: int) -> tuple[ParsedScore, Optional[dict]]:
        prompt = build_prompt(resume_text, rubric, job_title)
        record = self.call(prompt, repetition)
        if record is None:
            return ParsedScore("not_run"), None
        return parse_response(record["raw_response"], rubric, resume_text, self.config.strict_evidence), record

    def estimate_cost(self, prompts: list[str]) -> dict[str, float]:
        """Rough cost of running every prompt for every repetition (about 4 characters per token)."""
        c = self.config
        calls = len(prompts) * c.repetitions
        tokens_in = sum(len(SYSTEM_PROMPT) + len(p) for p in prompts) / 4 * c.repetitions
        tokens_out = calls * 700
        usd = tokens_in / 1e6 * c.price_per_mtok_input + tokens_out / 1e6 * c.price_per_mtok_output
        return {"calls": calls, "input_tokens": round(tokens_in), "output_tokens": tokens_out, "usd": round(usd, 2)}
