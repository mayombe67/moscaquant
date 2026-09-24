from pathlib import Path
import tomllib

import numpy as np

import brain.sq05_stimulus as s


ROOT = Path(__file__).resolve().parents[2]
CFG = ROOT / "config/controls/sq05-two-betrayals-stimulus-v1.toml"


def load_cfg():
    with CFG.open("rb") as f:
        return tomllib.load(f)


def test_timing_is_exact():
    cfg = load_cfg()
    timing = cfg["timing"]
    assert timing["total_frames"] == 192
    assert timing["frame_block"] == 16
    assert timing["cue_a_onset"] == 32
    assert timing["cue_b_onset"] == 96
    assert s.cue_b_radius(95) is None
    assert [s.cue_b_radius(f) for f in (96, 112, 128, 144, 160, 176)] == [
        0, 1, 2, 3, 4, 4
    ]


def test_layouts_are_counterbalanced():
    assert s.LAYOUTS["LR"] == (("L", 25, 32), ("R", 21, 29))
    assert s.LAYOUTS["RL"] == (("R", 21, 29), ("L", 25, 32))


def test_cue_a_is_six_receptors_in_both_layouts():
    for layout in ("LR", "RL"):
        cue_a, cue_b = s.cue_components(layout, 32)
        assert len(cue_a) == 6
        assert len(cue_b) == 0


def test_cue_b_expansion_counts_are_exact():
    expected = {
        "LR": [6, 36, 97, 187, 318, 318],
        "RL": [6, 45, 134, 238, 367, 367],
    }
    frames = (96, 112, 128, 144, 160, 176)

    for layout in ("LR", "RL"):
        observed = []
        for frame in frames:
            cue_a, cue_b = s.cue_components(layout, frame)
            assert len(cue_a) == 6
            observed.append(len(cue_b))
            assert set(cue_a.tolist()).isdisjoint(set(cue_b.tolist()))
        assert observed == expected[layout]


def test_each_active_cue_has_equal_total_drive():
    for layout in ("LR", "RL"):
        a_only = s.stimulus_frame(layout, 32)
        assert np.isclose(
            float(a_only.sum()),
            s.SENSORY_GAIN,
            rtol=1e-6,
            atol=1e-6,
        )

        for frame in (96, 112, 128, 144, 160, 176):
            combined = s.stimulus_frame(layout, frame)
            assert np.isclose(
                float(combined.sum()),
                2.0 * s.SENSORY_GAIN,
                rtol=1e-6,
                atol=1e-5,
            )


def test_schedule_digests_are_frozen():
    assert s.assert_frozen_stimulus() == s.EXPECTED_SCHEDULE_SHA256
    assert s.EXPECTED_SCHEDULE_SHA256 == {
        "LR": "61e5b3de5ea61947f1053fc513b7a6d8f2fb17af7efca4af038e8c4024d1c3c7",
        "RL": "e044055d99fe8a19d69b4eee7bd02ba5279641c99b48d0c99cb468a5bd8f20ab",
    }


def test_scientific_language_boundaries_are_explicit():
    cfg = load_cfg()
    boundaries = cfg["boundaries"]
    assert boundaries["not_fruit_recognition"] is True
    assert boundaries["not_olfactory_stimulation"] is True
    assert boundaries["not_hunger_induction"] is True
    assert boundaries["not_threat_perception"] is True
    assert boundaries["not_fear_induction"] is True
    assert boundaries["not_biological_looming_detector_claim"] is True
    assert cfg["experiment"]["neural_execution_authorized"] is False
    assert cfg["experiment"]["result_execution_authorized"] is False


def test_generator_has_no_neural_runtime_entrypoint():
    source = (ROOT / "brain/sq05_stimulus.py").read_text(encoding="utf-8")
    assert "PhysiologyConstrainedVisualTransductionRuntime" not in source
    assert "LIFRuntime" not in source
    assert 'if __name__ == "__main__"' not in source
