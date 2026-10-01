# THE CORNER: output silencing under an inactive-target condition

Reported: 2026-10-01. Experiment: `mq5-er6r-the-warrant-v1`. Execution stage: `mq5-er6r-the-corner-v1`.

**Result:** In one frozen 192-frame C13 episode, silencing candidate node 1952 or matched-control node 3056 left measured responder voltages, spikes, first-positive onsets and positive-voltage fingerprints identical to P0. Both targets produced zero native effective activity at the silencing insertion point throughout the episode. Necessity was not observed under this inactive-target condition; dispensability when active was not tested.

This is a technical results report, not a peer-reviewed paper. The [machine-readable public summary](../../artifacts/mq5-er6r-the-corner-public-results-summary-v1.json) transcribes the retained validation and completion receipts. It is distinct from the sealed raw scientific result.

## Frozen question and methods

The [execution-stage protocol](mq5-er6r-the-corner-execution-protocol.md) implements the already frozen [THE WARRANT protocol](mq5-er6r-the-warrant-protocol.md): is transmission from candidate 1952 necessary for the frozen C13 responder phenotype, and is any effect more specific than the same intervention on structurally matched control 3056? Candidate and control selection preceded the outcome and were not changed afterward.

The [stage config](../../config/controls/mq5-er6r-the-corner-v1.toml) fixes the stimulus, 192-frame window, target identities and endpoint. The three arms used the frozen connectome, stimulus, runtime and responder order:

| Arm | Operation |
| --- | --- |
| P0 | Native C13 runtime with no activity modifier |
| P1952 | Compute native effective activity; zero only index 1952 before connectome multiplication |
| PCONTROL | Identical operation at index 3056 |

The modifier applied on frames 0–191 inclusive. It did not delete a neuron or edge, replace membrane/internal state, alter the stimulus, or zero another index. Each arm used its own runtime instance. The [frozen runner](https://github.com/mayombe67/moscaquant/blob/7b3c74261ba04b09a779d48f30071adc793b7bd3/brain/mq5_er6r_the_corner_runner.py) recorded native target output immediately before silencing.

The primary endpoint counts a dependency when a responder present in P0 has a later first-positive onset or is absent within the 192 frames. Earlier onset does not count. Among five affected responders (55, 92, 656, 126002, 137122), a count of five yields complete necessity, one through four partial necessity, and zero necessity not observed. Four retained responders (51, 129, 317, 1273) are specificity diagnostics. Secondary fingerprints cannot override the primary classification.

## Observations

| Quantity | P1952 versus P0 | PCONTROL versus P0 |
| --- | --- | --- |
| Affected-panel dependencies | 0 of 5 | 0 of 5 |
| Retained-panel dependencies | 0 of 4 | 0 of 4 |
| Frozen primary classification | WARRANT_NECESSITY_NOT_OBSERVED | WARRANT_NECESSITY_NOT_OBSERVED |
| Frames with nonzero native target output | 0 of 192 | 0 of 192 |
| Responder voltage and spike traces | Identical | Identical |
| First-positive onsets and positive fingerprints | Identical | Identical |
| Secondary normalized L2 distance | 0.0 | 0.0 |
| Raw secondary cosine | 1.0000000000000002 | 1.0000000000000002 |

P0 reproduced the frozen onset vector. Both interventions preserved it:

| Responder | First-positive onset frame in all three arms |
| --- | --- |
| 51 | 150 |
| 55 | 145 |
| 92 | 141 |
| 129 | 149 |
| 317 | 156 |
| 656 | 141 |
| 1273 | 149 |
| 126002 | 151 |
| 137122 | 151 |

The successful three-arm job had one attempt and worker exit code 0. Earlier separately authorized failures were retained in operations evidence; this was not the first overall attempt to run the stage. No outcome-driven control replacement or additional scientific rerun is claimed here.

## Interpretation and limitations

The frozen primary classification is unchanged. The engagement diagnostic narrows its interpretation to **NECESSITY_NOT_OBSERVED_UNDER_INACTIVE_TARGET_CONDITION**.

At the modifier insertion point, both selected native outputs were already zero. Consequently, these interventions changed no native target output in the measured episode. An unchanged downstream response cannot establish that an actively transmitting target is dispensable.

Zero effective output at this point does not establish that every internal variable of either neuron was inactive. The result also does not establish biological necessity, behavior, cognition, trading competence, financial performance or recruitment under another condition. Context-dependent recruitment is a possible follow-up hypothesis, not a finding of this experiment.

There is one frozen episode and one successful three-arm execution, without a multi-seed population study or statistical generalization claim. Graph structure and a structurally matched control do not establish physiological engagement.

## Numeric validation and exact exception

Two raw cosine values exceed the strict schema bound of 1.0 by `2.220446049250313e-16`, one representable floating-point step at 1.0. The raw result therefore fails that original strict bound. Its bytes were not rewritten.

A separate validation view sets only `/comparisons/P1952/secondary_fingerprint/cosine` and `/comparisons/PCONTROL/secondary_fingerprint/cosine` to 1.0. That view passes the accepted schema. The retained validation receipt reports that recomputed comparisons from the pinned source match the raw result.

Wil explicitly accepted an exception for this exact artifact and these two values on 2026-10-01. Publication applied a narrowly bound in-memory exception schema after checking the raw result, validation view and decision hashes. This does not generally relax the schema, alter the primary classifications, or conceal the raw-schema failure.

## Evidence and provenance

| Evidence | SHA-256 |
| --- | --- |
| Original result, 299878 bytes | `535a187b45acc01ec4b4d63f41d2835c21cfefdd8e3211fb0043b9022caa62b4` |
| Result seal | `cde1c5964cc3325ddb04e0a5b5f1e1802727775c046f27e5d1db453e506d620b` |
| Execution-output manifest | `bdd327615d59e30015689fb2688fb904a0872d8273818b3ba172e77bc8fe054d` |
| Final handoff receipt | `e01091dda4aeab292eb97c4f1eb6ffb3cb60253267d82f36043f40246d2526a0` |
| Separate normalized validation view | `8221a1b67a5ba4748b90e1819bd00e464eca5022e4328edb7f3a5e3f4a39e61e` |
| Accepted exact numeric decision | `9426f408e010650d8c560bb78e55d34c60461e5ab2d92f8df6f322ad48ff6138` |

Implementation commit: [7b3c742](https://github.com/mayombe67/moscaquant/commit/7b3c74261ba04b09a779d48f30071adc793b7bd3). Image digest: `sha256:d4f8bd8ceb7524f41942542658931ce22f51d5d3e267840e7bf1a955fe6c3de9`.

Qualification hash: `122bad0ccc94e8abf8c15faf720f1aea9da052ec63b880e0e647d75544306c99`. Historical execution-authority hash: `1eb4443487f4e25b37280478772719a7461ee5d6d30b45ae03513684b1fa7e1c`.

The completion receipt reports conditional creation and exact-version byte/checksum readback of the result, seal, manifest and handoff receipt. These observations support artifact integrity; they do not independently validate biological fidelity or make the inactive-target test informative about active-target necessity.

The full result traces and transport evidence remain access-controlled in S3. This public report supplies findings, source links and content hashes, not anonymous access to those files or a complete independently downloadable reproduction bundle. A hash is a content reference, not an access mechanism. Infrastructure policies, live authority objects and operator journals remain in the operations repository.

No new neural execution or independent S3 retrieval was performed to prepare this report. It transcribes the operator-provided validation and handoff evidence. The operational closeout remains [in the private ops repository](https://github.com/mayombe67/moscaquant-ops/blob/raid/the-corner/rasputin/runtime/the-corner/CORNER_CLOSEOUT_2026-10-01.md), accessible only to its authorized readers.

## Historical preregistration and future work

The original protocol/config retain their pre-execution status text and disabled flags because their bytes are frozen scientific bindings. This results report records the later authorized execution without rewriting that historical preregistration or granting a new run.

A follow-up could prospectively define conditions, engagement criteria and controls to ask whether either target produces nonzero output, and only then test necessity under an active condition. Any such study requires its own design and authority. No result is assumed in advance, and neither control reselection nor candidate replacement is authorized by this report.
