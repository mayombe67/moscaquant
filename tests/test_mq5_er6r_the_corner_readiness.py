from brain import mq5_er6r_the_corner_readiness as readiness


def test_readiness_never_promotes_presence_to_qualification(monkeypatch, tmp_path):
    runner = readiness.runner
    monkeypatch.setattr(runner, "_git", lambda *args: "" if args[0] == "status" else "a" * 40)
    missing = tmp_path / "input"
    monkeypatch.setattr(runner, "INPUTS", {"connectome": missing})
    monkeypatch.setattr(runner, "QUALIFICATION", tmp_path / "qualification")
    monkeypatch.setattr(runner, "AUTHORIZATION", tmp_path / "authorization")
    monkeypatch.setattr(runner, "OUTPUT", tmp_path / "results" / "result.json")
    before = sorted(tmp_path.iterdir())
    report = readiness.inspect_readiness()
    assert "missing_input:connectome" in report["observed_blockers"]
    assert sorted(tmp_path.iterdir()) == before
    for path in (missing, runner.QUALIFICATION, runner.AUTHORIZATION):
        path.write_text("invalid data")
    runner.OUTPUT.parent.mkdir()
    report = readiness.inspect_readiness()
    assert report["observed_blockers"] == []
    assert report["qualification_granted"] is False
    assert report["execution_authorized"] is False
    assert report["status"] == "INVENTORY_ONLY_NOT_EXECUTION_QUALIFICATION"
