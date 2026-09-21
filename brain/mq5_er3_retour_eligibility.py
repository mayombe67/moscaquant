from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.mq5_ts_runtime import (
    CONNECTOME,
    RETINA,
    RELAY,
    GRADED,
    RELEASE_GAIN,
)
from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from brain.visual_transduction import VisualTransductionConfig


CONFIG = Path("config/controls/mq5-er3-retour-v1.toml")

NO_SHOW = (116680, 12024)
MATCHED_CONTROL = (78481, 16087)

CANCELED = "DETERMINISTICALLY_CANCELED_RETINA_RELAY"
ELIGIBLE = "INTERVENTION_ADDRESSABLE"


def load_protocol() -> dict:
    with CONFIG.open("rb") as handle:
        return tomllib.load(handle)


def build_runtime_inputs():
    original = sparse.load_npz(CONNECTOME).tocsr()
    original.sum_duplicates()
    original.sort_indices()

    retina_data = np.load(RETINA)
    retinal_indices = np.asarray(
        retina_data["neuron_index"],
        dtype=np.int32,
    )

    runtime = PhysiologyConstrainedVisualTransductionRuntime(
        connectome=original,
        retinal_indices=retinal_indices,
        relay_artifact=RELAY,
        graded_artifact=GRADED,
        config=VisualTransductionConfig(
            release_gain=RELEASE_GAIN,
        ),
    )

    return original, runtime


def _index_map(indices: np.ndarray) -> dict[int, int]:
    return {
        int(model_index): int(local_index)
        for local_index, model_index in enumerate(
            np.asarray(indices, dtype=np.int64)
        )
    }


def classify_edge(
    *,
    original,
    runtime,
    pre: int,
    post: int,
    rtol: float,
    atol: float,
) -> dict:
    pre = int(pre)
    post = int(post)

    ordinary_weight = float(original[post, pre])
    if ordinary_weight == 0.0:
        raise RuntimeError(f"ordinary connectome edge absent: {pre}->{post}")

    retina_map = _index_map(runtime.retinal_indices)
    relay_map = _index_map(runtime.relay_indices)

    pre_retina = pre in retina_map
    post_relay = post in relay_map

    record = {
        "presynaptic": pre,
        "postsynaptic": post,
        "ordinary_weight": ordinary_weight,
        "pre_in_retina": bool(pre_retina),
        "post_in_relay": bool(post_relay),
    }

    if not (pre_retina and post_relay):
        record.update({
            "status": ELIGIBLE,
            "relay_weight": None,
            "weight_delta": None,
        })
        return record

    row = relay_map[post]
    col = retina_map[pre]
    relay_weight = float(runtime.relay_from_retina[row, col])
    delta = float(ordinary_weight - relay_weight)

    record.update({
        "relay_weight": relay_weight,
        "weight_delta": delta,
    })

    if not np.isclose(
        ordinary_weight,
        relay_weight,
        rtol=float(rtol),
        atol=float(atol),
    ):
        raise RuntimeError(
            "RETOUR retina-relay representation mismatch for "
            f"{pre}->{post}: ordinary={ordinary_weight}, "
            f"relay={relay_weight}, delta={delta}"
        )

    record["status"] = CANCELED
    return record


def verify_negative_controls() -> dict:
    protocol = load_protocol()
    eligibility = protocol["eligibility"]

    rtol = float(eligibility["retina_relay_weight_rtol"])
    atol = float(eligibility["retina_relay_weight_atol"])

    original, runtime = build_runtime_inputs()

    controls = {
        "no_show": classify_edge(
            original=original,
            runtime=runtime,
            pre=NO_SHOW[0],
            post=NO_SHOW[1],
            rtol=rtol,
            atol=atol,
        ),
        "matched_control": classify_edge(
            original=original,
            runtime=runtime,
            pre=MATCHED_CONTROL[0],
            post=MATCHED_CONTROL[1],
            rtol=rtol,
            atol=atol,
        ),
    }

    expected = protocol["negative_controls"]
    expected_edges = {
        "no_show": NO_SHOW,
        "matched_control": MATCHED_CONTROL,
    }

    for name, edge in expected_edges.items():
        frozen = expected[name]
        configured = (
            int(frozen["presynaptic"]),
            int(frozen["postsynaptic"]),
        )
        if configured != edge:
            raise RuntimeError(
                f"{name} config edge drift: {configured} != {edge}"
            )

        required = str(frozen["required_status"])
        observed = controls[name]["status"]
        if observed != required:
            raise RuntimeError(
                f"{name} negative-control failure: "
                f"{observed} != {required}"
            )

        if not bool(frozen["must_not_appear_in_candidate_lists"]):
            raise RuntimeError(
                f"{name} must-not-appear candidate gate is not frozen true"
            )

    return {
        "experiment": protocol["experiment_id"],
        "codename": protocol["codename"],
        "kind": "PRE-OUTCOME ELIGIBILITY VERIFICATION",
        "confirmatory_or_retour_outcomes_used": False,
        "retina_relay_weight_rtol": rtol,
        "retina_relay_weight_atol": atol,
        "negative_controls": controls,
        "candidate_exclusion_gate_verified": True,
        "result_execution_enabled": bool(
            protocol["result_execution_enabled"]
        ),
        "financial_semantics": protocol["financial_semantics"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-negative-controls",
        action="store_true",
        required=True,
    )
    args = parser.parse_args()
    del args

    print(
        json.dumps(
            verify_negative_controls(),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
