# MQ-5.TS.MIX — WARTHOG RUN Implementation Freeze

**Status:** IMPLEMENTATION STAGED FOR REVIEW — NOT EXECUTED

## Scope

This implementation realizes the separately preregistered structural
mixing-depth characterization for MQ-5.TS Arm C.

Narrative label: **WARTHOG RUN**

Narrative banner: **THE MAW IS COLLAPSING. FLOOR IT.**

Both strings are presentation-only. They do not enter any scientific metric or
classification rule.

## Result-bearing boundary

Creating, reviewing, testing or committing this implementation does **not**
execute any frozen mixing-depth seed.

The result-bearing command is exclusively:

`python -m brain.mq5_ts_arm_c_mixing_depth --run-frozen`

That command must not be run until this implementation is reviewed, committed,
pushed, and its source identity accepted.

## Non-result preflight

The only pre-result runner command authorized during implementation review is:

`python -m brain.mq5_ts_arm_c_mixing_depth --preflight-only`

Preflight validates frozen input hashes and the native constructor source
contract. It also runs two exact replays of a tiny synthetic-only graph using a
non-preregistered seed to verify deterministic native behavior.

Preflight performs no MaleCNS/full-connectome topology build, no preregistered
seed build, and no neural execution.

## Production constructor

The runner imports the existing production constructor directly:

`brain.mq5_ts_strict_shuffle_native.build_strict_matched_control_native`

It does not implement a second edge-swap constructor.

The existing scalable verifier is also reused directly.

## Same-seed prefix contract

The preregistration requires shallower same-seed executions to represent
prefixes of the deeper deterministic accepted-swap trajectory.

The implementation audits the frozen native source before execution:

- the deterministic trajectory begins from the frozen seed;
- requested depth controls the accepted-swap stopping target;
- target is forbidden from perturbing RNG state;
- proposal and acceptance behavior remain the production implementation.

The source audit additionally fails if `target` is used anywhere in the
frozen native function other than input validation, termination, or the final
target-reached check.

A future backend change that violates these source-contract markers fails
preflight closed and requires a new reviewed implementation.


## Result-execution authorization gate

`--run-frozen` is fail-closed until a separate tracked authorization file
exists at:

`config/controls/mq5-ts-arm-c-mixing-depth-execution-authorization-v1.json`

That future gate is created only after:

1. this implementation is reviewed and committed;
2. the implementation commit is pushed;
3. expected WARTHOG RUN RAM/runtime/I/O load is assessed;
4. Habitat vs. RASPUTIN is selected prospectively.

The authorization binds:

- implementation commit;
- runner SHA-256;
- frozen config SHA-256;
- production native backend SHA-256;
- scalable verifier SHA-256;
- execution mode (`local` or `rasputin`).

Result execution additionally requires a clean Git tree and tracked scientific
files. The authorized implementation commit must remain an ancestor of the
execution HEAD.

If a final result artifact already exists, `--run-frozen` refuses **before**
constructing any topology.

RASPUTIN is therefore not implicitly recruited by this implementation. Its use,
if warranted by the load assessment, requires explicit authorization.

## Memory-conscious analysis

The runner does not create Python sets containing tens of millions of edges.

Exact directed-edge intersections are calculated from CSR structure. The three
`4.0x` deep-reference column-index arrays live only in a temporary directory
and are memory-mapped for cross-seed comparisons.

No shuffled full-connectome is promoted as the scientific result.

The final result is a JSON record containing provenance, build diagnostics,
invariant reports, structural metrics and the preregistered classification.

## Build order

The implementation constructs all three `4.0x` deep references first, then the
`0.5x`, `1.0x`, and `2.0x` checkpoints.

This ordering exists only to permit memory-conscious cross-seed analysis. It
does not alter the frozen 12-build design or the classification rule.

There is no outcome-dependent early stopping.

## Scientific boundaries

The runner executes no neural dynamics, responder metrics, voltage/onset
metrics, market metrics, trading metrics, or profitability metrics.

It does not reopen the accepted MQ-5.TS result.

It refuses to overwrite an existing final mixing-depth result artifact.

## Review rule

This implementation must be reviewed as actual file content before commit.
Commit does not itself authorize execution. Push remains a separate manual
action.
