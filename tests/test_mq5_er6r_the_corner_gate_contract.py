"""Gate contracts and native synthetic checks; no real scientific inputs or authority."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy import sparse
from brain import mq5_er6r_the_corner as corner
from brain import mq5_er6r_the_corner_runner as runner


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class GateContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git_calls = []
        self.git_fault = None
        inputs = {}
        for name in runner.INPUTS:
            inputs[name] = self.root / (name + '.fixture')
            inputs[name].write_bytes(b'SYNTHETIC-NOT-SCIENTIFIC-' + name.encode())
        for name, value in [('AUTHORIZATION', self.root / 'auth.json'),
                            ('QUALIFICATION', self.root / 'qual.json'),
                            ('OUTPUT', self.root / 'result.json'), ('INPUTS', inputs), ('_git', self.git)]:
            context = patch.object(runner, name, value)
            context.start()
            self.addCleanup(context.stop)
        self.qualification = {'status': 'CORNER_RUNNER_QUALIFIED_NO_NEURAL_EXECUTION',
            'runner_sha256': sha(runner.__file__), 'operator_sha256': sha(corner.__file__), 'neural_execution': False}
        self.authority = {
            'schema_version': 'moscaquant.mq5-er6r-the-corner-neural-execution-authorization/v1',
            'stage_id': corner.load_frozen_stage()['stage_id'], 'candidate_node': 1952, 'matched_control_node': 3056,
            'neural_execution_authorized': True, 'result_execution_authorized': True,
            'control_reselection_authorized': False, 'candidate_replacement_authorized': False,
            'stage_config_sha256': sha(corner.CONFIG), 'stage_protocol_sha256': sha(runner.PROTOCOL),
            'control_artifact_sha256': sha(corner.CONTROL), 'operator_sha256': sha(corner.__file__),
            'runner_sha256': sha(runner.__file__), 'implementation_git_sha': 'a' * 40,
            'source_sha256': {name: sha(path) for name, path in runner.SOURCE_FILES.items()},
            'input_sha256': {name: sha(path) for name, path in runner.INPUTS.items()},
        }
        self.save()

    def git(self, *args):
        self.git_calls.append(args)
        if args[0] == 'status':
            return ' M brain/fixture.py' if self.git_fault == 'dirty' else ''
        if args[0] == 'ls-files':
            if self.git_fault == 'untracked':
                raise corner.CornerRefusal('git provenance check failed')
            return ''
        if args[0] == 'merge-base':
            return 'b' * 40 if self.git_fault == 'ancestry' else args[1]
        raise AssertionError('unexpected Git request: ' + repr(args))

    def save(self):
        runner.QUALIFICATION.write_text(json.dumps(self.qualification))
        self.authority['qualification_sha256'] = sha(runner.QUALIFICATION)
        runner.AUTHORIZATION.write_text(json.dumps(self.authority))

    def test_nominal_gate_uses_only_synthetic_input_and_writes_no_result(self):
        self.assertEqual(runner.execution_gate(), self.authority)
        self.assertFalse(runner.OUTPUT.exists())
        self.assertEqual(list(self.root.glob('.corner-write-check-*')), [])
        self.assertTrue(any(args[:2] == ('ls-files', '--error-unmatch') for args in self.git_calls))

    def test_numeric_values_cannot_grant_boolean_permission(self):
        original = copy.deepcopy(self.authority)
        for name in ('neural_execution_authorized', 'result_execution_authorized',
                     'control_reselection_authorized', 'candidate_replacement_authorized'):
            with self.subTest(field=name):
                self.authority = copy.deepcopy(original)
                self.authority[name] = int(self.authority[name])
                self.save()
                with self.assertRaisesRegex(corner.CornerRefusal, 'authorization binding drift'):
                    runner.execution_gate()

    def test_float_node_identities_are_not_integer_bindings(self):
        original = copy.deepcopy(self.authority)
        for name in ('candidate_node', 'matched_control_node'):
            with self.subTest(field=name):
                self.authority = copy.deepcopy(original)
                self.authority[name] = float(original[name])
                self.save()
                with self.assertRaisesRegex(corner.CornerRefusal, 'authorization binding drift'):
                    runner.execution_gate()

    def test_every_fixed_authority_binding_refuses_drift(self):
        original = copy.deepcopy(self.authority)
        names = ('schema_version', 'stage_id', 'candidate_node', 'matched_control_node',
            'neural_execution_authorized', 'result_execution_authorized', 'control_reselection_authorized',
            'candidate_replacement_authorized', 'stage_config_sha256', 'stage_protocol_sha256',
            'control_artifact_sha256', 'operator_sha256', 'runner_sha256', 'qualification_sha256')
        for name in names:
            with self.subTest(field=name):
                self.authority = copy.deepcopy(original)
                runner.QUALIFICATION.write_text(json.dumps(self.qualification))
                self.authority[name] = None
                runner.AUTHORIZATION.write_text(json.dumps(self.authority))
                with self.assertRaisesRegex(corner.CornerRefusal, 'authorization binding drift'):
                    runner.execution_gate()

    def test_missing_authority_refuses_before_any_neural_access(self):
        runner.AUTHORIZATION.unlink()
        with patch.object(runner, 'build_stimuli', side_effect=AssertionError('neural access')), \
             patch.object(runner, 'load_c13', side_effect=AssertionError('real input access')), \
             patch.object(runner, 'run_arm', side_effect=AssertionError('neural execution')):
            with self.assertRaisesRegex(corner.CornerRefusal, 'qualification or authorization missing'):
                runner.execute()
        self.assertFalse(runner.OUTPUT.exists())

    def test_qualification_status_and_source_bindings_refuse_drift(self):
        original = copy.deepcopy(self.qualification)
        for name, value in [('status', 'unqualified'), ('runner_sha256', 'wrong'),
                            ('operator_sha256', 'wrong'), ('neural_execution', 0)]:
            with self.subTest(field=name):
                self.qualification = copy.deepcopy(original)
                self.qualification[name] = value
                self.save()
                with self.assertRaisesRegex(corner.CornerRefusal, 'qualification drift'):
                    runner.execution_gate()

    def test_source_manifest_missing_extra_and_each_hash_refuse(self):
        original = copy.deepcopy(self.authority)
        for value in (None, {}, {**original['source_sha256'], 'unexpected': 'f' * 64}):
            self.authority = copy.deepcopy(original)
            self.authority['source_sha256'] = value
            self.save()
            with self.assertRaisesRegex(corner.CornerRefusal, 'source hash manifest missing'):
                runner.execution_gate()
        for name in original['source_sha256']:
            with self.subTest(source=name):
                self.authority = copy.deepcopy(original)
                self.authority['source_sha256'][name] = 'f' * 64
                self.save()
                with self.assertRaisesRegex(corner.CornerRefusal, 'source hash drift'):
                    runner.execution_gate()

    def test_git_dirty_untracked_and_ancestry_refuse(self):
        for fault, message in [('dirty', 'working tree'), ('untracked', 'provenance'), ('ancestry', 'not ancestral')]:
            with self.subTest(git=fault):
                self.git_fault = fault
                with self.assertRaisesRegex(corner.CornerRefusal, message):
                    runner.execution_gate()

    def test_implementation_commit_must_be_full_hex(self):
        for value in (None, 'a' * 39, 'g' * 40, '--' + 'a' * 38):
            with self.subTest(commit=value):
                self.authority['implementation_git_sha'] = value
                self.save()
                with self.assertRaisesRegex(corner.CornerRefusal, 'implementation commit missing'):
                    runner.execution_gate()

    def test_input_manifest_and_each_missing_or_changed_input_refuse(self):
        original = copy.deepcopy(self.authority)
        for value in (None, {}, {**original['input_sha256'], 'extra': 'f' * 64}):
            self.authority = copy.deepcopy(original)
            self.authority['input_sha256'] = value
            self.save()
            with self.assertRaisesRegex(corner.CornerRefusal, 'input hash manifest missing'):
                runner.execution_gate()
        self.authority = original
        self.save()
        for name, path in runner.INPUTS.items():
            raw = path.read_bytes()
            with self.subTest(input=name, state='changed'):
                path.write_bytes(b'changed')
                with self.assertRaisesRegex(corner.CornerRefusal, 'input missing or hash drift'):
                    runner.execution_gate()
            path.unlink()
            with self.subTest(input=name, state='missing'):
                with self.assertRaisesRegex(corner.CornerRefusal, 'input missing or hash drift'):
                    runner.execution_gate()
            path.write_bytes(raw)

    def test_output_exists_missing_directory_and_failed_write_refuse(self):
        runner.OUTPUT.write_bytes(b'prior-result')
        with self.assertRaisesRegex(corner.CornerRefusal, 'result already exists'):
            runner.execution_gate()
        self.assertEqual(runner.OUTPUT.read_bytes(), b'prior-result')
        runner.OUTPUT.unlink()
        with patch.object(runner, 'OUTPUT', self.root / 'missing' / 'result.json'):
            with self.assertRaisesRegex(corner.CornerRefusal, 'result directory missing'):
                runner.execution_gate()
        with patch.object(runner.tempfile, 'NamedTemporaryFile', side_effect=OSError('write denied')):
            with self.assertRaisesRegex(corner.CornerRefusal, 'write path unavailable'):
                runner.execution_gate()


class NativeSyntheticContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        directory = Path(self.temporary.name)
        relay, graded = directory / 'relay.npz', directory / 'graded.npz'
        np.savez(relay, neuron_index=np.arange(4000, 6430), body_id=np.arange(2430), type=np.full(2430, 'L1'))
        np.savez(graded, neuron_index=np.arange(6500, 11990), type=np.resize(np.array(['Tm2', 'Tm3', 'Tm4']), 5490))
        for name, value in [('RELAY', relay), ('GRADED', graded)]:
            context = patch.object(runner, name, value)
            context.start()
            self.addCleanup(context.stop)
        self.graph = sparse.csr_matrix(([0.4, 0.4, 0.2, -0.1],
            ([55, 92, 656, 4000], [1952, 3056, 6500, 0])), shape=(12000, 12000), dtype=np.float32)
        self.retina = np.array([0], dtype=np.int32)

    def runtime(self, modifier=None):
        return runner.PhysiologyConstrainedVisualTransductionRuntime(connectome=self.graph,
            retinal_indices=self.retina, relay_artifact=runner.RELAY, graded_artifact=runner.GRADED,
            config=runner.VisualTransductionConfig(release_gain=runner.RELEASE_GAIN), activity_modifier=modifier)

    def test_p0_matches_native_for_all_192_synthetic_frames(self):
        stimuli = []
        for frame in range(192):
            stimulus = np.zeros(12000, dtype=np.float32)
            stimulus[[1952, 3056, 6500, 0]] = 1.1 if frame % 7 == 0 else 0.07
            stimuli.append(stimulus)
        targets = (55, 92, 656, 1952, 3056, 6500, 4000)
        native = self.runtime()
        voltage, spikes = [], []
        for frame, stimulus in enumerate(stimuli):
            native.step(stimulus, generation=frame)
            voltage.append(native.voltage[list(targets)].copy())
            spikes.append(native.spikes[list(targets)].copy())
        actual = runner.run_arm('P0', self.graph, self.retina, targets, stimuli)
        np.testing.assert_array_equal(actual['responder_voltage'], voltage)
        np.testing.assert_array_equal(actual['responder_spikes'], spikes)

    def test_both_native_hooks_change_only_output_and_preserve_state(self):
        for arm, target, downstream in [('P1952', 1952, 55), ('PCONTROL', 3056, 92)]:
            with self.subTest(arm=arm):
                observed = []
                silencer = corner.arm_modifier(arm, population_size=12000)
                native = self.runtime()
                def inspect(activity, frame):
                    voltage, spikes = treated.voltage.copy(), treated.spikes.copy()
                    result = silencer(activity, frame)
                    np.testing.assert_array_equal(treated.voltage, voltage)
                    np.testing.assert_array_equal(treated.spikes, spikes)
                    self.assertEqual(np.flatnonzero(result != activity).tolist(), [target])
                    self.assertEqual(result[6500], activity[6500])
                    observed.append(frame)
                    return result
                treated = self.runtime(inspect)
                for runtime in (native, treated):
                    runtime.spikes[[1952, 3056, 0]] = 1.0
                    runtime.voltage[[1952, 3056]] = 0.3
                    runtime.voltage[6500] = 0.5
                stimulus = np.zeros(12000, dtype=np.float32)
                native.step(stimulus, generation=0)
                treated.step(stimulus, generation=0)
                self.assertEqual(observed, [0])
                self.assertEqual(np.flatnonzero(native.voltage != treated.voltage).tolist(), [downstream])
                np.testing.assert_array_equal(native.spikes, treated.spikes)
                self.assertGreater(native.voltage[downstream], treated.voltage[downstream])


if __name__ == '__main__':
    unittest.main()
