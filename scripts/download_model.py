"""Download the embedding model files and check them against pinned SHA-256 hashes.

Usage:
    python scripts/download_model.py

The files (about 90 MB) are fetched from a pinned commit of a public GitHub
repository that bundles an ONNX export of sentence-transformers/all-MiniLM-L6-v2.
That copy reproduces the model's published reference similarities exactly
(see tests/test_rankers.py). The files are not committed to this repository.
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
TARGET = REPO / "models" / "all-MiniLM-L6-v2"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    cfg = yaml.safe_load((REPO / "config" / "models.yaml").read_text(encoding="utf-8"))["embedding"]
    base = cfg["source_repo"].replace("https://github.com/", "https://raw.githubusercontent.com/")
    TARGET.mkdir(parents=True, exist_ok=True)
    for name, expected in cfg["sha256"].items():
        path = TARGET / name
        if path.exists() and sha256(path) == expected:
            print(f"{name}: already present and verified")
            continue
        url = f"{base}/{cfg['source_commit']}/all_minilm_l6_v2/{name}"
        print(f"downloading {name} from {url}")
        urllib.request.urlretrieve(url, path)
        actual = sha256(path)
        if actual != expected:
            path.unlink()
            sys.exit(f"{name}: SHA-256 mismatch (got {actual}, expected {expected}). File removed.")
        print(f"{name}: verified")


if __name__ == "__main__":
    main()
