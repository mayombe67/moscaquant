"""Deterministic sequential visual stimulus for MQ-001."""

from argparse import ArgumentParser
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.populations import visual_r1_r6_indices
from brain.retina import load_optic_columns, infer_r1_r6_retina
from brain.runtime import LIFConfig


DEFAULT_DATA = Path.home() / "moscaquant-data"

FROZEN_SEQUENCE = (
    ("L", 23, 32),
    ("L", 24, 32),
    ("L", 25, 32),
)


def main() -> None:
    parser = ArgumentParser()

    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA,
    )

    parser.add_argument(
        "--hold-steps",
        type=int,
        default=1,
        help="LIF steps for which each retinal position is stimulated.",
    )

    args = parser.parse_args()

    if args.hold_steps < 1:
        raise ValueError("--hold-steps must be >= 1")

    data = args.data

    ids = np.load(
        data / "processed/neuron_ids.npy",
        mmap_mode="r",
    )

    graph = sparse.load_npz(
        data / "processed/connectome-baseline-v1.npz"
    ).tocsr()

    annotations_path = (
        data
        / "raw"
        / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )

    r1 = visual_r1_r6_indices(
        annotations_path,
        ids,
    )

    optic_columns = load_optic_columns(
        data
        / "raw"
        / "reference"
        / "optic-column-type-assignments-v1.0.xlsx"
    )

    placed, _ = infer_r1_r6_retina(
        graph,
        ids,
        r1,
        optic_columns,
    )

    by_column = {}

    for eye, h1, h2 in FROZEN_SEQUENCE:
        indices = np.asarray(
            [
                p.neuron_index
                for p in placed
                if (p.eye, p.h1, p.h2)
                == (eye, h1, h2)
            ],
            dtype=np.int32,
        )

        if len(indices) != 6:
            raise RuntimeError(
                f"Frozen column {eye}/{h1}/{h2} "
                f"expected 6 R1-R6, found {len(indices)}"
            )

        by_column[(eye, h1, h2)] = indices

    cfg = LIFConfig()

    voltage = np.zeros(
        len(ids),
        dtype=np.float32,
    )

    spikes = np.zeros(
        len(ids),
        dtype=np.float32,
    )

    decay = np.exp(
        -cfg.dt_ms / cfg.tau_ms
    )

    print("=== MQ-001 SEQUENTIAL VISUAL STIMULUS ===")
    print("sequence:", " -> ".join(
        f"{e}/{h1}/{h2}"
        for e, h1, h2 in FROZEN_SEQUENCE
    ))
    print("hold steps:", args.hold_steps)
    print()

    step = 0

    for coord in FROZEN_SEQUENCE:
        indices = by_column[coord]

        for local_step in range(args.hold_steps):
            synaptic = graph @ spikes

            voltage *= decay
            voltage += synaptic

            stimulus = np.zeros(
                len(ids),
                dtype=np.float32,
            )

            stimulus[indices] = 1.1
            voltage += stimulus

            fired = voltage >= cfg.threshold

            spike_count = int(
                np.count_nonzero(fired)
            )

            active = int(
                np.count_nonzero(voltage)
            )

            positive = int(
                np.count_nonzero(voltage > 0)
            )

            negative = int(
                np.count_nonzero(voltage < 0)
            )

            print(
                f"step={step:03d}",
                f"column={coord[0]}/{coord[1]}/{coord[2]}",
                f"local={local_step}",
                f"spikes={spike_count}",
                f"active={active}",
                f"positive={positive}",
                f"negative={negative}",
                f"min={float(voltage.min()):.8f}",
                f"max={float(voltage.max()):.8f}",
            )

            spikes.fill(0.0)
            spikes[fired] = 1.0

            voltage[fired] = cfg.reset

            step += 1

    # One unstimulated propagation step so the final
    # retinal position can reach its immediate targets.
    synaptic = graph @ spikes
    voltage *= decay
    voltage += synaptic

    fired = voltage >= cfg.threshold

    print(
        f"step={step:03d}",
        "column=NONE",
        "local=-",
        f"spikes={int(np.count_nonzero(fired))}",
        f"active={int(np.count_nonzero(voltage))}",
        f"positive={int(np.count_nonzero(voltage > 0))}",
        f"negative={int(np.count_nonzero(voltage < 0))}",
        f"min={float(voltage.min()):.8f}",
        f"max={float(voltage.max()):.8f}",
    )


if __name__ == "__main__":
    main()
