from pathlib import Path


def test_launcher_patch_is_non_result_bearing():
    text = Path(
        "tools/mq5_er_pre_audit_readiness.py"
    ).read_text(encoding="utf-8")

    assert "--run-frozen-ensemble" not in text
    assert "result_execution_enabled" in text
    assert "must remain false before audit resolution" in text

def test_safe_hold_requires_only_expected_bundle_dirty():
    text = Path(
        "tools/mq5_er_pre_audit_readiness.py"
    ).read_text(encoding="utf-8")

    safe_hold_block = text.split(
        "safe_hold = (", 1
    )[1].split(
        ")", 1
    )[0]

    assert "only_expected_bundle_dirty" in safe_hold_block


def test_safe_hold_requires_runner_freeze_ancestry():
    text = Path(
        "tools/mq5_er_pre_audit_readiness.py"
    ).read_text(encoding="utf-8")

    safe_hold_block = text.split(
        "safe_hold = (", 1
    )[1].split(
        ")", 1
    )[0]

    assert 'checks["runner_freeze_is_ancestor"]' in safe_hold_block
    assert "merge-base" in text
