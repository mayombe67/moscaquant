from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VIEWER = ROOT / "panopticon" / "debug_viewer"


def test_debug_viewer_files_exist():
    assert (VIEWER / "index.html").is_file()
    assert (VIEWER / "style.css").is_file()
    assert (VIEWER / "app.js").is_file()


def test_debug_viewer_targets_public_render_frame_endpoint():
    js = (VIEWER / "app.js").read_text(encoding="utf-8")
    assert "/api/panopticon/render-frame" in js
    assert "DEMO FEED" in js
    assert "LIVE FEED" in js


def test_debug_viewer_surfaces_cell67_and_morty():
    html = (VIEWER / "index.html").read_text(encoding="utf-8")
    assert "CELL-67" in html
    assert "MQ-001 / MORTY" in html
    assert "KILLFEED" in html


def test_debug_viewer_has_no_external_script_dependencies():
    html = (VIEWER / "index.html").read_text(encoding="utf-8")
    assert "http://" not in html
    assert "https://" not in html
