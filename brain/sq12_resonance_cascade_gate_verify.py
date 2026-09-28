from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from brain.physiology_constrained_visual_transduction import (
    PhysiologyConstrainedVisualTransductionRuntime,
)
from config.paths import data_path


ROOT = Path(__file__).resolve().parents[1]

GATE = (
    ROOT
    / "artifacts/experiments/"
    "sq12-resonance-cascade/"
    "sq12-transmission-gate-audit-v1.json"
)

EVIDENCE = (
    ROOT
    / "artifacts/experiments/"
    "sq11-dark-forest/"
    "sq11-dark-forest-evidence-v2.npz"
)

RUNTIME = (
    ROOT
    / "brain/"
    "physiology_constrained_visual_transduction.py"
)

TOPOLOGY = (
    ROOT
    / "config/controls/"
    "sq12-resonance-cascade-topology-v1.json"
)

GRADED = data_path(
    "processed",
    "mq3-2-graded-visual-types-v1.npz",
)

OUTPUT = (
    ROOT
    / "artifacts/experiments/"
    "sq12-resonance-cascade/"
    "sq12-transmission-gate-verification-v1.json"
)

EXPECTED_SHA256 = {
    "gate": (
        "916cb99c1bec589467c6ab6fbff79289"
        "d0d0d52c6e2110e95b4d7964f24dd065"
    ),
    "evidence": (
        "cef49b5e581d6c9b2f21aafc701d06e"
        "8d53b0abc03f8453c9fe6c5d19ede9c37"
    ),
    "runtime": (
        "bf754a29155ade789349fbdfc3c579f1"
        "b2c8dbea3c63804f2cf3d858d0a2f605"
    ),
    "graded": (
        "1c514bf58bf69b24bfba28489344d0fe"
        "3e0f7590d649e0ef446c33898d38e379"
    ),
    "topology": (
        "eae563550ea12bcb6be7a4612edb7856"
        "dcdf26291b6f2c7b0d90eb2bc025ae7e"
    ),
}

BODY_RESPONDERS = np.asarray(
    [137122, 317, 126002],
    dtype=np.int64,
)

MASKS = (
    "000",
    "001",
    "010",
    "011",
    "100",
    "101",
    "110",
    "111",
)

FIELDS = (
    "source_effective_activity_pre_synaptic",
    "responder_fired",
    "responder_spikes_post_commit",
)


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(8 * 1024 * 1024),
            b"",
        ):
            h.update(chunk)

    return h.hexdigest()


def verify_sha(
    name: str,
    path: Path,
) -> str:
    if not path.is_file():
        fail(
            f"missing {name}: {path}"
        )

    observed = sha256_file(path)

    if observed != EXPECTED_SHA256[name]:
        fail(
            f"{name} SHA drift: "
            f"{observed} != "
            f"{EXPECTED_SHA256[name]}"
        )

    return observed


def verify_runtime_semantics() -> bool:
    """
    Independently exercise the frozen
    effective_activity method.

    Non-graded coordinates must preserve
    spike-only activity even when they carry
    positive subthreshold voltage.

    Graded coordinates must remain capable
    of transmitting subthreshold voltage.
    """

    dummy = SimpleNamespace()

    dummy.spikes = np.asarray(
        [
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
        ],
        dtype=np.float32,
    )

    dummy.voltage = np.asarray(
        [
            0.75,
            0.50,
            0.25,
            0.90,
            0.40,
            0.10,
        ],
        dtype=np.float32,
    )

    dummy.graded_indices = np.asarray(
        [1, 4],
        dtype=np.int32,
    )

    dummy.config = SimpleNamespace(
        threshold=1.0,
    )

    result = (
        PhysiologyConstrainedVisualTransductionRuntime
        .effective_activity(dummy)
    )

    #
    # Non-graded coordinates:
    # activity must be exactly spike state.
    #
    non_graded = np.asarray(
        [0, 2, 3, 5],
        dtype=np.int64,
    )

    if not np.array_equal(
        result[non_graded],
        dummy.spikes[non_graded],
    ):
        fail(
            "non-graded activity is not "
            "spike-only"
        )

    #
    # Graded zero-spike coordinates:
    # positive voltage is transmitted.
    #
    if not (
        result[1] == np.float32(0.50)
        and result[4] == np.float32(0.40)
    ):
        fail(
            "graded transmission behavior drift"
        )

    return True


def canonicalize(
    masks: np.ndarray,
    replicates: np.ndarray,
    values: np.ndarray,
) -> dict[str, np.ndarray]:
    result = {}

    for mask in MASKS:
        matches = np.flatnonzero(
            masks == mask
        )

        if len(matches) != 2:
            fail(
                f"{mask}: expected two replicates"
            )

        by_rep = {}

        for index in matches:
            rep = int(
                replicates[index]
            )

            if rep in by_rep:
                fail(
                    f"{mask}: duplicate r{rep}"
                )

            by_rep[rep] = np.asarray(
                values[index]
            )

        if set(by_rep) != {1, 2}:
            fail(
                f"{mask}: replicate set drift"
            )

        if not np.array_equal(
            by_rep[1],
            by_rep[2],
        ):
            fail(
                f"{mask}: deterministic "
                "replicate mismatch"
            )

        result[mask] = np.array(
            by_rep[1],
            copy=True,
        )

    return result


def verify_evidence() -> dict:
    with np.load(
        EVIDENCE,
        allow_pickle=False,
    ) as z:

        required = {
            "condition_mask",
            "condition_replicate",
            *FIELDS,
        }

        missing = required - set(z.files)

        if missing:
            fail(
                "evidence missing fields: "
                f"{sorted(missing)}"
            )

        masks = np.asarray(
            z["condition_mask"]
        ).astype(str)

        replicates = np.asarray(
            z["condition_replicate"],
            dtype=np.int64,
        )

        canonical = {
            field: canonicalize(
                masks,
                replicates,
                np.asarray(z[field]),
            )
            for field in FIELDS
        }

    #
    # P6 and committed P7 spikes must agree
    # for every mask.
    #
    for mask in MASKS:
        if not np.array_equal(
            canonical[
                "responder_fired"
            ][mask],
            canonical[
                "responder_spikes_post_commit"
            ][mask],
        ):
            fail(
                f"{mask}: P6/P7 spike drift"
            )

    counts = {}

    baseline = {
        field: canonical[field]["000"]
        for field in FIELDS
    }

    for field in FIELDS:
        total = 0
        per_mask = {}

        for mask in MASKS:
            mismatch = (
                canonical[field][mask]
                != baseline[field]
            )

            count = int(
                np.count_nonzero(mismatch)
            )

            per_mask[mask] = count
            total += count

        counts[field] = {
            "per_mask":
                per_mask,
            "total_mismatches_vs_000":
                total,
        }

        if total != 0:
            fail(
                f"{field}: transmission "
                f"gate is not closed: {total}"
            )

    return counts


def verify_graded_boundary() -> dict:
    with np.load(
        GRADED,
        allow_pickle=False,
    ) as z:
        graded_indices = np.asarray(
            z["neuron_index"],
            dtype=np.int64,
        )

    overlap = np.intersect1d(
        BODY_RESPONDERS,
        graded_indices,
    )

    if len(overlap):
        fail(
            "BODY responder unexpectedly graded: "
            f"{overlap.tolist()}"
        )

    return {
        "body_responder_count": 3,
        "graded_overlap":
            overlap.tolist(),
        "all_body_responders_non_graded":
            True,
    }


def verify_gate_artifact() -> dict:
    gate = json.loads(
        GATE.read_text(
            encoding="utf-8"
        )
    )

    required = {
        "classification":
            "TRANSMISSION_GATE_CLOSED_192_FRAMES",
        "neural_execution_performed":
            False,
    }

    for key, expected in required.items():
        if gate.get(key) != expected:
            fail(
                f"gate artifact {key} drift"
            )

    if (
        gate.get(
            "causal_gate",
            {},
        ).get("closed")
        is not True
    ):
        fail(
            "gate artifact does not "
            "declare causal gate closed"
        )

    if (
        gate.get(
            "downstream_execution",
            {},
        ).get(
            "required_if_gate_closed"
        )
        is not False
    ):
        fail(
            "gate artifact downstream "
            "requirement drift"
        )

    return gate


def main() -> None:
    if OUTPUT.exists():
        fail(
            "verification artifact "
            "already exists"
        )

    observed_sha = {
        "gate":
            verify_sha(
                "gate",
                GATE,
            ),
        "evidence":
            verify_sha(
                "evidence",
                EVIDENCE,
            ),
        "runtime":
            verify_sha(
                "runtime",
                RUNTIME,
            ),
        "graded":
            verify_sha(
                "graded",
                GRADED,
            ),
        "topology":
            verify_sha(
                "topology",
                TOPOLOGY,
            ),
    }

    gate = verify_gate_artifact()

    runtime_semantics = (
        verify_runtime_semantics()
    )

    graded_boundary = (
        verify_graded_boundary()
    )

    evidence = verify_evidence()

    payload = {
        "schema_version":
            (
                "moscaquant."
                "sq12-resonance-cascade-"
                "transmission-gate-verification/v1"
            ),
        "experiment":
            "SQ-12",
        "codename":
            "RESONANCE CASCADE",
        "status":
            "INDEPENDENT_VERIFICATION_PASS",
        "neural_execution_performed":
            False,
        "verified_classification":
            gate["classification"],
        "runtime_semantics_verified":
            runtime_semantics,
        "graded_boundary":
            graded_boundary,
        "evidence_exactness":
            evidence,
        "provenance_sha256":
            observed_sha,
        "conclusion": (
            "Within the frozen 192-frame "
            "runtime, the BODY perturbations "
            "change local responder state but "
            "never change a transmissible BODY "
            "responder state. Downstream neural "
            "execution is not required to establish "
            "closure of this propagation question."
        ),
        "claim_boundary": (
            "frozen MoscaQuant computational "
            "runtime only; no biological, "
            "behavioral, cognitive, organism-level, "
            "market, or financial claim"
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
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "SQ-12 RESONANCE CASCADE "
        "INDEPENDENT VERIFICATION PASS"
    )

    print(
        "classification:",
        payload[
            "verified_classification"
        ],
    )

    print(
        "runtime semantics verified:",
        runtime_semantics,
    )

    print(
        "BODY graded overlap:",
        graded_boundary[
            "graded_overlap"
        ],
    )

    for field in FIELDS:
        print(
            field,
            "mismatches:",
            evidence[field][
                "total_mismatches_vs_000"
            ],
        )

    print(
        "neural execution performed:",
        payload[
            "neural_execution_performed"
        ],
    )

    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
