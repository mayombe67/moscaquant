import numpy as np

from brain.mq3_pd_propagation_depth import (
    add_survival_ratios,
    build_hop_sets,
    summarize_hop_frame,
)


def test_build_hop_sets_unions_nodes_by_source_relative_depth():
    causal = {
        "targets": [
            {
                "frames": [
                    {
                        "label": "first_positive",
                        "paths": [
                            {"nodes": [10, 20, 30]},
                            {"nodes": [11, 20, 31]},
                        ],
                    }
                ]
            }
        ]
    }

    hops = build_hop_sets(causal)

    assert hops[0].tolist() == [10, 11]
    assert hops[1].tolist() == [20]
    assert hops[2].tolist() == [30, 31]


def test_summarize_hop_frame_uses_requested_indices_only():
    voltage = np.asarray([-1.0, 0.5, 2.0, 99.0])
    spikes = np.asarray([False, True, False, True])
    effective = np.asarray([0.0, 0.25, 0.75, 10.0])

    result = summarize_hop_frame(
        voltage,
        spikes,
        effective,
        np.asarray([1, 2], dtype=np.int32),
    )

    assert result["integrated_positive_voltage"] == 2.5
    assert result["mean_positive_voltage"] == 1.25
    assert result["maximum_voltage"] == 2.0
    assert result["active_neuron_count"] == 2
    assert result["active_neuron_fraction"] == 1.0
    assert result["integrated_effective_activity"] == 1.0
    assert result["mean_effective_activity"] == 0.5
    assert result["spike_count"] == 1


def test_add_survival_ratios_uses_hop0_and_previous_hop():
    hops = [
        {
            "integrated_positive_voltage": 100.0,
            "integrated_effective_activity": 50.0,
        },
        {
            "integrated_positive_voltage": 25.0,
            "integrated_effective_activity": 10.0,
        },
        {
            "integrated_positive_voltage": 5.0,
            "integrated_effective_activity": 2.0,
        },
    ]

    result = add_survival_ratios(hops)

    assert result[0]["voltage_survival_vs_hop0"] == 1.0
    assert result[0]["voltage_survival_vs_previous"] is None
    assert result[1]["voltage_survival_vs_hop0"] == 0.25
    assert result[1]["voltage_survival_vs_previous"] == 0.25
    assert result[2]["voltage_survival_vs_hop0"] == 0.05
    assert result[2]["voltage_survival_vs_previous"] == 0.2

    assert result[1]["effective_survival_vs_hop0"] == 0.2
    assert result[2]["effective_survival_vs_previous"] == 0.2
