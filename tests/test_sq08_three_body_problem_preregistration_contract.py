from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs/experiments/sq08-three-body-problem-preregistration.md"


def prereg():
    return PREREG.read_text()


def test_sq08_contains_complete_boolean_cube():
    text = prereg()
    for mask in ("000", "001", "010", "011", "100", "101", "110", "111"):
        assert f"`{mask}`" in text


def test_sq08_freezes_three_way_inclusion_exclusion_term():
    text = prereg()
    assert (
        "`I_ABC = Y111 - Y110 - Y101 - Y011 + Y100 + Y010 + Y001 - Y000`"
        in text
    )


def test_sq08_freezes_pairwise_terms():
    text = prereg()
    assert "`I_AB = Y110 - Y100 - Y010 + Y000`" in text
    assert "`I_AC = Y101 - Y100 - Y001 + Y000`" in text
    assert "`I_BC = Y011 - Y010 - Y001 + Y000`" in text


def test_sq08_requires_tolerance_before_results():
    text = prereg()
    assert "inherits the frozen SQ-07 primary-fingerprint exactness contract" in text
    assert "symmetric normalized L2 distance: `<= 1e-9`" in text
    assert "maximum absolute distance: `<= 1e-12`" in text
    assert "The tolerances may not be changed after inspecting SQ-08 results." in text


def test_sq08_separates_interaction_from_mechanism():
    text = prereg()
    assert "distinguishes mathematical interaction from mechanistic interpretation" in text
    assert "A response pattern alone is insufficient" in text
    assert "It does not determine the anatomical cause" in text


def test_sq08_preserves_unresolved_as_valid_result():
    text = prereg()
    assert "### UNRESOLVED" in text
    assert "`UNRESOLVED` is scientifically acceptable." in text


def test_sq08_requires_explicit_spike_boundary():
    text = prereg()
    assert "spike status or explicit spike-unavailable status" in text


def test_sq08_does_not_promote_computational_result_to_biology():
    text = prereg()
    assert "It does not by itself establish a biological mechanism." in text
    assert "beyond the frozen computational endpoint" in text


def test_sq08_inherits_sq07_exactness_contract():
    text = prereg()
    assert "`positive_membrane_voltage`" in text
    assert "`192 x 1191`" in text
    assert "symmetric normalized L2 distance: `<= 1e-9`" in text
    assert "maximum absolute distance: `<= 1e-12`" in text
    assert "`THREE_WAY_EXACT_ZERO`" in text
    assert "`THREE_WAY_NONZERO`" in text
    assert "Y111 - Y111_pairwise = I_ABC" in text
    assert "No post-result threshold may be introduced." in text


def test_sq08_freezes_body_identity_and_bit_order():
    text = prereg()

    assert "`BODY A = E10`" in text
    assert "presynaptic neuron: `65084`" in text
    assert "postsynaptic neuron / accepted responder: `137122`" in text

    assert "`BODY B = E11`" in text
    assert "presynaptic neuron: `128590`" in text
    assert "postsynaptic neuron / accepted responder: `317`" in text

    assert "`BODY C = E12`" in text
    assert "presynaptic neuron: `135589`" in text
    assert "postsynaptic neuron / accepted responder: `126002`" in text

    assert "`E10, E11, E12`" in text
    assert "`A, B, C`" in text
    assert "must not be reordered after result inspection" in text


def test_sq08_freezes_mechanistic_topology_rule():
    text = prereg()

    assert "## Frozen mechanistic readout topology" in text
    assert "maximum hop depth is frozen at:" in text
    assert "`4`" in text

    assert "`branch_A` = nodes reachable from `137122`" in text
    assert "`branch_B` = nodes reachable from `317`" in text
    assert "`branch_C` = nodes reachable from `126002`" in text

    assert "`AB = branch_A intersection branch_B`" in text
    assert "`AC = branch_A intersection branch_C`" in text
    assert "`BC = branch_B intersection branch_C`" in text
    assert "`ABC = branch_A intersection branch_B intersection branch_C`" in text

    assert "Membership is determined before SQ-08 result execution." in text
    assert "Structural convergence alone is not evidence of functional mediation" in text


def test_sq08_localizes_interaction_in_time_without_overclaiming():
    text = prereg()
    normalized = " ".join(text.split())

    assert "first frame of nonzero `I_ABC`" in text
    assert "interaction-localization observation only" in normalized
    assert "does not by itself establish biological necessity" in normalized


def test_sq08_preserves_pre_result_topology_amendment():
    text = prereg()
    normalized = " ".join(text.split())

    assert (
        "sq08-three-body-problem-topology-amendment.md"
        in text
    )
    assert (
        "exactly 18 nodes"
        in normalized
    )
    assert (
        "must not be deleted or rewritten"
        in normalized
    )


def test_sq08_inherits_sq07_lesion_mask_semantics():
    text = prereg()
    normalized = " ".join(text.split())

    assert "`0` means the frozen BODY edge is retained" in normalized
    assert "`1` means the frozen BODY edge is zeroed" in normalized
    assert "`Y000` — all three frozen BODY edges retained" in normalized
    assert "`Y111` — BODY A + BODY B + BODY C all zeroed" in normalized


def test_sq08_freezes_post_step_observation_semantics():
    text = prereg()
    normalized = " ".join(text.split())

    assert "immediately after each invocation" in normalized
    assert "spike state has been committed" in normalized
    assert "membrane voltage reset" in normalized
    assert "voltage and spike trajectories are paired readouts" in normalized
    assert "must not infer framewise activation from voltage alone" in normalized
    assert "The observer is passive" in normalized
