"""MQ-001 biologically mapped heartbeat experiment."""

import argparse
from pathlib import Path

import numpy as np
from scipy import sparse

from brain.populations import visual_r1_r6_indices
from brain.runtime import LIFRuntime
from config.loader import load_runtime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default="habitat")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--stimulus", type=float, default=1.1)

    args = parser.parse_args()

    runtime = load_runtime(args.runtime)
    data_dir = Path(runtime["paths"]["data_dir"])

    processed = data_dir / "processed"
    raw = data_dir / "raw"

    graph_path = processed / "connectome-baseline-v1.npz"
    ids_path = processed / "neuron_ids.npy"
    annotations_path = (
        raw
        / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
    )

    print("Loading MQ-001 connectome")
    graph = sparse.load_npz(graph_path).tocsr()
    neuron_ids = np.load(ids_path, mmap_mode="r")

    print(f"Neurons: {graph.shape[0]:,}")
    print(f"Edges:   {graph.nnz:,}")

    r1_r6 = visual_r1_r6_indices(
        annotations_path,
        neuron_ids,
    )

    print(f"R1-R6 photoreceptors: {len(r1_r6):,}")

    brain = LIFRuntime(graph)

    stimulus = np.zeros(graph.shape[0], dtype=np.float32)
    stimulus[r1_r6] = args.stimulus

    print()
    print("=== MQ-001 VISUAL HEARTBEAT ===")

    for step in range(args.steps):
        current_stimulus = stimulus if step == 0 else None

        spikes = brain.step(current_stimulus)

        active_voltage = np.count_nonzero(brain.voltage)
        positive_voltage = np.count_nonzero(brain.voltage > 0)
        negative_voltage = np.count_nonzero(brain.voltage < 0)

        print(
            f"step={step:03d} "
            f"spikes={int(spikes.sum()):,} "
            f"active={active_voltage:,} "
            f"positive={positive_voltage:,} "
            f"negative={negative_voltage:,} "
            f"mean={brain.voltage.mean():.8f} "
            f"min={brain.voltage.min():.8f} "
            f"max={brain.voltage.max():.8f}"
        )


if __name__ == "__main__":
    main()
