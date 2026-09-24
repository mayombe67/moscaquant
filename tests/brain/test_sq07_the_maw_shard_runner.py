from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

import brain.sq07_the_maw_shard_runner as r
from brain.sq07_the_maw_evidence import canonical_shard


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "brain/sq07_the_maw_shard_runner.py"


def test_runner_config_preserves_human_authority_boundary():
    r.load_runner_config.cache_clear()
    config = r.load_runner_config()

    experiment = config["experiment"]
    authority = config["human_command_authority"]

    assert experiment["neural_execution_authorized"] is False
    assert experiment["result_execution_authorized"] is False

    assert authority["human_execution_authorization_required"] is True
    assert authority["automated_authorization_forbidden"] is True
    assert authority["ai_generated_authorization_forbidden"] is True
    assert authority["ci_success_is_not_execution_authorization"] is True
    assert authority["test_success_is_not_execution_authorization"] is True
    assert authority["runner_presence_is_not_execution_authorization"] is True

    assert (
        authority["authorization_must_be_explicit_and_run_specific"]
        is True
    )

    assert (
        authority["authorization_may_not_be_inferred_from_prior_runs"]
        is True
    )


def test_frozen_upstream_dependencies_are_exact():
    r.verify_frozen_dependencies.cache_clear()
    deps = r.verify_frozen_dependencies()

    assert deps["episode_executor"] == (
        "a4b85e45779ab98c9a1275a0e97ced9f1abb48bfadd974319bfcecf4305be9d8"
    )

    assert deps["evidence_writer"] == (
        "255427764b0f0b49273c27c44f000ecb50628fc7d129ec8dc9fcfddeb0af3e11"
    )

    assert deps["evidence_schema"] == (
        "c1065506a90b26856896e0a522c7023738de13b0ac5af7a17cea7973774d2f01"
    )


def test_invalid_run_ids_fail_closed():
    for value in (
        "",
        "../escape",
        "hello world",
        "x/y",
        "x" * 65,
    ):
        with pytest.raises((TypeError, ValueError)):
            r.validate_run_id(value)


def test_unauthorized_execution_calls_zero_runtime_or_neurons(
    monkeypatch,
):
    calls = {
        "runtime": 0,
        "episode": 0,
        "writer": 0,
    }

    def reject(**kwargs):
        raise r.Refusal("synthetic unauthorized")

    def runtime():
        calls["runtime"] += 1
        raise AssertionError("runtime must not load")

    def episode(**kwargs):
        calls["episode"] += 1
        raise AssertionError("episode must not execute")

    def writer(**kwargs):
        calls["writer"] += 1
        raise AssertionError("writer must not execute")

    monkeypatch.setattr(
        r,
        "verify_execution_authorization",
        reject,
    )
    monkeypatch.setattr(r, "_load_runtime_inputs", runtime)
    monkeypatch.setattr(r, "execute_condition", episode)
    monkeypatch.setattr(r, "write_shard_evidence", writer)

    with pytest.raises(r.Refusal, match="unauthorized"):
        r.run_authorized_shard(
            shard_index=0,
            run_id="synthetic-run",
            authorization_path=Path(
                "config/controls/sq07-authorizations/fake.json"
            ),
        )

    assert calls == {
        "runtime": 0,
        "episode": 0,
        "writer": 0,
    }


def test_synthetically_authorized_shard_calls_exactly_64_mock_episodes(
    monkeypatch,
    tmp_path,
):
    shard = canonical_shard(0)

    monkeypatch.setattr(
        r,
        "verify_execution_authorization",
        lambda **kwargs: {
            "authorization_path": (
                "config/controls/sq07-authorizations/fake.json"
            ),
            "authorization_sha256": "1" * 64,
            "authorization_commit": "2" * 40,
        },
    )

    monkeypatch.setattr(
        r,
        "canonical_shard",
        lambda shard_index: shard,
    )

    monkeypatch.setattr(
        r,
        "DATA_ROOT",
        tmp_path,
    )

    baseline = sparse.eye(2, format="csr")
    retina = np.asarray([0], dtype=np.int32)
    dn_indices = np.arange(1191, dtype=np.int32)

    channels = {
        "DN-C0": np.asarray([0], dtype=np.int32),
        "DN-C1": np.asarray([1], dtype=np.int32),
        "DN-C2": np.asarray([2], dtype=np.int32),
    }

    monkeypatch.setattr(
        r,
        "_load_runtime_inputs",
        lambda: (
            baseline,
            retina,
            dn_indices,
            channels,
        ),
    )

    seen = []

    def fake_episode(**kwargs):
        seen.append(kwargs["condition"])
        return {
            "condition": kwargs["condition"],
            "topology_provenance": {"synthetic": True},
            "result": {},
            "timing": {
                "started_at_utc": "synthetic",
                "completed_at_utc": "synthetic",
                "elapsed_seconds": 0.0,
            },
        }

    monkeypatch.setattr(
        r,
        "execute_condition",
        fake_episode,
    )

    writer_calls = []

    def fake_writer(**kwargs):
        writer_calls.append(kwargs)

        return (
            kwargs["output_dir"] / "manifest.json",
            kwargs["output_dir"] / "evidence.npz",
        )

    monkeypatch.setattr(
        r,
        "write_shard_evidence",
        fake_writer,
    )

    result = r.run_authorized_shard(
        shard_index=0,
        run_id="synthetic-run",
        authorization_path=Path(
            "config/controls/sq07-authorizations/fake.json"
        ),
    )

    assert len(seen) == 64
    assert len(writer_calls) == 1

    assert [row["condition_id"] for row in seen] == (
        shard["condition_ids"]
    )

    assert [row["ordinal"] for row in seen] == list(
        range(0, 64)
    )

    assert result["condition_count"] == 64
    assert result["shard_id"] == "sq07-shard-000"


def test_existing_output_refuses_before_runtime_load(
    monkeypatch,
    tmp_path,
):
    shard = canonical_shard(0)

    monkeypatch.setattr(
        r,
        "verify_execution_authorization",
        lambda **kwargs: {
            "authorization_path": "synthetic",
            "authorization_sha256": "1" * 64,
            "authorization_commit": "2" * 40,
        },
    )

    monkeypatch.setattr(
        r,
        "canonical_shard",
        lambda shard_index: shard,
    )

    monkeypatch.setattr(r, "DATA_ROOT", tmp_path)

    output = r._shard_output_dir(
        "synthetic-run",
        shard,
    )
    output.mkdir(parents=True)

    runtime_calls = 0

    def runtime():
        nonlocal runtime_calls
        runtime_calls += 1
        raise AssertionError("runtime must not load")

    monkeypatch.setattr(r, "_load_runtime_inputs", runtime)

    with pytest.raises(
        r.Refusal,
        match="already exists",
    ):
        r.run_authorized_shard(
            shard_index=0,
            run_id="synthetic-run",
            authorization_path=Path("synthetic"),
        )

    assert runtime_calls == 0


def test_runner_executes_only_one_canonical_shard_per_call():
    config = r.load_runner_config()

    assert config["execution"]["max_shards_per_invocation"] == 1
    assert config["execution"]["conditions_per_shard"] == 64


def test_source_contains_no_analysis_or_automatic_authorization():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "EXACT_INTACT",
        "EXACT_FULL13",
        "INTERMEDIATE",
        "minimal_recapitulator",
        "inactive_subset_closure",
        "strict_subset_separability",
        "result_execution_enabled = True",
        "human_execution_authorized = True",
    ]

    for token in forbidden:
        assert token not in source


def test_runner_has_no_cli_execution_surface():
    source = SOURCE.read_text(encoding="utf-8")

    forbidden = [
        "argparse",
        "--run-frozen",
        'if __name__ == "__main__"',
        "if __name__ == '__main__'",
    ]

    for token in forbidden:
        assert token not in source
