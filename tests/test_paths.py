from pathlib import Path

from config.paths import data_path, data_root


def test_default_data_root_uses_home(monkeypatch, tmp_path):
    monkeypatch.delenv("MOSCAQUANT_DATA_ROOT", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert data_root() == (tmp_path / "moscaquant-data").resolve()


def test_env_override(monkeypatch, tmp_path):
    custom = tmp_path / "mq-data"
    monkeypatch.setenv("MOSCAQUANT_DATA_ROOT", str(custom))
    assert data_root() == custom.resolve()
    assert data_path("processed", "x.npy") == custom.resolve() / "processed" / "x.npy"
