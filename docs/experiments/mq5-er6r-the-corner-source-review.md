# THE CORNER — source review and qualification boundary

Status: **SOURCE CONTRACTS TESTED — EXECUTION QUALIFICATION PENDING**.

The recovered local runner commit `7cee132d18a05694e92470394285e511df26ec17`
adds the three-arm executor and refusal/no-overwrite tests. It follows the
[frozen execution protocol](mq5-er6r-the-corner-execution-protocol.md).
Candidate `1952`, matched control `3056`, primary onset endpoint, 192-frame
window, and disabled preregistration are unchanged. The recovered commit was
local-only when this review began; the remote branch was at `a39d61a`.

## Evidence obtained

The original runner symmetry test substitutes a fake runtime. It establishes
argument routing and operator selection, but cannot establish where the real
runtime applies the hook. The additional
[native-runtime contracts](../../tests/test_mq5_er6r_the_corner_native_runtime.py)
use the actual physiology runtime with explicitly synthetic artifacts:

- P0 responder voltage and spikes equal a direct native-runtime invocation
  for all 192 frames, including retinal-release and graded activity pathways.
- Both candidate and control interventions change only the target activity
  entry at the native hook, after native activity calculation.
- Calling the operator leaves membrane and spike arrays unchanged. The
  synthetic downstream response demonstrates that output transmission changes.
- The candidate/control synthetic graphs are symmetric. These are software
  contracts, not evidence of C13 necessity or biological behavior.

The focused CORNER, WARRANT, and WAY DOWN suites passed **60 tests** in this
workspace using `python3 -m pytest -q tests/test_mq5_er6r_the_corner*.py
 tests/test_mq5_er6r_the_warrant*.py tests/test_mq5_er5r_way_down_in_the_hole*.py`.
This is not a RASPUTIN runtime acceptance or an authoritative neural result.

## Remaining qualification work

The read-only inventory can be run from the repository with:

```bash
python3 -m brain.mq5_er6r_the_corner_readiness
```

It never emits the runner's accepted qualification status and never creates
an authorization, result, data directory, or scientific input. Presence checks
are explicitly distinct from hash validation or write-path acceptance. A test
proves that even apparently complete files containing invalid data cannot be
promoted to qualification by this command.

This workspace has none of the six expected external inputs: connectome,
retina, relay, graded types, retinal territories, and causal-edge artifact.
Its authoritative result directory is absent. Qualification and authorization
artifacts are also absent. Do not create substitute artifacts to pass gates.

Before authoritative execution, complete the following on the established
RASPUTIN path required by THE WARRANT:

1. Review the full gate and freeze the accepted implementation/test/source
   manifests. Current unit tests do not yet cover every authorized-gate drift
   case; the existence of these tests is not full gate qualification.
2. Bind and validate real input hashes, frozen stimulus, parent provenance,
   runtime image and dependencies. Reproduce the frozen P0 checks under the
   applicable acceptance/execution authority; do not run C13 locally under
   the guise of synthetic qualification.
3. Validate actual durable output creation and authoritative handoff. The
   runner's local atomic no-overwrite publication does not prove a remote
   artifact handoff. Review failed-attempt/retry handling before any run.
4. Seal the complete qualification receipt, then separately authorize neural
   execution with exact bindings. No such authority is supplied by this review.
5. Execute and seal the three arms only after all applicable gates pass.

The runtime source/hash checks and local output checks in the recovered runner
are preparation; they do not themselves establish RASPUTIN image acceptance.
No authoritative THE CORNER neural execution occurred during this review.

## APOTHEOSIS #33 — QUALIFICATION CANNOT OUTRUN EVIDENCE

A test result supports only the behavior and environment actually exercised.
A fake-runtime pass is not a native-runtime proof; a native-runtime test on
synthetic data is not frozen-data acceptance; file presence is not hash
validation; local publication is not durable remote handoff.

Qualify each claim at its own boundary and record what remains untested.
The executable safeguards are the native-runtime contracts and the readiness
status that cannot be mistaken for the runner's accepted qualification status.
This lesson extends #31's write-path requirement without asserting that a
scientific result has been obtained.

Lore: checking the prop gun does not clear the whole crime scene.

## Typed authority gate correction

A later gate audit reproduced eight failing adversarial subcases: the four
permission booleans accepted JSON numbers through Python's `1 == True` and
`0 == False`, both fixed node identities accepted floating-point equivalents,
and two malformed 40-character implementation identities reached the mocked
Git ancestry check. The source correction requires both exact JSON/Python type
and exact value for each frozen authority binding, and requires a full lowercase
hexadecimal commit identity before invoking Git ancestry validation.

The additional standard-library
[`gate contract suite`](../../tests/test_mq5_er6r_the_corner_gate_contract.py)
checks the nominal gate with temporary synthetic input bytes, every frozen
binding, missing authority, qualification drift, missing/extra/changed source
and input manifests, dirty/untracked/non-ancestral Git responses, existing output,
missing output directory, and failed write access. It also exercises actual
native P0 equality for all 192 **synthetic** frames and both native intervention
hooks. Temporary fixture authority files are untracked, removed by the test
harness, and cannot authorize a real scientific input run. Git responses in
gate tests are simulated; container source provenance must be checked separately.

The focused CORNER, WARRANT, and WAY DOWN suite now passes **73 tests** locally,
including 13 new gate/native synthetic tests. Local dependencies were NumPy
2.3.5 and SciPy 1.17.0; this is not acceptance under the RASPUTIN dependency
versions. The new runner hash supersedes the source used by the earlier
non-neural preflight image. Earlier cloud and controller-mediated S3 handoff
acceptance remains historical evidence for that older image and source only.

The next Numancia check tests the corrected pinned source in the older accepted
image's dependency environment using a read-only source mount, no real data
mount, and no container network. That checks software contracts under those
dependencies. It neither builds nor accepts an execution image and must report
`GATE_CONTRACTS_ACCEPTED_NOT_QUALIFIED`. Full executor qualification, real-data
P0 validation under its applicable authority, and separate neural authorization
remain pending. No final qualification or authorization artifact is created.
