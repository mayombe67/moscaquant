from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np


DATA_ROOT = Path(
    os.environ.get("MOSCAQUANT_DATA_ROOT", str(Path.home() / "moscaquant-data"))
).expanduser().resolve()

RETINA = DATA_ROOT / "processed/visual-r1-r6-map-v1.npz"
RETINA_SHA256 = "c4655220e1aee4eab580a534df009f0a7493f075c42285b430ad1365ae37917f"

POPULATION_SIZE = 166_700
SENSORY_GAIN = 12.626497881530927
TOTAL_FRAMES = 192
FRAME_BLOCK = 16
CUE_A_ONSET = 32
CUE_B_ONSET = 96

LAYOUTS = {
    "LR": (("L", 25, 32), ("R", 21, 29)),
    "RL": (("R", 21, 29), ("L", 25, 32)),
}

EXPECTED_SCHEDULE_SHA256 = {
    "LR": "61e5b3de5ea61947f1053fc513b7a6d8f2fb17af7efca4af038e8c4024d1c3c7",
    "RL": "e044055d99fe8a19d69b4eee7bd02ba5279641c99b48d0c99cb468a5bd8f20ab",
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _normalize_eye(raw: np.ndarray) -> np.ndarray:
    if raw.dtype.kind in {"U", "S", "O"}:
        result = []
        for value in raw.tolist():
            if isinstance(value, bytes):
                value = value.decode("utf-8")
            text = str(value).strip().lower()
            if text in {"l", "left", "0"}:
                result.append("L")
            elif text in {"r", "right", "1"}:
                result.append("R")
            else:
                raise RuntimeError(f"unknown retinal eye value: {value!r}")
        return np.asarray(result)

    unique = set(int(x) for x in np.unique(raw))
    if not unique.issubset({0, 1}):
        raise RuntimeError(f"unexpected retinal eye encoding: {sorted(unique)}")
    return np.asarray(["L" if int(x) == 0 else "R" for x in raw])


def load_retina() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not RETINA.is_file():
        raise RuntimeError(f"missing frozen retinal artifact: {RETINA}")
    if _sha256_file(RETINA) != RETINA_SHA256:
        raise RuntimeError("SQ-05 retinal artifact SHA mismatch")

    data = np.load(RETINA, allow_pickle=False)
    required = {"neuron_index", "eye", "h1", "h2"}
    missing = required - set(data.files)
    if missing:
        raise RuntimeError(
            "SQ-05 retina missing arrays: " + ", ".join(sorted(missing))
        )

    return (
        np.asarray(data["neuron_index"], dtype=np.int32),
        _normalize_eye(np.asarray(data["eye"])),
        np.asarray(data["h1"], dtype=np.int32),
        np.asarray(data["h2"], dtype=np.int32),
    )


def cue_b_radius(frame: int) -> int | None:
    if frame < CUE_B_ONSET:
        return None
    if frame >= TOTAL_FRAMES:
        raise ValueError("frame outside SQ-05 stimulus schedule")
    return min(4, (frame - CUE_B_ONSET) // FRAME_BLOCK)


def _positions(
    eye: np.ndarray,
    h1: np.ndarray,
    h2: np.ndarray,
    center: tuple[str, int, int],
    radius: int,
) -> np.ndarray:
    center_eye, center_h1, center_h2 = center
    mask = (
        (eye == center_eye)
        & (np.abs(h1 - center_h1) <= radius)
        & (np.abs(h2 - center_h2) <= radius)
    )
    return np.flatnonzero(mask).astype(np.int32)


def cue_components(
    layout: str,
    frame: int,
) -> tuple[np.ndarray, np.ndarray]:
    if layout not in LAYOUTS:
        raise ValueError(f"unknown SQ-05 layout: {layout}")
    if frame < 0 or frame >= TOTAL_FRAMES:
        raise ValueError(f"frame outside SQ-05 schedule: {frame}")

    neuron_index, eye, h1, h2 = load_retina()
    cue_a_center, cue_b_center = LAYOUTS[layout]

    if frame >= CUE_A_ONSET:
        a_pos = _positions(eye, h1, h2, cue_a_center, 0)
        a_idx = np.sort(neuron_index[a_pos])
    else:
        a_idx = np.asarray([], dtype=np.int32)

    radius = cue_b_radius(frame)
    if radius is None:
        b_idx = np.asarray([], dtype=np.int32)
    else:
        b_pos = _positions(eye, h1, h2, cue_b_center, radius)
        b_idx = np.sort(neuron_index[b_pos])

    return (
        a_idx.astype(np.int32, copy=False),
        b_idx.astype(np.int32, copy=False),
    )


def stimulus_frame(layout: str, frame: int) -> np.ndarray:
    cue_a, cue_b = cue_components(layout, frame)
    stimulus = np.zeros(POPULATION_SIZE, dtype=np.float32)

    if len(cue_a):
        stimulus[cue_a] += np.float32(SENSORY_GAIN / len(cue_a))

    if len(cue_b):
        stimulus[cue_b] += np.float32(SENSORY_GAIN / len(cue_b))

    return stimulus


def schedule_sha256(layout: str) -> str:
    h = hashlib.sha256()

    for frame in range(TOTAL_FRAMES):
        cue_a, cue_b = cue_components(layout, frame)
        a_value = (
            np.float32(SENSORY_GAIN / len(cue_a))
            if len(cue_a)
            else np.float32(0)
        )
        b_value = (
            np.float32(SENSORY_GAIN / len(cue_b))
            if len(cue_b)
            else np.float32(0)
        )

        h.update(np.asarray([frame], dtype="<i4").tobytes())
        h.update(np.asarray([len(cue_a)], dtype="<i4").tobytes())
        h.update(cue_a.astype("<i4", copy=False).tobytes())
        h.update(np.asarray([a_value], dtype="<f4").tobytes())
        h.update(np.asarray([len(cue_b)], dtype="<i4").tobytes())
        h.update(cue_b.astype("<i4", copy=False).tobytes())
        h.update(np.asarray([b_value], dtype="<f4").tobytes())

    return h.hexdigest()


def assert_frozen_stimulus() -> dict[str, str]:
    observed = {layout: schedule_sha256(layout) for layout in LAYOUTS}
    if observed != EXPECTED_SCHEDULE_SHA256:
        raise RuntimeError(
            f"SQ-05 stimulus schedule SHA mismatch: {observed}"
        )
    return observed
