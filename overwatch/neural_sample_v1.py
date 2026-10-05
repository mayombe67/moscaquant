"""Passive post-step neural projection; no runtime imports or execution."""
from datetime import datetime
import math


def _finite(value):
    # Explicit conversion supports NumPy scalar values without importing NumPy.
    if isinstance(value, (str, bytes, bool)):
        raise ValueError('numeric runtime value required')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('finite runtime value required')
    return result


def snapshot_post_step(*, voltage, spikes, model_indices, step_index,
                       simulation_time_seconds, sample_observed_at_utc):
    """Copy selected current arrays after the caller's step has completed.

    Voltage is the actual post-reset runtime voltage, not pre-reset membrane
    voltage. Spikes must be exact binary values. No clamp, motor mapping,
    effective_activity call, wall-clock substitution or neural step occurs.
    The caller owns qualification, execution authority and synchronization.
    """
    if type(step_index) is not int or step_index < 0:
        raise ValueError('nonnegative integer step required')
    simulation_time = _finite(simulation_time_seconds)
    if simulation_time < 0:
        raise ValueError('nonnegative simulation time required')
    if type(sample_observed_at_utc) is not str or len(sample_observed_at_utc) > 40:
        raise ValueError('bounded UTC observation timestamp required')
    observed = datetime.fromisoformat(sample_observed_at_utc)
    if observed.tzinfo is None or observed.utcoffset().total_seconds() != 0:
        raise ValueError('UTC observation timestamp required')
    if type(model_indices) not in (list, tuple) or not 1 <= len(model_indices) <= 256:
        raise ValueError('bounded selected model indices required')
    if any(type(i) is not int or i < 0 for i in model_indices) or list(model_indices) != sorted(set(model_indices)):
        raise ValueError('sorted unique model indices required')
    if len(voltage) != len(spikes) or model_indices[-1] >= len(voltage):
        raise ValueError('runtime array membership mismatch')
    neurons = []
    for index in model_indices:
        v = _finite(voltage[index])
        spike = _finite(spikes[index])
        if spike not in (0.0, 1.0):
            raise ValueError('binary runtime spike required')
        neurons.append({'model_index': index, 'voltage': v, 'spike': spike == 1.0})
    return {'schema': 'overwatch.neural-post-step-sample.v1', 'step_index': step_index,
            'simulation_time_seconds': simulation_time,
            'sample_observed_at_utc': sample_observed_at_utc, 'neurons': neurons,
            'voltage_semantics': 'runtime_post_step_post_reset',
            'voltage_unit': 'runtime_native_unscaled',
            'motor_state_available': False, 'body_state_available': False,
            'presentation_interpolation': False}
