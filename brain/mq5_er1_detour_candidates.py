from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


MAX_BACKWARD_HOPS = 3
TOP_K_PER_TARGET = 5
FOCUSED_MIN_TARGETS = 3
ACTIVITY_EPSILON = 1e-12


@dataclass(frozen=True)
class EdgeTrace:
    presynaptic: int
    postsynaptic: int
    hop_from_target: int
    a_baseline: tuple[float, ...]
    c_baseline: tuple[float, ...]
    c_lesion13: tuple[float, ...]


@dataclass(frozen=True)
class Candidate:
    target: int
    presynaptic: int
    postsynaptic: int
    hop_from_target: int
    onset_frame: int
    encoding_divergence_l1: float
    lesion_persistence_l1: float
    score: float


def _prefix(values: tuple[float, ...], onset_frame: int) -> np.ndarray:
    if onset_frame < 0:
        raise ValueError("onset_frame must be >= 0")
    stop = min(onset_frame + 1, len(values))
    return np.asarray(values[:stop], dtype=np.float64)


def score_trace(
    *,
    target: int,
    onset_frame: int,
    trace: EdgeTrace,
) -> Candidate | None:
    if trace.hop_from_target < 1 or trace.hop_from_target > MAX_BACKWARD_HOPS:
        return None

    lengths = {
        len(trace.a_baseline),
        len(trace.c_baseline),
        len(trace.c_lesion13),
    }
    if len(lengths) != 1:
        raise ValueError("trace lengths differ")

    a = _prefix(trace.a_baseline, onset_frame)
    c = _prefix(trace.c_baseline, onset_frame)
    lesion = _prefix(trace.c_lesion13, onset_frame)

    encoding_divergence = float(np.abs(c - a).sum())
    lesion_persistence = float(np.abs(lesion).sum())

    if encoding_divergence <= ACTIVITY_EPSILON:
        return None
    if lesion_persistence <= ACTIVITY_EPSILON:
        return None

    score = float(encoding_divergence * lesion_persistence)

    return Candidate(
        target=int(target),
        presynaptic=int(trace.presynaptic),
        postsynaptic=int(trace.postsynaptic),
        hop_from_target=int(trace.hop_from_target),
        onset_frame=int(onset_frame),
        encoding_divergence_l1=encoding_divergence,
        lesion_persistence_l1=lesion_persistence,
        score=score,
    )


def rank_candidates(
    *,
    target: int,
    onset_frame: int,
    traces: Iterable[EdgeTrace],
) -> list[Candidate]:
    scored = []

    for trace in traces:
        candidate = score_trace(
            target=target,
            onset_frame=onset_frame,
            trace=trace,
        )
        if candidate is not None:
            scored.append(candidate)

    scored.sort(
        key=lambda c: (
            -c.score,
            c.hop_from_target,
            c.postsynaptic,
            c.presynaptic,
        )
    )

    return scored[:TOP_K_PER_TARGET]


def classify_candidate_family(
    by_target: dict[int, list[Candidate]],
    *,
    affected_targets: Iterable[int],
) -> str:
    targets = [int(x) for x in affected_targets]

    all_candidates = [
        candidate
        for target in targets
        for candidate in by_target.get(target, [])
    ]

    if not all_candidates:
        return "NO_CLEAR_DETOUR_CANDIDATES"

    counts: dict[tuple[int, int], set[int]] = {}

    for candidate in all_candidates:
        edge = (
            candidate.presynaptic,
            candidate.postsynaptic,
        )
        counts.setdefault(edge, set()).add(candidate.target)

    if any(
        len(target_set) >= FOCUSED_MIN_TARGETS
        for target_set in counts.values()
    ):
        return "FOCUSED_DETOUR_CANDIDATES"

    return "DIFFUSE_DETOUR_CANDIDATES"
