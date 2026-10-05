# Passive neural post-step sampling v1 — unqualified integration candidate

`overwatch/neural_sample_v1.py` is an additive, standard-library-only projection
hook. Existing runtime classes, CORNER runners, frozen scientific artifacts and
authority gates are unchanged. No production caller is wired to this hook.

The hook receives already computed voltage/spike arrays and explicitly supplied
step index, simulation time, UTC observation time and selected model indices.
It reads the selected current values and returns detached JSON-native records.
It imports no runtime, calls no step or effective_activity function, reads no
scientific files, creates no authority and emits no feed mode. It cannot establish
that its caller actually completed a qualified step; that is the wrapper's duty.

The inspected LIF and physiology-constrained visual runtimes reset fired-neuron
voltage before returning from step. Consequently this projection labels voltage
as **runtime_post_step_post_reset**, in **runtime_native_unscaled** units. A spike
can be true while its recorded voltage is the reset value. Do not substitute a
pre-reset voltage, threshold, normalized activity or default zero. Binary spike
values must be exactly 0 or 1; voltage is not clipped. Missing/invalid values,
nonfinite values, duplicate/unsorted indices and non-UTC timestamps refuse.

The schema is `overwatch.neural-post-step-sample.v1`. A maximum of 256 selected
model indices is supported. This is explicitly a subset readout, not a complete
population claim. The wrapper must freeze index mapping and selection before
execution, call the hook at a synchronized step boundary, and avoid concurrent
mutation of the supplied arrays during copying. Simulation time and step index
are supplied from the actual runtime protocol; the hook derives neither from a
wall clock. Observation time must be captured at the measurement boundary.

The projection always declares motor/body state unavailable and presentation
interpolation false. It makes no biological, behavioral or financial claim.
Scientific source state hashes are not invented; any canonical state digest must
come from its separately approved source contract. Public transport digests are
distinct from those scientific hashes.

Before use in a newly authorized runtime, freeze the wrapper, approved public
schema, stimulus/input/configuration/model hashes, source/image and qualification
evidence. Test instrumented versus uninstrumented computation under the applicable
parity acceptance gate. The synthetic tests here cannot grant that qualification.
Historical CORNER qualification and consumed execution authority do not extend
to a changed worker. No neural execution is authorized by this implementation.

Six tests passed using ordinary Python lists and a scalar double, without
importing NumPy, SciPy, a neural runtime, or constructing a connectome:

```bash
python3 -m unittest discover -s tests -p test_neural_sample_v1.py -v
```

The corresponding private ops candidate tests the hook with hard-coded synthetic
vectors, a bounded local spool and the private Panopticon rehearsal receiver.
Those packets are SYNTHETIC and resulting frames remain REFERENCE. This source
hook is not itself a subject publisher, a LIVE mode switch or a runtime launcher.
