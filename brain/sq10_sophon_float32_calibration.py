from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.sq05_two_betrayals_runner import (
    CONNECTOME,
    RELAY,
)
from brain.sq08_three_body_episode import (
    resolve_body_edges,
)
from brain.sq08_three_body_plan import (
    CONNECTOME_SHA256,
)
from brain.visual_transduction import (
    VisualTransductionConfig,
)


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "config/experiments/"
    "sq10-sophon-float32-calibration-contract-v1.json"
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq10-sophon/"
    "sq10-sophon-float32-calibration-v1.json"
)

BODY_LABELS = ("A", "B", "C")


class CalibrationRefusal(RuntimeError):
    pass


def refuse(message: str) -> None:
    raise CalibrationRefusal(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(
                8 * 1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def science_git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def load_contract() -> dict:
    return json.loads(
        CONTRACT.read_text()
    )


def background_pattern(
    name: str,
    count: int,
) -> np.ndarray:
    p = np.arange(
        count,
        dtype=np.uint64,
    )

    if name == "all_zero":
        values = np.zeros(
            count,
            dtype=np.float32,
        )

    elif name == "all_one":
        values = np.ones(
            count,
            dtype=np.float32,
        )

    elif name == "all_half":
        values = np.full(
            count,
            np.float32(0.5),
            dtype=np.float32,
        )

    elif name == "alternating_zero_one":
        values = (
            p % np.uint64(2)
        ).astype(
            np.float32
        )

    elif name == (
        "alternating_quarter_threequarter"
    ):
        values = np.where(
            p % np.uint64(2),
            np.float32(0.75),
            np.float32(0.25),
        ).astype(
            np.float32,
            copy=False,
        )

    elif name == "ramp_mod_257":
        values = (
            (p % np.uint64(257))
            .astype(np.float32)
            / np.float32(256.0)
        )

    elif name == "lcg16":
        raw = (
            p * np.uint64(1103515245)
            + np.uint64(12345)
        ) & np.uint64(0xFFFF)

        values = (
            raw.astype(np.float32)
            / np.float32(65535.0)
        )

    elif name == "sparse_stride_7":
        values = np.where(
            p % np.uint64(7) == 0,
            np.float32(1.0),
            np.float32(0.125),
        ).astype(
            np.float32,
            copy=False,
        )

    else:
        raise ValueError(
            f"unknown calibration pattern: {name}"
        )

    if np.any(values < 0.0):
        refuse(
            f"negative activity in pattern {name}"
        )

    if np.any(values > 1.0):
        refuse(
            f"activity above 1 in pattern {name}"
        )

    return values


def remove_csr_position(
    row: sparse.csr_matrix,
    position: int,
) -> sparse.csr_matrix:
    if row.shape[0] != 1:
        raise ValueError(
            "expected one CSR row"
        )

    if position < 0 or position >= row.nnz:
        raise ValueError(
            "CSR removal position out of range"
        )

    data = np.delete(
        row.data,
        position,
    )

    indices = np.delete(
        row.indices,
        position,
    )

    result = sparse.csr_matrix(
        (
            data,
            indices,
            np.asarray(
                [0, len(data)],
                dtype=row.indptr.dtype,
            ),
        ),
        shape=row.shape,
        dtype=np.float32,
    )

    if result.nnz != row.nnz - 1:
        refuse(
            "lesioned calibration row "
            "nnz mismatch"
        )

    return result


def float32_p5(
    *,
    pre_voltage,
    synaptic,
    stimulus,
    decay,
) -> np.float32:
    value = np.asarray(
        [pre_voltage],
        dtype=np.float32,
    )

    value *= decay
    value += np.float32(
        synaptic
    )
    value += np.float32(
        stimulus
    )

    return np.float32(
        value[0]
    )


def float32_ulp(
    value,
) -> float:
    value = np.float32(
        value
    )

    spacing = np.spacing(
        value
    )

    return abs(
        float(spacing)
    )


def power_of_two_ceiling(
    value: float,
) -> float:
    if (
        not math.isfinite(value)
        or value <= 0.0
    ):
        raise ValueError(
            "positive finite value required"
        )

    exponent = math.ceil(
        math.log2(value)
    )

    return float(
        2.0 ** exponent
    )


def main() -> None:
    contract = load_contract()

    if (
        contract[
            "neural_execution_authorized"
        ]
        is not False
    ):
        refuse(
            "calibration contract unexpectedly "
            "authorizes neural execution"
        )

    actual_connectome_sha = sha256_file(
        CONNECTOME
    )

    if (
        actual_connectome_sha
        != CONNECTOME_SHA256
    ):
        refuse(
            "connectome SHA mismatch"
        )

    matrix = sparse.load_npz(
        CONNECTOME
    ).tocsr()

    if matrix.dtype != np.float32:
        refuse(
            "connectome is not float32"
        )

    if not matrix.has_sorted_indices:
        refuse(
            "connectome CSR indices "
            "are not sorted"
        )

    relay = np.load(
        RELAY
    )

    relay_indices = set(
        np.asarray(
            relay["neuron_index"],
            dtype=np.int64,
        ).tolist()
    )

    config = VisualTransductionConfig()

    decay = math.exp(
        -config.dt_ms
        / config.tau_ms
    )

    body_edges = resolve_body_edges()

    source_levels = [
        np.float32(value)
        for value in contract[
            "synthetic_activity"
        ][
            "source_levels_float32"
        ]
    ]

    patterns = list(
        contract[
            "synthetic_activity"
        ][
            "background_patterns"
        ]
    )

    pre_voltages = [
        np.float32(value)
        for value in contract[
            "synthetic_membrane_state"
        ][
            "pre_step_voltage_float32"
        ]
    ]

    stimuli = [
        np.float32(value)
        for value in contract[
            "synthetic_membrane_state"
        ][
            "direct_stimulus_float32"
        ]
    ]

    case_count = 0
    overall_max_residual = 0.0
    overall_max_ulp = 0.0
    worst_case = None
    per_body = {}

    for label, (
        source,
        responder,
        frozen_weight,
    ) in zip(
        BODY_LABELS,
        body_edges,
    ):
        source = int(source)
        responder = int(responder)

        if responder in relay_indices:
            refuse(
                f"{label}: BODY responder "
                "belongs to relay population"
            )

        topology = contract[
            "topology"
        ][
            "body"
        ][label]

        if source != int(
            topology["source"]
        ):
            refuse(
                f"{label}: source drift"
            )

        if responder != int(
            topology["responder"]
        ):
            refuse(
                f"{label}: responder drift"
            )

        retained = matrix.getrow(
            responder
        ).tocsr()

        if retained.nnz != int(
            topology["row_nnz"]
        ):
            refuse(
                f"{label}: row nnz drift"
            )

        hits = np.flatnonzero(
            retained.indices
            == source
        )

        if len(hits) != 1:
            refuse(
                f"{label}: BODY edge "
                "multiplicity drift"
            )

        source_position = int(
            hits[0]
        )

        if source_position != int(
            topology[
                "source_csr_position"
            ]
        ):
            refuse(
                f"{label}: CSR position drift"
            )

        weight = np.float32(
            retained.data[
                source_position
            ]
        )

        if not np.array_equal(
            np.asarray(
                [weight],
                dtype=np.float32,
            ),
            np.asarray(
                [frozen_weight],
                dtype=np.float32,
            ),
        ):
            refuse(
                f"{label}: edge weight drift"
            )

        lesioned = remove_csr_position(
            retained,
            source_position,
        )

        body_max_residual = 0.0
        body_max_ulp = 0.0
        body_worst = None
        body_cases = 0

        for pattern_name in patterns:
            row_activity = (
                background_pattern(
                    pattern_name,
                    retained.nnz,
                )
            )

            full_activity = np.zeros(
                matrix.shape[1],
                dtype=np.float32,
            )

            full_activity[
                retained.indices
            ] = row_activity

            for source_level in source_levels:
                full_activity[
                    source
                ] = source_level

                retained_synaptic = (
                    retained
                    @ full_activity
                )

                lesioned_synaptic = (
                    lesioned
                    @ full_activity
                )

                retained_synaptic = (
                    np.asarray(
                        retained_synaptic,
                        dtype=np.float32,
                    ).ravel()[0]
                )

                lesioned_synaptic = (
                    np.asarray(
                        lesioned_synaptic,
                        dtype=np.float32,
                    ).ravel()[0]
                )

                predicted = (
                    float(
                        np.float64(
                            source_level
                        )
                        * np.float64(
                            weight
                        )
                    )
                )

                for pre_voltage in pre_voltages:
                    for stimulus in stimuli:
                        retained_p5 = float32_p5(
                            pre_voltage=pre_voltage,
                            synaptic=(
                                retained_synaptic
                            ),
                            stimulus=stimulus,
                            decay=decay,
                        )

                        lesioned_p5 = float32_p5(
                            pre_voltage=pre_voltage,
                            synaptic=(
                                lesioned_synaptic
                            ),
                            stimulus=stimulus,
                            decay=decay,
                        )

                        observed = (
                            float(
                                np.float64(
                                    retained_p5
                                )
                                - np.float64(
                                    lesioned_p5
                                )
                            )
                        )

                        residual = (
                            observed
                            - predicted
                        )

                        abs_residual = abs(
                            residual
                        )

                        ulp = max(
                            float32_ulp(
                                retained_p5
                            ),
                            float32_ulp(
                                lesioned_p5
                            ),
                        )

                        case_count += 1
                        body_cases += 1

                        if (
                            abs_residual
                            > body_max_residual
                        ):
                            body_max_residual = (
                                abs_residual
                            )

                            body_worst = {
                                "pattern":
                                    pattern_name,
                                "source_activity":
                                    float(
                                        source_level
                                    ),
                                "pre_voltage":
                                    float(
                                        pre_voltage
                                    ),
                                "stimulus":
                                    float(
                                        stimulus
                                    ),
                                "retained_synaptic":
                                    float(
                                        retained_synaptic
                                    ),
                                "lesioned_synaptic":
                                    float(
                                        lesioned_synaptic
                                    ),
                                "retained_p5":
                                    float(
                                        retained_p5
                                    ),
                                "lesioned_p5":
                                    float(
                                        lesioned_p5
                                    ),
                                "observed_delta":
                                    observed,
                                "predicted_delta":
                                    predicted,
                                "residual":
                                    residual,
                            }

                        body_max_ulp = max(
                            body_max_ulp,
                            ulp,
                        )

        per_body[label] = {
            "source": source,
            "responder": responder,
            "edge_weight":
                float(weight),
            "row_nnz":
                int(retained.nnz),
            "source_csr_position":
                source_position,
            "calibration_case_count":
                body_cases,
            "max_abs_residual":
                body_max_residual,
            "max_float32_p5_ulp":
                body_max_ulp,
            "worst_case":
                body_worst,
        }

        if (
            body_max_residual
            > overall_max_residual
        ):
            overall_max_residual = (
                body_max_residual
            )

            worst_case = {
                "body": label,
                **(
                    body_worst
                    if body_worst is not None
                    else {}
                ),
            }

        overall_max_ulp = max(
            overall_max_ulp,
            body_max_ulp,
        )

    if case_count != int(
        contract[
            "expected_case_count"
        ]
    ):
        refuse(
            "calibration case-count drift: "
            f"{case_count}"
        )

    rule = contract[
        "tolerance_rule"
    ]

    residual_guard = (
        float(
            rule[
                "residual_safety_multiplier"
            ]
        )
        * overall_max_residual
    )

    ulp_guard = (
        float(
            rule["ulp_guard"]["multiplier"]
        )
        * overall_max_ulp
    )

    candidate = max(
        residual_guard,
        ulp_guard,
    )

    tolerance = power_of_two_ceiling(
        candidate
    )

    payload = {
        "schema_version":
            "moscaquant."
            "sq10-sophon-float32-calibration/v1",

        "experiment": "SQ-10",
        "codename": "SOPHON",

        "status":
            "CALIBRATION_COMPLETE_NO_NEURAL_EXECUTION",

        "science_git_sha":
            science_git_sha(),

        "inputs": {
            "contract":
                str(
                    CONTRACT.relative_to(
                        ROOT
                    )
                ),
            "contract_sha256":
                sha256_file(CONTRACT),
            "connectome_sha256":
                actual_connectome_sha,
        },

        "calibration": {
            "case_count":
                case_count,
            "max_abs_residual":
                overall_max_residual,
            "max_float32_p5_ulp":
                overall_max_ulp,
            "residual_guard":
                residual_guard,
            "ulp_guard":
                ulp_guard,
            "candidate":
                candidate,
            "frozen_absolute_tolerance":
                tolerance,
            "frozen_relative_tolerance":
                0.0,
            "worst_case":
                worst_case,
            "per_body":
                per_body,
        },

        "integrity": {
            "neural_runtime_executed":
                False,
            "sq10_evidence_consumed":
                False,
            "tolerance_rule_was_predeclared":
                True,
        },
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
        )
        + "\n"
    )

    print(
        json.dumps(
            payload["calibration"],
            indent=2,
            sort_keys=True,
        )
    )

    print()
    print("output:", OUTPUT)
    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
