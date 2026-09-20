# SQ-03C — CHECK THE RECEIPTS — Results

**Status:** COMPLETE  
**Classification:** Authoritative scalar verification result  
**Source commit:** `249e83e4f32241e67077494e0f908afdbffef37f`  
**Artifact SHA-256:** `4728c197addeadac8eae2af363c9abe9093fdee00dee6b632ff2324b0f70328a`

## Result

SQ-03C reran the frozen SQ-03B verification panel one job at a time through the
original scalar `HybridRuntime`.

- selected jobs: **148**
- upper-tail verification jobs: **84**
- low-tail controls: **64**
- deterministic A/A replay: **PASS**
- all metrics agree with SQ-03B: **PASS**
- upper-tail agreement: **84/84**
- low-tail agreement: **64/64**

The scalar execution reproduced the SQ-03B batched results for every selected
upper-tail job and every selected low-tail control under the already-frozen
numerical agreement contract.

## Interpretation

SQ-03C confirms that the selected SQ-03B upper-tail localization effects are
not artifacts of the batched counterfactual execution path.

The low-tail controls also reproduced under scalar execution, supporting the
observed separation between extremely small effects and the stronger upper tail
inside this frozen computational model.

This is a **computational replication across execution paths**, not an
independent biological replication and not a population-level statistical test.

SQ-03C does not establish:

- a biological mechanism in living flies;
- formal population-level statistical significance;
- general male/female behavioral differences;
- sex superiority;
- intelligence differences;
- market skill;
- profitability;
- financial usefulness.

No post-hoc SQ-03B tolerance is promoted to a significance threshold.

## Claim boundary

SQ-03C is a confirmatory computational verification of a frozen subset of SQ-03B localization jobs. It tests whether upper-tail and low-tail effects reproduce under the original scalar HybridRuntime. It does not establish a biological mechanism, formal population-level statistical significance, general sex differences, behavior, intelligence, or financial utility.
