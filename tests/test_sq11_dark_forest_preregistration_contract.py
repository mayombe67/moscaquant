from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PREREG = (
    ROOT
    / "docs/experiments/"
    "sq11-dark-forest-preregistration.md"
)


def text():
    return PREREG.read_text()


def test_dark_forest_is_pre_execution():
    t = text()

    assert (
        "Status: PREREGISTERED / PRE-EXECUTION"
        in t
    )


def test_dark_forest_inherits_exact_cube():
    t = text()

    for mask in (
        "000",
        "001",
        "010",
        "011",
        "100",
        "101",
        "110",
        "111",
    ):
        assert f"`{mask}`" in t

    assert "`16`" in t


def test_dark_forest_freezes_body_identity():
    t = text()

    assert "65084 -> 137122" in t
    assert "128590 -> 317" in t
    assert "135589 -> 126002" in t


def test_dark_forest_moves_primary_readout_to_p3():
    t = text()

    assert (
        "P3 is the earliest phase"
        in t
    )

    assert (
        "captured runtime P3"
        in t
    )


def test_dark_forest_requires_local_presynaptic_state():
    t = text()

    assert (
        "union of all presynaptic neurons"
        in t
    )

    assert (
        "static ordered CSR column indices"
        in t
    )

    assert (
        "static float32 CSR weights"
        in t
    )


def test_dark_forest_requires_exact_replay():
    t = text()

    assert (
        "Exact means exact float32 equality."
        in t
    )

    assert (
        "No tolerance substitution is allowed."
        in t
    )


def test_dark_forest_calibrates_before_execution():
    t = text()

    assert (
        "Before neural execution"
        in t
    )

    assert (
        "must not inspect SQ-11 neural evidence"
        in t
    )

    assert (
        "No post-result tolerance"
        in t
    )


def test_dark_forest_freezes_all_12_contrasts():
    t = text()

    expected = (
        "000 -> 100",
        "001 -> 101",
        "010 -> 110",
        "011 -> 111",
        "000 -> 010",
        "001 -> 011",
        "100 -> 110",
        "101 -> 111",
        "000 -> 001",
        "010 -> 011",
        "100 -> 101",
        "110 -> 111",
    )

    for contrast in expected:
        assert contrast in t


def test_dark_forest_freezes_primary_classes():
    t = text()

    for classification in (
        "DIRECT_TERM_EXACT_FLOAT32",
        "DIRECT_TERM_WITH_FLOAT32_ROUNDING_PATH",
        "SOURCE_STATE_DIVERGES_BEFORE_OR_AT_P3",
        "LOCAL_REPLAY_MISMATCH",
        "NO_P3_DIVERGENCE",
    ):
        assert classification in t


def test_dark_forest_freezes_decomposition():
    t = text()

    assert (
        "runtime_delta ="
        in t
    )

    assert (
        "direct_term ="
        in t
    )

    assert (
        "rounding_path_residual ="
        in t
    )


def test_dark_forest_forbids_post_result_rules():
    t = text()

    assert (
        "No additional conditions or numerical rules "
        "may be introduced after inspecting SQ-11 results."
        in t
    )


def test_dark_forest_preserves_claim_boundary():
    t = text()

    assert (
        "A direct-local computational mechanism "
        "must not be promoted into a biological claim."
        in t
    )
