from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from config.paths import data_path


ROOT = Path(__file__).resolve().parents[1]

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
    "sq12-transmission-gate-audit-v1.json"
)

EXPECTED = {
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

BODY_SOURCES = np.asarray(
    [65084, 128590, 135589],
    dtype=np.int64,
)

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

EXPECTED_IDS = tuple(
    f"sq11:{mask}:r{replicate}"
    for mask in MASKS
    for replicate in (1, 2)
)

FIELDS = {
    "source_effective_activity_pre_synaptic":
        (np.dtype(np.float32), (16, 192, 3)),
    "responder_fired":
        (np.dtype(np.uint8), (16, 192, 3)),
    "responder_spikes_post_commit":
        (np.dtype(np.uint8), (16, 192, 3)),
}


class GateAuditError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise GateAuditError(message)


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
    expected = EXPECTED[name]

    if observed != expected:
        fail(
            f"{name} SHA drift: "
            f"{observed} != {expected}"
        )

    return observed


def canonicalize(
    masks: np.ndarray,
    reps: np.ndarray,
    values: np.ndarray,
) -> dict[str, np.ndarray]:
    found = {}

    for mask in MASKS:
        rows = {}

        for i in range(len(masks)):
            if str(masks[i]) != mask:
                continue

            rep = int(reps[i])

            if rep in rows:
                fail(
                    f"duplicate {mask}/r{rep}"
                )

            rows[rep] = np.array(
                values[i],
                copy=True,
            )

        if set(rows) != {1, 2}:
            fail(
                f"incomplete replicate pair: {mask}"
            )

        if not np.array_equal(
            rows[1],
            rows[2],
        ):
            fail(
                f"deterministic replicate mismatch: {mask}"
            )

        found[mask] = rows[1]

    return found


def mismatch_report(
    canonical: dict[str, np.ndarray],
) -> dict:
    baseline = canonical["000"]

    rows = {}
    total = 0

    for mask in MASKS:
        delta = (
            canonical[mask]
            != baseline
        )

        count = int(
            np.count_nonzero(delta)
        )

        total += count

        hits = np.argwhere(delta)

        first = None

        if len(hits):
            first = {
                "frame": int(hits[0][0]),
                "body_position":
                    int(hits[0][1]),
            }

        rows[mask] = {
            "mismatch_count_vs_000":
                count,
            "first_mismatch":
                first,
        }

    return {
        "by_mask": rows,
        "total_mismatches_vs_000":
            total,
        "all_masks_exact_to_000":
            total == 0,
    }


def audit() -> dict:
    provenance = {
        name: verify_sha(
            name,
            {
                "evidence": EVIDENCE,
                "runtime": RUNTIME,
                "graded": GRADED,
                "topology": TOPOLOGY,
            }[name],
        )
        for name in EXPECTED
    }

    graded = np.load(
        GRADED,
        allow_pickle=False,
    )

    graded_indices = np.asarray(
        graded["neuron_index"],
        dtype=np.int64,
    )

    responder_overlap = sorted(
        set(
            BODY_RESPONDERS.tolist()
        )
        & set(
            graded_indices.tolist()
        )
    )

    if responder_overlap:
        fail(
            "BODY responder entered graded "
            f"population: {responder_overlap}"
        )

    with np.load(
        EVIDENCE,
        allow_pickle=False,
    ) as z:

        required = {
            "condition_id",
            "condition_mask",
            "condition_replicate",
            *FIELDS,
        }

        missing = required - set(z.files)

        if missing:
            fail(
                "SQ-11 evidence missing fields: "
                f"{sorted(missing)}"
            )

        ids = tuple(
            str(x)
            for x in z["condition_id"]
        )

        if ids != EXPECTED_IDS:
            fail(
                "SQ-11 condition order drift"
            )

        masks = np.asarray(
            z["condition_mask"]
        )

        reps = np.asarray(
            z["condition_replicate"]
        )

        canonical = {}

        for name, (
            expected_dtype,
            expected_shape,
        ) in FIELDS.items():

            value = np.asarray(
                z[name]
            )

            if value.dtype != expected_dtype:
                fail(
                    f"{name} dtype drift: "
                    f"{value.dtype}"
                )

            if value.shape != expected_shape:
                fail(
                    f"{name} shape drift: "
                    f"{value.shape}"
                )

            canonical[name] = (
                canonicalize(
                    masks,
                    reps,
                    value,
                )
            )

        #
        # P6 firing and committed P7 spikes are
        # required to agree exactly.
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
                    f"P6/P7 spike disagreement: {mask}"
                )

    source_activity = mismatch_report(
        canonical[
            "source_effective_activity_pre_synaptic"
        ]
    )

    responder_firing = mismatch_report(
        canonical[
            "responder_fired"
        ]
    )

    responder_spikes = mismatch_report(
        canonical[
            "responder_spikes_post_commit"
        ]
    )

    gate_closed = all((
        source_activity[
            "all_masks_exact_to_000"
        ],
        responder_firing[
            "all_masks_exact_to_000"
        ],
        responder_spikes[
            "all_masks_exact_to_000"
        ],
    ))

    classification = (
        "TRANSMISSION_GATE_CLOSED_192_FRAMES"
        if gate_closed
        else
        "TRANSMISSION_GATE_OPEN"
    )

    return {
        "schema_version":
            (
                "moscaquant."
                "sq12-resonance-cascade-"
                "transmission-gate-audit/v1"
            ),
        "experiment":
            "SQ-12",
        "codename":
            "RESONANCE CASCADE",
        "status":
            "AUDIT_COMPLETE",
        "audit_type":
            "PRE_EXECUTION_EXISTING_EVIDENCE",
        "neural_execution_performed":
            False,
        "classification":
            classification,
        "frame_count":
            192,
        "body_sources":
            BODY_SOURCES.tolist(),
        "body_responders":
            BODY_RESPONDERS.tolist(),
        "runtime_transmission_rule": {
            "graded_population":
                "Tm2/Tm3/Tm4 may transmit positive subthreshold voltage",
            "non_graded_population":
                "spike-only propagation",
            "body_responders_are_graded":
                False,
            "body_responder_graded_overlap":
                responder_overlap,
        },
        "source_effective_activity":
            source_activity,
        "responder_firing":
            responder_firing,
        "responder_spikes":
            responder_spikes,
        "causal_gate": {
            "closed":
                gate_closed,
            "logic": (
                "The intervention changes only the "
                "three frozen BODY input edges. "
                "BODY responders are non-graded, so "
                "their outgoing effective activity is "
                "their spike state. If BODY source P2 "
                "effective activity and BODY responder "
                "spikes remain exact across all eight "
                "masks for all 192 frames, the known "
                "local subthreshold BODY perturbation "
                "has no changed transmissible state "
                "through which to leave the immediate "
                "BODY boundary during this window."
            ),
        },
        "downstream_execution": {
            "authorized_here":
                False,
            "required_if_gate_closed":
                False,
            "requires_separate_authorization_if_gate_open":
                True,
        },
        "provenance": {
            "sq11_evidence": {
                "path":
                    str(
                        EVIDENCE.relative_to(ROOT)
                    ),
                "sha256":
                    provenance["evidence"],
            },
            "frozen_runtime": {
                "path":
                    str(
                        RUNTIME.relative_to(ROOT)
                    ),
                "sha256":
                    provenance["runtime"],
            },
            "graded_population": {
                "path":
                    str(GRADED),
                "sha256":
                    provenance["graded"],
            },
            "sq12_topology": {
                "path":
                    str(
                        TOPOLOGY.relative_to(ROOT)
                    ),
                "sha256":
                    provenance["topology"],
            },
        },
        "claim_boundary": (
            "computational transmission-gate audit "
            "within the frozen 192-frame runtime only; "
            "no biological, behavioral, cognitive, "
            "organism-level, or financial claim"
        ),
    }


def main() -> None:
    if OUTPUT.exists():
        fail(
            "SQ-12 transmission-gate artifact "
            "already exists"
        )

    result = audit()

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        "SQ-12 RESONANCE CASCADE "
        "TRANSMISSION GATE"
    )

    print(
        "classification:",
        result["classification"],
    )

    print(
        "source P2 mismatches:",
        result[
            "source_effective_activity"
        ][
            "total_mismatches_vs_000"
        ],
    )

    print(
        "responder firing mismatches:",
        result[
            "responder_firing"
        ][
            "total_mismatches_vs_000"
        ],
    )

    print(
        "responder spike mismatches:",
        result[
            "responder_spikes"
        ][
            "total_mismatches_vs_000"
        ],
    )

    print(
        "BODY responders graded:",
        result[
            "runtime_transmission_rule"
        ][
            "body_responders_are_graded"
        ],
    )

    print(
        "neural execution performed:",
        result[
            "neural_execution_performed"
        ],
    )

    print(
        "output sha256:",
        sha256_file(OUTPUT),
    )


if __name__ == "__main__":
    main()
