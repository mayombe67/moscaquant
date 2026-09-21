from brain.mq5_er1_detour_candidates import (
    EdgeTrace,
    classify_candidate_family,
    rank_candidates,
)


def make_trace(
    pre,
    post,
    *,
    hop=1,
    a=(0.0, 0.0, 0.0),
    c=(0.0, 1.0, 0.0),
    lesion=(0.0, 0.5, 0.0),
):
    return EdgeTrace(
        presynaptic=pre,
        postsynaptic=post,
        hop_from_target=hop,
        a_baseline=tuple(a),
        c_baseline=tuple(c),
        c_lesion13=tuple(lesion),
    )


def test_requires_both_encoding_divergence_and_lesion_persistence():
    traces = [
        make_trace(1, 9, c=(0, 0, 0), lesion=(0, 1, 0)),
        make_trace(2, 9, c=(0, 1, 0), lesion=(0, 0, 0)),
        make_trace(3, 9, c=(0, 1, 0), lesion=(0, 0.5, 0)),
    ]

    ranked = rank_candidates(
        target=9,
        onset_frame=2,
        traces=traces,
    )

    assert [(c.presynaptic, c.postsynaptic) for c in ranked] == [(3, 9)]


def test_post_onset_activity_does_not_create_candidate():
    trace = make_trace(
        3,
        9,
        a=(0, 0, 0, 0),
        c=(0, 0, 0, 2),
        lesion=(0, 0, 0, 2),
    )

    ranked = rank_candidates(
        target=9,
        onset_frame=2,
        traces=[trace],
    )

    assert ranked == []


def test_ranking_is_score_then_hop_then_edge_id_and_capped_at_five():
    traces = [
        make_trace(pre, 9, hop=2 if pre == 5 else 1)
        for pre in range(1, 8)
    ]

    ranked = rank_candidates(
        target=9,
        onset_frame=2,
        traces=traces,
    )

    assert len(ranked) == 5
    assert [c.presynaptic for c in ranked] == [1, 2, 3, 4, 6]


def test_focused_requires_same_directed_edge_in_three_targets():
    shared = make_trace(7, 8)

    by_target = {}
    for target in [55, 92, 656]:
        by_target[target] = rank_candidates(
            target=target,
            onset_frame=2,
            traces=[shared],
        )

    label = classify_candidate_family(
        by_target,
        affected_targets=[55, 92, 656, 126002, 137122],
    )

    assert label == "FOCUSED_DETOUR_CANDIDATES"


def test_diffuse_when_candidates_exist_without_three_target_recurrence():
    by_target = {
        55: rank_candidates(
            target=55,
            onset_frame=2,
            traces=[make_trace(1, 55)],
        ),
        92: rank_candidates(
            target=92,
            onset_frame=2,
            traces=[make_trace(2, 92)],
        ),
    }

    label = classify_candidate_family(
        by_target,
        affected_targets=[55, 92, 656, 126002, 137122],
    )

    assert label == "DIFFUSE_DETOUR_CANDIDATES"


def test_no_clear_when_all_lists_empty():
    label = classify_candidate_family(
        {},
        affected_targets=[55, 92, 656, 126002, 137122],
    )

    assert label == "NO_CLEAR_DETOUR_CANDIDATES"
