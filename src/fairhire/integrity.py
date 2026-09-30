"""Pair integrity: prove that two variants differ only where they are allowed to.

Each transformation type has a list of permitted field paths (see
``schemas.PERMITTED_FIELDS``). We delete those paths from both resumes, hash
what is left, and require the hashes to match. We also require that the full
records are different, so a pair can never be accidentally identical.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from fairhire.schemas import PERMITTED_FIELDS, Resume, TransformationType


class PairIntegrityError(AssertionError):
    """Raised when a pair differs outside its permitted fields, or not at all."""


def _delete_path(node: Any, parts: list[str]) -> None:
    head, rest = parts[0], parts[1:]
    if head.endswith("[]"):
        items = node.get(head[:-2], [])
        for item in items:
            if rest:
                _delete_path(item, rest)
        if not rest:
            node.pop(head[:-2], None)
        return
    if "[" in head:  # e.g. education[0]
        key, idx = head[:-1].split("[")
        items = node.get(key, [])
        if int(idx) < len(items):
            if rest:
                _delete_path(items[int(idx)], rest)
        return
    if rest:
        if head in node:
            _delete_path(node[head], rest)
    else:
        node.pop(head, None)


def strip_permitted(resume: Resume, transformation: TransformationType) -> dict:
    """Return the resume as a dict with the transformation's permitted fields removed."""
    data = copy.deepcopy(resume.model_dump(mode="json"))
    for path in PERMITTED_FIELDS[transformation]:
        _delete_path(data, path.split("."))
    return data


def content_hash(resume: Resume, transformation: TransformationType) -> str:
    """SHA-256 of everything a transformation is not allowed to touch."""
    stripped = strip_permitted(resume, transformation)
    return hashlib.sha256(json.dumps(stripped, sort_keys=True).encode("utf-8")).hexdigest()


def check_pair(a: Resume, b: Resume, transformation: TransformationType) -> None:
    """Raise ``PairIntegrityError`` unless a and b differ only in permitted fields."""
    if content_hash(a, transformation) != content_hash(b, transformation):
        raise PairIntegrityError(f"pair differs outside the fields permitted for {transformation.value}")
    if a.model_dump(mode="json") == b.model_dump(mode="json"):
        raise PairIntegrityError("pair members are identical, so the pair tests nothing")
