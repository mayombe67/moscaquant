from __future__ import annotations

import argparse
import heapq
import json
import subprocess
import tempfile
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

from config.paths import data_path
from brain.mq5_er1_detour_runner import (
    ACTIVITY_EPSILON,
    A_BASELINE_ONSETS,
    C_BASELINE_ONSETS,
    C_LESION13_ONSETS,
    EXPECTED_A_STIMULUS_SHA256,
    EXPECTED_C_STIMULUS_SHA256,
    build_stimuli,
    load_inputs,
    sha256_file,
    verify_known_replay,
)
from brain.mq5_er3_retour_eligibility import (
    CANCELED,
    MATCHED_CONTROL,
    NO_SHOW,
    build_runtime_inputs,
    verify_negative_controls,
)


CONFIG = Path("config/controls/mq5-er3-retour-v1.toml")
OUTPUT = data_path("experiments", "mq5-er3-retour-v1.json")

DETOUR_RESULT = data_path("experiments", "mq5-er1-detour-v1.json")
RACKET_RESULT = data_path("experiments", "mq5-er2-the-racket-v1.json")

EXPECTED_DETOUR_RESULT_SHA256 = (
    "4b06c0181514f01715319dfacfa91569202067e583db7ef9fda5f35818eb4611"
)
EXPECTED_RACKET_RESULT_SHA256 = (
    "3c5e18e63330d99c591536a59db9e6d40c5e5e8dca0789b576fa573e6e0bbfb1"
)

EXPERIMENT_ID = "mq5-er3-retour-v1"
CODENAME = "RETOUR"
FINANCIAL_SEMANTICS = "NOT ASSIGNED"

MAX_BACKWARD_HOPS = 3
TOP_K_PER_TARGET = 5
FOCUSED_MIN_TARGETS = 3

AFFECTED_TARGETS = (55, 92, 656, 126002, 137122)
RETAINED_TARGETS = (51, 129, 317, 1273)
ALL_TRACE_TARGETS = (
    51, 55, 92, 129, 317, 656, 1273, 126002, 137122
)

REQUIRED_TRACKED_FILES = (
    "config/controls/mq5-er3-retour-v1.toml",
    "docs/experiments/mq5-er3-retour-protocol.md",
    "brain/mq5_er3_retour_eligibility.py",
    "brain/mq5_er3_retour_runner.py",
    "tests/test_mq5_er3_retour_eligibility.py",
    "tests/test_mq5_er3_retour_runner_contract.py",
)


def git_status_porcelain() -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "unable to inspect git status: " + completed.stdout
        )
    return completed.stdout


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "unable to determine git HEAD: " + completed.stdout
        )
    return completed.stdout.strip()


def load_protocol() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def verify_parent_results() -> dict:
    detour_sha = sha256_file(DETOUR_RESULT)
    racket_sha = sha256_file(RACKET_RESULT)

    if detour_sha != EXPECTED_DETOUR_RESULT_SHA256:
        raise RuntimeError(
            f"DETOUR parent result SHA mismatch: {detour_sha}"
        )
    if racket_sha != EXPECTED_RACKET_RESULT_SHA256:
        raise RuntimeError(
            f"THE RACKET parent result SHA mismatch: {racket_sha}"
        )

    return {
        "detour_result_sha256": detour_sha,
        "racket_result_sha256": racket_sha,
    }


class RuntimeEligibilityIndex:
    """
    Fast row-local implementation of the frozen RETOUR eligibility rule.

    Only dynamically eligible candidate edges are checked. Traversal ancestry
    remains unchanged; canceled retina->relay edges may be traversed but can
    never be emitted as candidates.
    """

    def __init__(
        self,
        *,
        population_size: int,
        retinal_indices: np.ndarray,
        relay_indices: np.ndarray,
        relay_from_retina,
        rtol: float,
        atol: float,
    ):
        self.rtol = float(rtol)
        self.atol = float(atol)
        self.relay_from_retina = relay_from_retina

        self.retina_local = np.full(
            int(population_size),
            -1,
            dtype=np.int32,
        )
        self.retina_local[
            np.asarray(retinal_indices, dtype=np.int32)
        ] = np.arange(
            len(retinal_indices),
            dtype=np.int32,
        )

        self.relay_local = np.full(
            int(population_size),
            -1,
            dtype=np.int32,
        )
        self.relay_local[
            np.asarray(relay_indices, dtype=np.int32)
        ] = np.arange(
            len(relay_indices),
            dtype=np.int32,
        )

        self.canceled_candidate_checks = 0

    def _relay_values(
        self,
        relay_row: int,
        retina_cols: np.ndarray,
    ) -> np.ndarray:
        values = self.relay_from_retina[
            int(relay_row),
            np.asarray(retina_cols, dtype=np.int32),
        ]
        if sparse.issparse(values):
            values = values.toarray()
        return np.asarray(values, dtype=np.float64).ravel()

    def keep_mask(
        self,
        *,
        post: int,
        pres: np.ndarray,
        weights: np.ndarray,
        eligible: np.ndarray,
    ) -> np.ndarray:
        eligible = np.asarray(eligible, dtype=np.int64)
        if eligible.size == 0:
            return np.zeros(0, dtype=bool)

        relay_row = int(self.relay_local[int(post)])
        if relay_row < 0:
            return np.ones(eligible.size, dtype=bool)

        eligible_pres = np.asarray(
            pres[eligible],
            dtype=np.int32,
        )
        retina_cols = self.retina_local[eligible_pres]
        is_retina = retina_cols >= 0

        keep = np.ones(eligible.size, dtype=bool)
        if not np.any(is_retina):
            return keep

        local_positions = np.flatnonzero(is_retina)
        relay_values = self._relay_values(
            relay_row,
            retina_cols[is_retina],
        )
        ordinary_values = np.asarray(
            weights[eligible[local_positions]],
            dtype=np.float64,
        )

        close = np.isclose(
            ordinary_values,
            relay_values,
            rtol=self.rtol,
            atol=self.atol,
        )

        if not np.all(close):
            bad = int(np.flatnonzero(~close)[0])
            pos = int(local_positions[bad])
            pre = int(eligible_pres[pos])
            raise RuntimeError(
                "RETOUR retina-relay representation mismatch for "
                f"{pre}->{int(post)}: "
                f"ordinary={ordinary_values[bad]}, "
                f"relay={relay_values[bad]}"
            )

        keep[local_positions] = False
        self.canceled_candidate_checks += int(
            len(local_positions)
        )
        return keep


def build_eligibility_index(
    protocol: dict,
    original,
) -> RuntimeEligibilityIndex:
    runtime_original, runtime = build_runtime_inputs()

    if runtime_original.shape != original.shape:
        raise RuntimeError("RETOUR runtime/connectome shape mismatch")

    eligibility = protocol["eligibility"]
    return RuntimeEligibilityIndex(
        population_size=int(original.shape[0]),
        retinal_indices=runtime.retinal_indices,
        relay_indices=runtime.relay_indices,
        relay_from_retina=runtime.relay_from_retina,
        rtol=float(
            eligibility["retina_relay_weight_rtol"]
        ),
        atol=float(
            eligibility["retina_relay_weight_atol"]
        ),
    )


def _push_top_candidate(heap, row):
    key = (
        float(row["score"]),
        -int(row["hop_from_target"]),
        -int(row["postsynaptic"]),
        -int(row["presynaptic"]),
    )
    item = (key, row)

    if len(heap) < TOP_K_PER_TARGET:
        heapq.heappush(heap, item)
        return

    if item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


def _deterministic_row_top_k(
    *,
    pres: np.ndarray,
    eligible: np.ndarray,
    scores: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    eligible_pres = pres[eligible].astype(
        np.int64,
        copy=False,
    )
    order = np.lexsort((eligible_pres, -scores))
    if eligible.size > int(k):
        order = order[: int(k)]
    return eligible[order], scores[order]


def score_target_streaming(
    *,
    original: sparse.csr_matrix,
    lesioned_edges: set[tuple[int, int]],
    target: int,
    onset: int,
    divergence_snapshot: np.ndarray,
    lesion_snapshot: np.ndarray,
    eligibility_index: RuntimeEligibilityIndex,
    max_backward_hops: int = MAX_BACKWARD_HOPS,
):
    frontier = np.asarray(
        [int(target)],
        dtype=np.int32,
    )
    visited_posts: set[int] = set()
    heap = []
    edge_visits = 0
    dynamically_eligible = 0
    canceled_candidates = 0

    for hop in range(
        1,
        int(max_backward_hops) + 1,
    ):
        next_nodes = []

        for post_raw in frontier:
            post = int(post_raw)
            if post in visited_posts:
                continue
            visited_posts.add(post)

            start = int(original.indptr[post])
            stop = int(original.indptr[post + 1])
            if stop <= start:
                continue

            pres = original.indices[start:stop].astype(
                np.int32,
                copy=False,
            )
            weights = original.data[start:stop].astype(
                np.float64,
                copy=False,
            )
            edge_visits += int(stop - start)

            enc = (
                np.abs(weights)
                * divergence_snapshot[pres]
            )
            lesion_part = (
                np.abs(weights)
                * lesion_snapshot[pres]
            )

            if lesioned_edges:
                mask_lesioned = np.fromiter(
                    (
                        (int(pre), post)
                        in lesioned_edges
                        for pre in pres
                    ),
                    dtype=bool,
                    count=len(pres),
                )
                lesion_part[mask_lesioned] = 0.0

            eligible = np.flatnonzero(
                (enc > ACTIVITY_EPSILON)
                & (lesion_part > ACTIVITY_EPSILON)
            )
            dynamically_eligible += int(
                eligible.size
            )

            if eligible.size:
                keep = eligibility_index.keep_mask(
                    post=post,
                    pres=pres,
                    weights=weights,
                    eligible=eligible,
                )
                canceled_candidates += int(
                    eligible.size - np.count_nonzero(keep)
                )
                eligible = eligible[keep]

            if eligible.size:
                scores = (
                    enc[eligible]
                    * lesion_part[eligible]
                )

                eligible, scores = (
                    _deterministic_row_top_k(
                        pres=pres,
                        eligible=eligible,
                        scores=scores,
                        k=TOP_K_PER_TARGET,
                    )
                )

                for local_idx, score in zip(
                    eligible.tolist(),
                    scores.tolist(),
                ):
                    pre = int(
                        pres[int(local_idx)]
                    )
                    row = {
                        "target": int(target),
                        "presynaptic": pre,
                        "postsynaptic": post,
                        "hop_from_target": int(hop),
                        "onset_frame": int(onset),
                        "encoding_divergence_l1": float(
                            enc[int(local_idx)]
                        ),
                        "lesion_persistence_l1": float(
                            lesion_part[
                                int(local_idx)
                            ]
                        ),
                        "score": float(score),
                    }
                    _push_top_candidate(
                        heap,
                        row,
                    )

            # Frozen RETOUR protocol permits canceled edges to remain part of
            # ancestry traversal. They may not be emitted/scored candidates.
            next_nodes.extend(
                int(x) for x in pres
            )

        if not next_nodes:
            break

        frontier = np.unique(
            np.asarray(
                next_nodes,
                dtype=np.int32,
            )
        )

    rows = [item[1] for item in heap]
    rows.sort(
        key=lambda row: (
            -float(row["score"]),
            int(row["hop_from_target"]),
            int(row["postsynaptic"]),
            int(row["presynaptic"]),
        )
    )

    return {
        "target": int(target),
        "onset": int(onset),
        "edge_visits": int(edge_visits),
        "dynamically_eligible_edges": int(
            dynamically_eligible
        ),
        "canceled_retina_relay_candidates": int(
            canceled_candidates
        ),
        "top_candidates": rows,
    }


def candidate_edges(
    by_target: dict[int, dict],
) -> set[tuple[int, int]]:
    return {
        (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
        )
        for target in by_target
        for row in by_target[int(target)][
            "top_candidates"
        ]
    }


def verify_negative_control_absence(
    by_target: dict[int, dict],
) -> None:
    observed = candidate_edges(by_target)

    for label, edge in (
        ("THE NO-SHOW", NO_SHOW),
        ("matched control", MATCHED_CONTROL),
    ):
        if edge in observed:
            raise RuntimeError(
                "RETOUR candidate exclusion failure: "
                f"{label} {edge[0]}->{edge[1]} "
                "appeared in a candidate list"
            )


def classify_family(
    by_target: dict[int, dict],
) -> str:
    all_rows = [
        row
        for target in AFFECTED_TARGETS
        for row in by_target[int(target)][
            "top_candidates"
        ]
    ]

    if not all_rows:
        return "NO_CLEAR_RETOUR_CANDIDATES"

    recurrence: dict[
        tuple[int, int],
        set[int],
    ] = {}

    for row in all_rows:
        edge = (
            int(row["presynaptic"]),
            int(row["postsynaptic"]),
        )
        recurrence.setdefault(
            edge,
            set(),
        ).add(int(row["target"]))

    if any(
        len(targets) >= FOCUSED_MIN_TARGETS
        for targets in recurrence.values()
    ):
        return "FOCUSED_RETOUR_CANDIDATES"

    return "DIFFUSE_RETOUR_CANDIDATES"


def focused_edges(
    by_target: dict[int, dict],
) -> list[dict]:
    recurrence: dict[
        tuple[int, int],
        set[int],
    ] = {}

    for target in AFFECTED_TARGETS:
        for row in by_target[int(target)][
            "top_candidates"
        ]:
            edge = (
                int(row["presynaptic"]),
                int(row["postsynaptic"]),
            )
            recurrence.setdefault(
                edge,
                set(),
            ).add(int(target))

    rows = [
        {
            "presynaptic": int(edge[0]),
            "postsynaptic": int(edge[1]),
            "affected_targets": sorted(
                int(x) for x in targets
            ),
            "recurrence_count": int(
                len(targets)
            ),
        }
        for edge, targets in recurrence.items()
        if len(targets) >= FOCUSED_MIN_TARGETS
    ]
    rows.sort(
        key=lambda row: (
            -int(row["recurrence_count"]),
            int(row["postsynaptic"]),
            int(row["presynaptic"]),
        )
    )
    return rows


def validate_protocol(
    protocol: dict,
) -> None:
    if protocol["experiment_id"] != EXPERIMENT_ID:
        raise RuntimeError(
            "RETOUR experiment_id drift"
        )
    if protocol["codename"] != CODENAME:
        raise RuntimeError(
            "RETOUR codename drift"
        )
    if (
        protocol["financial_semantics"]
        != FINANCIAL_SEMANTICS
    ):
        raise RuntimeError(
            "RETOUR financial semantics drift"
        )
    if int(protocol["frames"]) != 192:
        raise RuntimeError(
            "RETOUR frame-count drift"
        )
    if (
        int(protocol["max_backward_hops"])
        != MAX_BACKWARD_HOPS
    ):
        raise RuntimeError(
            "RETOUR hop-depth drift"
        )
    if (
        int(protocol["top_k_per_target"])
        != TOP_K_PER_TARGET
    ):
        raise RuntimeError(
            "RETOUR top-k drift"
        )
    if (
        tuple(protocol["affected_targets"])
        != AFFECTED_TARGETS
    ):
        raise RuntimeError(
            "RETOUR affected-target drift"
        )
    if (
        tuple(
            protocol[
                "retained_dependency_comparisons"
            ]
        )
        != RETAINED_TARGETS
    ):
        raise RuntimeError(
            "RETOUR retained-target drift"
        )
    if (
        tuple(protocol["all_targets"])
        != ALL_TRACE_TARGETS
    ):
        raise RuntimeError(
            "RETOUR all-target drift"
        )

    classification = protocol["classification"]
    if (
        int(
            classification[
                "focused_min_recurrence_targets"
            ]
        )
        != FOCUSED_MIN_TARGETS
    ):
        raise RuntimeError(
            "RETOUR recurrence threshold drift"
        )
    if (
        classification["focused_label"]
        != "FOCUSED_RETOUR_CANDIDATES"
    ):
        raise RuntimeError(
            "RETOUR focused label drift"
        )
    if (
        classification["diffuse_label"]
        != "DIFFUSE_RETOUR_CANDIDATES"
    ):
        raise RuntimeError(
            "RETOUR diffuse label drift"
        )
    if (
        classification["none_label"]
        != "NO_CLEAR_RETOUR_CANDIDATES"
    ):
        raise RuntimeError(
            "RETOUR none label drift"
        )


def execution_gate(
    protocol: dict,
) -> str:
    validate_protocol(protocol)

    if not bool(
        protocol["result_execution_enabled"]
    ):
        raise RuntimeError(
            "RETOUR RESULT EXECUTION REFUSED: "
            "result_execution_enabled is false"
        )

    if git_status_porcelain().strip():
        raise RuntimeError(
            "RETOUR RESULT EXECUTION REFUSED: "
            "working tree not clean"
        )

    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "--error-unmatch",
            *REQUIRED_TRACKED_FILES,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "RETOUR RESULT EXECUTION REFUSED: "
            "required frozen files are not all tracked"
        )

    if OUTPUT.exists():
        raise RuntimeError(
            "RETOUR result artifact already exists: "
            f"{OUTPUT}"
        )

    return git_head()


def run_retour(
    *,
    authorize_result: bool,
) -> dict:
    protocol = load_protocol()
    validate_protocol(protocol)

    parents = verify_parent_results()
    negative_control_gate = (
        verify_negative_controls()
    )

    if (
        negative_control_gate[
            "candidate_exclusion_gate_verified"
        ]
        is not True
    ):
        raise RuntimeError(
            "RETOUR negative-control gate failed"
        )

    if authorize_result:
        head = execution_gate(protocol)
    else:
        head = git_head()

    (
        original,
        lesioned,
        retina,
        responders,
        causal_edges,
    ) = load_inputs()

    (
        a_stimuli,
        c_stimuli,
        a_sha,
        c_sha,
    ) = build_stimuli()

    if a_sha != EXPECTED_A_STIMULUS_SHA256:
        raise RuntimeError(
            "RETOUR Arm-A stimulus hash drift"
        )
    if c_sha != EXPECTED_C_STIMULUS_SHA256:
        raise RuntimeError(
            "RETOUR Arm-C stimulus hash drift"
        )

    with tempfile.TemporaryDirectory(
        prefix="mq5-er3-retour-"
    ) as temp:
        replay = verify_known_replay(
            original=original,
            lesioned=lesioned,
            retinal_indices=retina,
            responders=responders,
            a_stimuli=a_stimuli,
            c_stimuli=c_stimuli,
            scratch_dir=Path(temp),
        )

        if (
            replay["a_result"]["onsets"]
            != A_BASELINE_ONSETS
        ):
            raise RuntimeError(
                "RETOUR Arm-A onset drift"
            )
        if (
            replay["c_result"]["onsets"]
            != C_BASELINE_ONSETS
        ):
            raise RuntimeError(
                "RETOUR Arm-C onset drift"
            )
        if (
            replay["lesion_result"]["onsets"]
            != C_LESION13_ONSETS
        ):
            raise RuntimeError(
                "RETOUR C13 onset drift"
            )

        if not authorize_result:
            return {
                "experiment": EXPERIMENT_ID,
                "codename": CODENAME,
                "status": "KNOWN-REPLAY-VERIFIED",
                "git_head": head,
                **parents,
                "arm_a_stimulus_sha256": a_sha,
                "arm_c_stimulus_sha256": c_sha,
                "arm_a_onsets": replay[
                    "a_result"
                ]["onsets"],
                "arm_c_onsets": replay[
                    "c_result"
                ]["onsets"],
                "c13_onsets": replay[
                    "lesion_result"
                ]["onsets"],
                "negative_controls": (
                    negative_control_gate[
                        "negative_controls"
                    ]
                ),
                "result_execution": False,
                "financial_semantics": (
                    FINANCIAL_SEMANTICS
                ),
            }

        eligibility_index = (
            build_eligibility_index(
                protocol,
                original,
            )
        )

        lesioned_edge_set = {
            (
                int(pre),
                int(post),
            )
            for pre, post, _weight
            in causal_edges
        }

        by_target = {}

        for target in ALL_TRACE_TARGETS:
            onset = C_BASELINE_ONSETS[
                int(target)
            ]
            by_target[int(target)] = (
                score_target_streaming(
                    original=original,
                    lesioned_edges=(
                        lesioned_edge_set
                    ),
                    target=int(target),
                    onset=int(onset),
                    divergence_snapshot=replay[
                        "divergence_snapshots"
                    ][int(onset)],
                    lesion_snapshot=replay[
                        "lesion_snapshots"
                    ][int(onset)],
                    eligibility_index=(
                        eligibility_index
                    ),
                )
            )

        verify_negative_control_absence(
            by_target
        )

        classification = classify_family(
            by_target
        )
        focused = focused_edges(
            by_target
        )

        payload = {
            "experiment": EXPERIMENT_ID,
            "codename": CODENAME,
            "kind": "discovery",
            "status": "DISCOVERY ONLY",
            "git_head": head,
            **parents,
            "arm_a_stimulus_sha256": a_sha,
            "arm_c_stimulus_sha256": c_sha,
            "max_backward_hops": (
                MAX_BACKWARD_HOPS
            ),
            "top_k_per_target": (
                TOP_K_PER_TARGET
            ),
            "affected_targets": list(
                AFFECTED_TARGETS
            ),
            "retained_dependency_targets": (
                list(RETAINED_TARGETS)
            ),
            "classification": classification,
            "focused_candidates": focused,
            "negative_control_gate": {
                "no_show_status": (
                    negative_control_gate[
                        "negative_controls"
                    ]["no_show"]["status"]
                ),
                "matched_control_status": (
                    negative_control_gate[
                        "negative_controls"
                    ][
                        "matched_control"
                    ]["status"]
                ),
                "no_show_absent_from_candidates": (
                    True
                ),
                "matched_control_absent_from_candidates": (
                    True
                ),
            },
            "targets": {
                str(k): v
                for k, v
                in sorted(by_target.items())
            },
            "canceled_candidate_checks": int(
                eligibility_index
                .canceled_candidate_checks
            ),
            "causal_claims_authorized": False,
            "required_followup": (
                "preregistered causal intervention "
                "for any focused RETOUR candidate"
            ),
            "financial_semantics": (
                FINANCIAL_SEMANTICS
            ),
        }

        OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        OUTPUT.write_text(
            json.dumps(
                payload,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
        )

        payload["result_artifact"] = str(
            OUTPUT
        )
        payload["result_sha256"] = (
            sha256_file(OUTPUT)
        )
        return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(
        required=True
    )
    group.add_argument(
        "--verify-known-replay",
        action="store_true",
    )
    group.add_argument(
        "--run-frozen",
        action="store_true",
    )
    args = parser.parse_args()

    payload = run_retour(
        authorize_result=bool(
            args.run_frozen
        )
    )

    print(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
