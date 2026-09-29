# MQ-5.ER.6R — THE CORNER — Execution-Stage Protocol

Status: **PREREGISTERED STAGE — NEURAL AND RESULT EXECUTION DISABLED**

This stage executes the already frozen [THE WARRANT scientific protocol](mq5-er6r-the-warrant-protocol.md).
Its stage identity is `mq5-er6r-the-corner-v1`; it does not replace THE
WARRANT's experiment identity, endpoint, or classification. The
[pre-outcome closeout](mq5-er6r-the-warrant-control-selection-closeout.md)
froze candidate `1952` and matched control `3056`. No neural execution has
occurred. Historical THE PINCH remains blocked.

## Frozen question

Is transmission from node `1952` necessary for the frozen C13 responder
phenotype in full network context, and is any effect more specific than the
same intervention on structurally matched node `3056`?

The three arms share the same frozen 192-frame C13 stimulus, connectome,
runtime, responder order, and first-positive onset logic:

| Arm | Runtime operation |
|---|---|
| `P0` | Native C13 runtime with no modifier. |
| `P1952` | Compute native `effective_activity`, then set only index `1952` to `0.0` before connectome multiplication. |
| `PCONTROL` | Apply the identical operation at index `3056`. |

The two interventions differ only by node identity. Neither deletes a neuron,
changes an edge, alters the stimulus, overwrites membrane or internal state,
or modifies any other activity index. Output silencing applies on frames
`0..191` inclusive. The proven
[`PhysiologyConstrainedVisualTransductionRuntime` activity modifier](../../brain/physiology_constrained_visual_transduction.py)
is the intended insertion point; implementation must demonstrate that P0
matches the native runtime exactly and that each modifier changes only its
designated activity entry.

## Frozen bindings

- THE WARRANT protocol SHA-256: `20eefc0a830a81a4123a675666db303fe57bce00e0d7691f874f9378d87b6c1b`
- THE WARRANT config SHA-256: `d19905969cb4fb06c776c59ba0c7621bd174dff351bf52b31c23bf136288a135`
- control artifact SHA-256: `b9246b27aafbdd71a52c64864c583d6fb1a6831d19aae0c3e054e0c80154ef19`
- control artifact seal commit: `b3a3d7deaa9c9575cab3cad1022d9ca6d67d11bf`
- corrected WAY DOWN result SHA-256: `3c56719c4bd87f45206c16326779386e22c55955a189d45ae6ca6f5dddb0ffbc`
- C13 stimulus SHA-256: `e8af8077d7d4c13431f7ad3fa05d81e2009263d9a5cb0e7dd800e889ea61ec8a`

All nine responders in frozen order: `51, 55, 92, 129, 317, 656, 1273,
126002, 137122`. The five affected responders are `55, 92, 656, 126002,
137122`; the retained diagnostics are `51, 129, 317, 1273`. These values
must be parsed from the frozen config and compared semantically (Apotheosis
#32), with authoritative input hashes checked against bytes.

## Endpoint and interpretation

For each responder present in P0, dependency under an intervention means a
later first-positive onset or absence within 192 frames. Earlier onset does
not count. The count `k` among the five affected responders yields THE
WARRANT's frozen primary label: `k=5` complete necessity, `k=1..4` partial,
`k=0` necessity not observed. The four retained responders are specificity
diagnostics only. PCONTROL uses the same comparison against P0. Secondary
voltage/activity diagnostics cannot override the primary label.

An effect in P1952 alone supports candidate-specific computational necessity
in this model; effects in both arms weaken specificity; PCONTROL alone argues
against assigning 1952 special necessity; neither is a clean null. No outcome
permits another control, reranking, or replacement candidate. No biological,
cognitive, trading, financial, or real-world behavioral claim is authorized.

## Execution boundary and next gate

This protocol and [stage config](../../config/controls/mq5-er6r-the-corner-v1.toml)
disable neural and result execution. No executor is authorized by their
presence. Before a run: freeze implementation and focused tests; prove P0
equivalence and intervention symmetry; bind source, protocol, config, control,
stimulus, runtime, and data hashes; verify clean committed code, immutable
input access, and durable output/write paths; qualify the implementation;
then freeze a **separate neural-execution authorization**. The previous
control-selection authorization grants none of these actions. Any failed
gate refuses execution without changing scientific state.

Wire lore: WAY DOWN found the suspect; THE WARRANT identified the lookalike;
THE CORNER tests whether taking Bodie or the comparable corner soldier off
the street changes the operation. These names are presentation only.
