"""Small, explicit statistics helpers.

The unit of analysis for pair gaps is the base resume: each base resume is
scored against two jobs and appears in many pairs, so those rows are not
independent. Gaps are first averaged within each base resume, and the
confidence interval resamples base resumes (a cluster bootstrap). The
Wilcoxon signed-rank test also uses one value per base resume.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
from scipy import stats


@dataclass(frozen=True)
class Interval:
    estimate: float
    low: float
    high: float


def bootstrap_mean(values: Sequence[float], n_resamples: int, seed: int, level: float = 0.95) -> Interval:
    """Percentile bootstrap interval for the mean of ``values``."""
    x = np.asarray(values, dtype=float)
    if x.size == 0:
        raise ValueError("no values to bootstrap")
    rng = np.random.default_rng(seed)
    means = x[rng.integers(0, x.size, size=(n_resamples, x.size))].mean(axis=1)
    tail = (1 - level) / 2
    return Interval(float(x.mean()), float(np.quantile(means, tail)), float(np.quantile(means, 1 - tail)))


def wilcoxon_p(values: Sequence[float]) -> Optional[float]:
    """Two-sided Wilcoxon signed-rank p-value, or None if every value is zero."""
    x = np.asarray(values, dtype=float)
    if np.allclose(x, 0.0):
        return None
    return float(stats.wilcoxon(x, zero_method="wilcox", alternative="two-sided").pvalue)


def holm(p_values: Sequence[Optional[float]]) -> list[Optional[float]]:
    """Holm-Bonferroni adjusted p-values. None entries are skipped and stay None."""
    idx = [i for i, p in enumerate(p_values) if p is not None]
    ordered = sorted(idx, key=lambda i: p_values[i])
    m = len(ordered)
    adjusted: dict[int, float] = {}
    running = 0.0
    for rank, i in enumerate(ordered):
        running = max(running, min(1.0, (m - rank) * p_values[i]))
        adjusted[i] = running
    return [adjusted.get(i) for i in range(len(p_values))]


def spearman(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    """Spearman rank correlation, or None if either input is constant."""
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None
    return float(stats.spearmanr(x, y).statistic)


def pairwise_order_accuracy(scores: Sequence[float], tiers: Sequence[int]) -> list[float]:
    """For every pair of candidates in different tiers: 1 if the higher tier scored higher,
    0.5 for a tie, 0 otherwise."""
    out = []
    for i in range(len(scores)):
        for j in range(i + 1, len(scores)):
            if tiers[i] == tiers[j]:
                continue
            hi, lo = (i, j) if tiers[i] > tiers[j] else (j, i)
            out.append(1.0 if scores[hi] > scores[lo] else 0.5 if scores[hi] == scores[lo] else 0.0)
    return out


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0
