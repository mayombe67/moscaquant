from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from scipy import sparse

FROZEN_MI_BINS = 8
FROZEN_MI_LAGS = (0, 1, 2, 3, 4)


def responder_identity(responder_voltage, responder_indices):
    voltage = np.asarray(responder_voltage, dtype=np.float64)
    indices = np.asarray(responder_indices, dtype=np.int32)

    if voltage.ndim != 2:
        raise ValueError("responder_voltage must be [frames, responders]")
    if voltage.shape[1] != len(indices):
        raise ValueError("responder index count does not match voltage columns")

    active_mask = np.any(voltage > 0.0, axis=0)
    active = indices[active_mask].astype(np.int32, copy=False)

    return {
        "responder_count": int(len(active)),
        "responder_indices": [int(x) for x in active],
    }


def first_positive_onsets(responder_voltage, responder_indices):
    voltage = np.asarray(responder_voltage, dtype=np.float64)
    indices = np.asarray(responder_indices, dtype=np.int32)

    if voltage.ndim != 2:
        raise ValueError("responder_voltage must be [frames, responders]")
    if voltage.shape[1] != len(indices):
        raise ValueError("responder index count does not match voltage columns")

    result = {}
    for column, index in enumerate(indices):
        positive = np.flatnonzero(voltage[:, column] > 0.0)
        result[int(index)] = int(positive[0]) if len(positive) else None
    return result


def positive_voltage_fingerprint(responder_voltage):
    voltage = np.asarray(responder_voltage, dtype=np.float64)
    if voltage.ndim != 2:
        raise ValueError("responder_voltage must be [frames, responders]")
    return np.maximum(voltage, 0.0).reshape(-1)


def compare_responder_identity(reference_indices, candidate_indices):
    a = set(int(x) for x in reference_indices)
    b = set(int(x) for x in candidate_indices)
    union = a | b
    intersection = a & b

    return {
        "exact_responder_set": a == b,
        "jaccard_vs_A": 1.0 if not union else float(len(intersection) / len(union)),
    }


def compare_onsets(reference, candidate):
    common = sorted(
        index
        for index in reference
        if index in candidate
        and reference[index] is not None
        and candidate[index] is not None
    )

    shifts = np.asarray(
        [abs(int(candidate[index]) - int(reference[index])) for index in common],
        dtype=np.int64,
    )

    return {
        "common_present_responders": int(len(common)),
        "exact_onset_agreement_count": int(np.count_nonzero(shifts == 0)),
        "median_absolute_onset_shift": (
            None if not len(shifts) else float(np.median(shifts))
        ),
        "maximum_absolute_onset_shift": (
            None if not len(shifts) else int(np.max(shifts))
        ),
    }


def compare_fingerprints(reference, candidate):
    a = np.asarray(reference, dtype=np.float64).reshape(-1)
    b = np.asarray(candidate, dtype=np.float64).reshape(-1)

    if a.shape != b.shape:
        raise ValueError("fingerprints must have identical shape")

    diff = b - a
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    denom = norm_a * norm_b

    if denom == 0.0:
        cosine = 1.0 if np.array_equal(a, b) else 0.0
    else:
        cosine = float(np.dot(a, b) / denom)

    l2 = float(np.linalg.norm(diff))
    normalized_l2 = l2 if norm_a == 0.0 else float(l2 / norm_a)
    max_abs = 0.0 if not len(diff) else float(np.max(np.abs(diff)))

    return {
        "cosine_similarity": cosine,
        "normalized_l2_distance": normalized_l2,
        "maximum_absolute_voltage_difference": max_abs,
    }


def _fixed_bin_ids(values, bins=FROZEN_MI_BINS):
    x = np.clip(np.asarray(values, dtype=np.float64), 0.0, 1.0)
    ids = np.floor(x * bins).astype(np.int64)
    ids[ids == bins] = bins - 1
    return ids


def _discrete_mutual_information(x, y, bins=FROZEN_MI_BINS):
    xi = _fixed_bin_ids(x, bins=bins)
    yi = _fixed_bin_ids(y, bins=bins)

    if len(xi) != len(yi):
        raise ValueError("MI traces must have identical length")
    if not len(xi):
        return 0.0

    joint = np.zeros((bins, bins), dtype=np.int64)
    np.add.at(joint, (xi, yi), 1)

    total = float(len(xi))
    pxy = joint / total
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)

    mi = 0.0
    for i in range(bins):
        for j in range(bins):
            p = float(pxy[i, j])
            if p <= 0.0:
                continue
            denom = float(px[i] * py[j])
            if denom <= 0.0:
                continue
            mi += p * math.log(p / denom, 2)

    return float(mi)


def lagged_mutual_information(
    stimulus_trace,
    dn_trace,
    *,
    bins=FROZEN_MI_BINS,
    lags=FROZEN_MI_LAGS,
):
    stimulus = np.asarray(stimulus_trace, dtype=np.float64).reshape(-1)
    dn = np.clip(np.asarray(dn_trace, dtype=np.float64).reshape(-1), 0.0, 1.0)

    if stimulus.shape != dn.shape:
        raise ValueError("stimulus and DN traces must have identical length")

    values = {}
    for lag in lags:
        lag = int(lag)
        if lag < 0:
            raise ValueError("lags must be nonnegative")
        if lag == 0:
            x, y = stimulus, dn
        elif lag >= len(stimulus):
            x, y = stimulus[:0], dn[:0]
        else:
            x, y = stimulus[:-lag], dn[lag:]

        values[str(lag)] = _discrete_mutual_information(x, y, bins=bins)

    return {
        "bins": int(bins),
        "lags": [int(x) for x in lags],
        "mi_by_lag": values,
        "maximum_mi": 0.0 if not values else float(max(values.values())),
    }


def accepted_causal_edge_survival(connectome, frozen_edges):
    matrix = connectome.tocsr(copy=False)
    surviving = []
    frozen = [(int(pre), int(post)) for pre, post in frozen_edges]

    for pre, post in frozen:
        lo = int(matrix.indptr[post])
        hi = int(matrix.indptr[post + 1])
        row = matrix.indices[lo:hi]
        position = int(np.searchsorted(row, pre))
        exists = position < len(row) and int(row[position]) == pre
        if exists:
            surviving.append((pre, post))

    count = int(len(surviving))
    total = int(len(frozen))

    return {
        "frozen_causal_edge_count": total,
        "surviving_causal_edge_count": count,
        "causal_edge_survival_fraction": 1.0 if total == 0 else float(count / total),
        "complete_causal_route_set_survives": count == total,
        "surviving_edges": [
            {"presynaptic": pre, "postsynaptic": post}
            for pre, post in surviving
        ],
    }
