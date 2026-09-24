from __future__ import annotations

from pathlib import Path

import pytest

import brain.sq07_the_maw_readiness as r


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "brain/sq07_the_maw_readiness.py"


def test_readiness_config_is_inert():
    r.load_config.cache_clear()
    config = r.load_config()

    readiness = config["readiness"]
    boundaries = config["boundaries"]

    assert readiness["may_execute"] is False
    assert readiness["human_execution_authorization_state"] == "ABSENT"
    assert readiness["result_execution_state"] == "NOT_STARTED"

    assert all(value is False for value in boundaries.values())


def test_frozen_execution_stack_hashes_are_exact():
    r.verify_frozen_dependencies.cache_clear()
    deps = r.verify_frozen_dependencies()

    assert deps["condition_plan_sha256"] == (
        "850ae560ab1b25c65f9932615f8ea1851781881c4492672767bcda692667becb"
    )

    assert deps["shard_plan_sha256"] == (
        "9039b8e708c2ffdb74436e5c6fdc8f7d2f38f3f3fb27fd7478dd2cc8101d2a55"
    )

    assert deps["file_sha256"]["shard_runner"] == (
        "bd736984acad6bbdceb812ca84ee6d413acaaa0f864f4a48899f9fbfacf87312"
    )


def test_complete_universe_is_exact():
    universe = r.verify_complete_universe()

    assert universe == {
        "mask_count": 8192,
        "condition_count": 32768,
        "unique_condition_count": 32768,
        "shard_count": 512,
        "conditions_per_shard": 64,
        "masks_per_shard": 16,
        "overlap_count": 0,
        "omission_count": 0,
        "canonical_order_exact": True,
    }


def test_condition_coordinate_extremes():
    assert r.expected_condition_id(0) == (
        "sq07:0000000000000:LR:r1"
    )

    assert r.expected_condition_id(3) == (
        "sq07:0000000000000:RL:r2"
    )

    assert r.expected_condition_id(32767) == (
        "sq07:1111111111111:RL:r2"
    )


def test_clean_preexecution_state_reports_ready_but_not_authorized(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        r,
        "verify_frozen_dependencies",
        lambda: {"synthetic": True},
    )

    monkeypatch.setattr(
        r,
        "verify_complete_universe",
        lambda: {
            "mask_count": 8192,
            "condition_count": 32768,
            "unique_condition_count": 32768,
            "shard_count": 512,
            "conditions_per_shard": 64,
            "masks_per_shard": 16,
            "overlap_count": 0,
            "omission_count": 0,
            "canonical_order_exact": True,
        },
    )

    monkeypatch.setattr(
        r,
        "git_state",
        lambda: {
            "head": "f" * 40,
            "branch": "science/sq07-the-maw",
            "clean": True,
            "implementation_commit_is_ancestor": True,
        },
    )

    monkeypatch.setattr(
        r,
        "authorization_files",
        lambda: [],
    )

    monkeypatch.setattr(
        r,
        "RESULT_ROOT",
        tmp_path / "absent-results",
    )

    report = r.evaluate_readiness()

    assert report["scientific_readiness"] == "READY"
    assert report["human_execution_authorization"] == "ABSENT"
    assert report["result_execution"] == "NOT_STARTED"
    assert report["real_episode_count"] == 0
    assert report["may_execute"] is False
    assert report["ready_but_not_authorized"] is True


def test_authorization_presence_breaks_preexecution_readiness(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        r,
        "verify_frozen_dependencies",
        lambda: {"synthetic": True},
    )

    monkeypatch.setattr(
        r,
        "verify_complete_universe",
        lambda: {
            "mask_count": 8192,
            "condition_count": 32768,
            "unique_condition_count": 32768,
            "shard_count": 512,
            "conditions_per_shard": 64,
            "masks_per_shard": 16,
            "overlap_count": 0,
            "omission_count": 0,
            "canonical_order_exact": True,
        },
    )

    monkeypatch.setattr(
        r,
        "git_state",
        lambda: {
            "head": "f" * 40,
            "branch": "science/sq07-the-maw",
            "clean": True,
            "implementation_commit_is_ancestor": True,
        },
    )

    monkeypatch.setattr(
        r,
        "authorization_files",
        lambda: ["config/controls/sq07-authorizations/auth.json"],
    )

    monkeypatch.setattr(
        r,
        "RESULT_ROOT",
        tmp_path / "absent-results",
    )

    report = r.evaluate_readiness()

    assert report["scientific_readiness"] == "NOT_READY"
    assert report["human_execution_authorization"] == "PRESENT"
    assert report["may_execute"] is False


def test_result_root_presence_breaks_preexecution_readiness(
    monkeypatch,
    tmp_path,
):
    result_root = tmp_path / "results"
    result_root.mkdir()

    monkeypatch.setattr(
        r,
        "verify_frozen_dependencies",
        lambda: {"synthetic": True},
    )

    monkeypatch.setattr(
        r,
        "verify_complete_universe",
        lambda: {
            "mask_count": 8192,
            "condition_count": 32768,
            "unique_condition_count": 32768,
            "shard_count": 512,
            "conditions_per_shard": 64,
            "masks_per_shard": 16,
            "overlap_count": 0,
            "omission_count": 0,
            "canonical_order_exact": True,
        },
    )

    monkeypatch.setattr(
        r,
        "git_state",
        lambda: {
            "head": "f" * 40,
            "branch": "science/sq07-the-maw",
            "clean": True,
            "implementation_commit_is_ancestor": True,
        },
    )

    monkeypatch.setattr(r, "authorization_files", lambda: [])
    monkeypatch.setattr(r, "RESULT_ROOT", result_root)

    report = r.evaluate_readiness()

    assert report["scientific_readiness"] == "NOT_READY"
    assert report["result_execution"] == "RESULT_ROOT_PRESENT"
    assert report["real_episode_count"] is None
    assert report["may_execute"] is False


def test_dirty_tree_breaks_readiness(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setattr(
        r,
        "verify_frozen_dependencies",
        lambda: {"synthetic": True},
    )

    monkeypatch.setattr(
        r,
        "verify_complete_universe",
        lambda: {
            "mask_count": 8192,
            "condition_count": 32768,
            "unique_condition_count": 32768,
            "shard_count": 512,
            "conditions_per_shard": 64,
            "masks_per_shard": 16,
            "overlap_count": 0,
            "omission_count": 0,
            "canonical_order_exact": True,
        },
    )

    monkeypatch.setattr(
        r,
        "git_state",
        lambda: {
            "head": "f" * 40,
            "branch": "science/sq07-the-maw",
            "clean": False,
            "implementation_commit_is_ancestor": True,
        },
    )

    monkeypatch.setattr(r, "authorization_files", lambda: [])
    monkeypatch.setattr(
        r,
        "RESULT_ROOT",
        tmp_path / "absent-results",
    )

    report = r.evaluate_readiness()

    assert report["scientific_readiness"] == "NOT_READY"
    assert report["checks"]["git_worktree_clean"] is False
    assert report["may_execute"] is False


def test_readiness_source_has_no_execution_surface():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "execute_condition",
        "run_authorized_shard",
        "run_episode",
        "build_stimuli",
        "build_mask_subset",
        "PhysiologyConstrainedVisualTransductionRuntime",
        "sparse.load_npz",
        "np.load",
        "--run-frozen",
        "human_execution_authorized",
        "result_execution_enabled",
    ]

    for token in forbidden:
        assert token not in source


def test_readiness_source_has_no_artifact_write_surface():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "write_text(",
        "write_bytes(",
        "json.dump(",
        "np.save(",
        "np.savez",
        "os.replace(",
        "mkdir(",
        "unlink(",
    ]

    for token in forbidden:
        assert token not in source
