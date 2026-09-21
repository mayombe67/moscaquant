from brain.mq5_er1_detour_stress_benchmark import MAX_BACKWARD_HOPS


def test_stress_benchmark_is_three_hops():
    assert MAX_BACKWARD_HOPS == 3
