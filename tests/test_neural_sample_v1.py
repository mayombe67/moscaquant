import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'overwatch/neural_sample_v1.py'
spec = importlib.util.spec_from_file_location('neural_sample', PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SampleTests(unittest.TestCase):
    def sample(self, **changes):
        args = dict(voltage=[0.0, -0.125, 0.75], spikes=[1.0, 0.0, 0.0],
                    model_indices=[0, 2], step_index=0, simulation_time_seconds=0.001,
                    sample_observed_at_utc='2026-10-05T16:00:00+00:00')
        args.update(changes)
        return m.snapshot_post_step(**args)

    def test_exact_post_reset_values_and_explicit_interpretation(self):
        p = self.sample()
        self.assertEqual(p['neurons'], [{'model_index': 0, 'voltage': 0.0, 'spike': True},
                                         {'model_index': 2, 'voltage': 0.75, 'spike': False}])
        self.assertEqual(p['voltage_semantics'], 'runtime_post_step_post_reset')
        self.assertFalse(p['motor_state_available'])
        self.assertFalse(p['body_state_available'])
        self.assertFalse(p['presentation_interpolation'])
        self.assertNotIn('feed_mode', p)
        json.dumps(p, allow_nan=False)

    def test_read_only_copy_does_not_alias_or_modify_arrays(self):
        voltage, spikes = [0.0, 0.3], [1.0, 0.0]
        p = self.sample(voltage=voltage, spikes=spikes, model_indices=[0, 1])
        self.assertEqual(voltage, [0.0, 0.3])
        self.assertEqual(spikes, [1.0, 0.0])
        voltage[1], spikes[1] = 99, 1
        self.assertEqual(p['neurons'][1]['voltage'], 0.3)
        self.assertFalse(p['neurons'][1]['spike'])

    def test_runtime_scalar_conversion_without_numpy_import(self):
        class Scalar:
            def __float__(self):
                return 0.625
        self.assertEqual(self.sample(voltage=[0, 0, Scalar()])['neurons'][1]['voltage'], 0.625)

    def test_no_clipping_defaults_or_nonbinary_spikes(self):
        self.assertEqual(self.sample(voltage=[0, 0, -123.0])['neurons'][1]['voltage'], -123.0)
        for changes in [dict(voltage=[0, 0, float('nan')]), dict(spikes=[0.5, 0, 0]),
                        dict(voltage=[0, 0, '0.75']), dict(spikes=[True, 0, 0])]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.sample(**changes)

    def test_missing_duplicate_unsorted_or_wrong_model_membership_refuses(self):
        for changes in [dict(model_indices=[]), dict(model_indices=[2, 0]),
                        dict(model_indices=[0, 0]), dict(model_indices=[True]),
                        dict(model_indices=[3]), dict(spikes=[0])]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.sample(**changes)

    def test_clock_and_step_metadata_are_not_invented(self):
        self.assertEqual(self.sample()['simulation_time_seconds'], 0.001)
        for changes in [dict(step_index=True), dict(simulation_time_seconds=-1),
                        dict(simulation_time_seconds=float('inf')),
                        dict(sample_observed_at_utc='2026-10-05T16:00:00')]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.sample(**changes)


if __name__ == '__main__':
    unittest.main()
